#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Scan history management module for AccessChk GUI.

This module provides the ScanHistoryManager class for tracking and
persisting scan history to disk.

Classes:
    ScanHistoryManager: Manages scan history storage and retrieval
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Dict
from pathlib import Path

__all__ = ['ScanHistoryManager']

logger = logging.getLogger(__name__)


class ScanHistoryManager:
    """Manager for scan history persistence.
    
    Maintains a JSON-based history of recent scans with automatic
    size limiting and graceful error handling.
    
    Attributes:
        storage_dir: Directory for storing history file
        history_file: Full path to scan_history.json
        max_history: Maximum number of history entries (default: 20)
        
    Example:
        >>> history_mgr = ScanHistoryManager("./data")
        >>> history_mgr.add_scan("full", ["C:\\"], "Users", 42)
        >>> entries = history_mgr.get_history()
        >>> print(f"Found {len(entries)} previous scans")
        >>> history_mgr.clear_history()
    """
    
    def __init__(self, storage_dir: str):
        """Initialize history manager with storage directory.
        
        Args:
            storage_dir: Directory path for storing history file
                        (will be created if it doesn't exist)
                        
        Example:
            >>> mgr = ScanHistoryManager("./data")
            >>> mgr = ScanHistoryManager(os.path.expanduser("~/.accesschk"))
        """
        self.storage_dir = storage_dir
        self.history_file = os.path.join(storage_dir, "scan_history.json")
        self.max_history = 20  # Maximum number of history entries
        
        # Create storage directory if it doesn't exist
        try:
            os.makedirs(storage_dir, exist_ok=True)
        except (OSError, PermissionError) as e:
            logger.warning(f"Could not create storage directory {storage_dir}: {e}")
    
    def add_scan(self, scan_type: str, targets: List[str], principal: str, result_count: int) -> None:
        """Add a scan to history.
        
        Adds a new scan entry to the beginning of the history list.
        Automatically limits history size to max_history entries.
        
        Args:
            scan_type: Type of scan (e.g., "full", "quick", "custom")
            targets: List of scanned target paths
            principal: User or group principal that was checked
            result_count: Number of results found
            
        Example:
            >>> mgr.add_scan(
            ...     scan_type="full",
            ...     targets=["C:\\Windows", "C:\\Program Files"],
            ...     principal="Users",
            ...     result_count=42
            ... )
        """
        try:
            history = self._load_history()
            
            entry = {
                "timestamp": datetime.now().isoformat(),
                "scan_type": scan_type,
                "targets": targets,
                "principal": principal,
                "result_count": result_count
            }
            
            history.insert(0, entry)  # Add to beginning (most recent first)
            
            # Limit history size
            if len(history) > self.max_history:
                history = history[:self.max_history]
            
            self._save_history(history)
            logger.info(f"Added scan to history: {scan_type} scan of {len(targets)} targets")
            
        except Exception as e:
            logger.warning(f"Could not save scan to history: {e}")
    
    def get_history(self) -> List[Dict]:
        """Retrieve scan history.
        
        Returns the full scan history list, with most recent scans first.
        
        Returns:
            List[Dict]: List of scan history entries, each containing:
                - timestamp: ISO format timestamp
                - scan_type: Type of scan
                - targets: List of target paths
                - principal: User/group checked
                - result_count: Number of results
                
        Example:
            >>> history = mgr.get_history()
            >>> for entry in history:
            ...     print(f"{entry['timestamp']}: {entry['scan_type']} scan")
            ...     print(f"  Targets: {', '.join(entry['targets'])}")
            ...     print(f"  Results: {entry['result_count']}")
        """
        return self._load_history()
    
    def clear_history(self) -> None:
        """Clear all scan history.
        
        Deletes the history file, removing all stored scan records.
        Safe to call even if history file doesn't exist.
        
        Example:
            >>> mgr.clear_history()  # Removes all history entries
        """
        try:
            if os.path.exists(self.history_file):
                os.remove(self.history_file)
                logger.info("Scan history cleared")
        except (OSError, PermissionError) as e:
            logger.warning(f"Could not clear history file: {e}")
    
    def _load_history(self) -> List[Dict]:
        """Load history from JSON file.
        
        Internal method to read history from disk. Returns empty list
        if file doesn't exist or cannot be read.
        
        Returns:
            List[Dict]: Loaded history entries, or empty list on error
        """
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return data
                    logger.warning(f"Invalid history format in {self.history_file}")
        except (IOError, OSError, json.JSONDecodeError) as e:
            logger.debug(f"Error loading history: {e}")
        return []
    
    def _save_history(self, history: List[Dict]) -> None:
        """Save history to JSON file.
        
        Internal method to persist history to disk with pretty formatting.
        
        Args:
            history: List of history entries to save
            
        Raises:
            IOError: If file cannot be written (logged, not raised)
        """
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
        except (IOError, OSError, json.JSONEncodeError) as e:
            logger.warning(f"Error saving history: {e}")
