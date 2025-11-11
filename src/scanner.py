#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""AccessChk scanner execution module.

This module provides the AccessChkRunner class responsible for executing
accesschk.exe scans in a separate thread, processing output, and managing
the scan lifecycle.

Classes:
    AccessChkRunner: Main scanner class that runs accesschk.exe and processes output
"""

import os
import queue
import subprocess
import threading
import time
import logging
from typing import List, Optional

from src.config import AppConfig
from src.validation import sanitize_command_args
from src.utils import (
    decode_bytes_with_fallback,
    matches_suppressed_error,
    WRITE_REGEX
)

__all__ = ['AccessChkRunner']

logger = logging.getLogger(__name__)


class AccessChkRunner:
    """Class responsible for executing AccessChk scans.
    
    This class manages the lifecycle of an accesschk.exe scan process:
    - Starts scan in a separate thread
    - Processes stdout/stderr output
    - Handles multiple target paths and principals
    - Manages process termination
    
    Attributes:
        config: Application configuration
        queue: Thread-safe queue for output messages
        current_process: Active subprocess.Popen instance
        is_running: Flag indicating if a scan is in progress
        
    Example:
        >>> runner = AccessChkRunner(config, output_queue)
        >>> runner.start_scan("tools/accesschk.exe", ["C:\\"], "Users")
        >>> # ... later ...
        >>> runner.stop_scan()
    """
    
    def __init__(self, config: AppConfig, queue_handler: queue.Queue):
        """Initialize scanner with configuration and output queue.
        
        Args:
            config: Application configuration instance
            queue_handler: Queue for sending output messages to GUI
        """
        self.config = config
        self.queue = queue_handler
        self.current_process: Optional[subprocess.Popen] = None
        self.is_running = False
    
    def start_scan(self, accesschk_path: str, targets: List[str], principal: str) -> None:
        """Start an AccessChk scan in a separate thread.
        
        Creates a daemon thread to run the scan without blocking the GUI.
        Only one scan can run at a time.
        
        Args:
            accesschk_path: Path to accesschk.exe executable
            targets: List of target paths to scan
            principal: User or group principal to check (e.g., "Users")
            
        Raises:
            RuntimeError: If a scan is already running
            
        Example:
            >>> runner.start_scan(
            ...     "tools/accesschk.exe",
            ...     ["C:\\Windows", "C:\\Program Files"],
            ...     "Users"
            ... )
        """
        if self.is_running:
            raise RuntimeError("Un scan est déjà en cours")
        
        self.is_running = True
        thread = threading.Thread(
            target=self._run_scan,
            args=(accesschk_path, targets, principal),
            daemon=True,
            name="AccessChkRunner"
        )
        thread.start()
    
    def stop_scan(self) -> None:
        """Stop the currently running scan.
        
        Terminates the active subprocess and cleans up state.
        Safe to call even if no scan is running.
        
        Example:
            >>> runner.stop_scan()  # Immediately terminates scan
        """
        try:
            if self.current_process and self.current_process.poll() is None:
                self.current_process.kill()
                logger.info("Scan arrêté par l'utilisateur")
        except (OSError, subprocess.SubprocessError) as e:
            logger.warning(f"Erreur lors de l'arrêt du scan: {e}")
        finally:
            self.is_running = False
            self.current_process = None
    
    def _run_scan(self, accesschk_path: str, targets: List[str], principal: str) -> None:
        """Main scan execution logic (runs in thread).
        
        Iterates through all targets and principals, launching accesschk.exe
        for each combination. Uses universal SID for principals.
        
        Args:
            accesschk_path: Path to accesschk.exe
            targets: List of target paths
            principal: Primary principal to check (defaults to S-1-5-32-545)
            
        Notes:
            - Default principal: S-1-5-32-545 (universal BUILTIN\\Users SID)
            - All output sent via self.queue for thread-safe communication
        """
        try:
            # Use universal SID for Users group (works on all Windows locales)
            effective_principal = principal if principal else "S-1-5-32-545"
            
            for target in targets:
                if not self.is_running:  # Check for early stop
                    break
                
                # Build secure command arguments
                base_args = [accesschk_path, "-accepteula", "-nobanner", 
                            effective_principal, "-w", "-s", target]
                args = sanitize_command_args(base_args)
                
                self.queue.put({"_status": f"Scan de {target} — {effective_principal}"})
                
                try:
                    self.current_process = self._create_process(args)
                    last_rc = self._process_output(self.current_process, effective_principal)
                    
                except (FileNotFoundError, OSError, subprocess.SubprocessError) as e:
                    error_msg = f"[ERREUR] Impossible de lancer accesschk.exe: {e}"
                    logger.error(error_msg)
                    self.queue.put({"line": error_msg, "write": False, "err": True})
                    self.queue.put({"_finished": True, "returncode": -1})
                    return
            
            self.queue.put({"_finished": True, "returncode": last_rc})
            
        except Exception as ex:
            error_msg = f"[EXCEPTION] Erreur inattendue dans le scan: {ex}"
            logger.exception(error_msg)
            self.queue.put({"line": error_msg, "write": False, "err": True})
            self.queue.put({"_finished": True, "returncode": -1})
        finally:
            self.is_running = False
            self.current_process = None
    
    def _create_process(self, args: List[str]) -> subprocess.Popen:
        """Create a subprocess.Popen instance for AccessChk.
        
        Configures Windows-specific flags to hide the console window.
        
        Args:
            args: Command-line arguments (sanitized)
            
        Returns:
            subprocess.Popen: Running process instance
            
        Raises:
            FileNotFoundError: If accesschk.exe not found
            OSError: If process creation fails
        """
        startupinfo = None
        creationflags = 0
        
        if os.name == "nt":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= getattr(subprocess, "STARTF_USESHOWWINDOW", 0)
            creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

        return subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            startupinfo=startupinfo,
            creationflags=creationflags,
        )
    
    def _process_output(self, proc: subprocess.Popen, who: str) -> int:
        """Process AccessChk stdout/stderr output.
        
        Spawns two reader threads (stdout, stderr) to process output
        line-by-line. Filters out suppressed errors and detects write permissions.
        
        Args:
            proc: Running subprocess instance
            who: Current principal being checked
            
        Returns:
            int: Process return code
            
        Notes:
            - Write permission detection via WRITE_REGEX
            - Queue throttling if backlog exceeds 500 items
        """
        
        def reader(stream, is_err=False):
            """Read an AccessChk stream and push lines to queue.
            
            Args:
                stream: File object (stdout or stderr)
                is_err: True if reading stderr
            """
            try:
                while True:
                    chunk = stream.readline()
                    if not chunk: 
                        break
                    
                    s = decode_bytes_with_fallback(chunk).rstrip("\r\n")
                    
                    # Skip suppressed errors
                    if matches_suppressed_error(s):
                        continue
                    
                    if is_err and "Invalid account name" in s: 
                        invalid = True
                    
                    # Determine if line has write permissions
                    has_write = bool(WRITE_REGEX.search(s)) if not is_err else False
                    
                    # Throttle if queue is getting too full
                    if self.queue.qsize() > 500:
                        time.sleep(0.001)
                    
                    self.queue.put({"line": s, "write": has_write, "err": is_err})
            except (UnicodeError, IOError) as e:
                logger.warning(f"Erreur lors de la lecture du flux: {e}")
        
        # Spawn reader threads for stdout/stderr
        t1 = threading.Thread(target=reader, args=(proc.stdout, False), daemon=True, name="StdoutReader")
        t2 = threading.Thread(target=reader, args=(proc.stderr, True), daemon=True, name="StderrReader")
        
        t1.start()
        t2.start()
        
        try:
            proc.wait()
        except KeyboardInterrupt:
            logger.info("Interruption du scan par l'utilisateur")
            proc.kill()
            return -1
        
        # Wait for reader threads to finish
        t1.join(timeout=2)
        t2.join(timeout=2)
        
        return proc.returncode
