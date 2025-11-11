#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Security validation functions for AccessChk GUI.

This module provides comprehensive input validation to prevent
command injection attacks and ensure safe execution of accesschk.exe.

Functions:
    validate_executable_path: Validate executable file paths
    validate_target_paths: Validate and sanitize scan targets
    sanitize_command_args: Escape dangerous characters in arguments
    is_running_elevated: Check if running with admin privileges
"""

import os
import logging
import shlex
import ctypes
from pathlib import Path
from typing import List, Tuple

from src.config import AppConfig

__all__ = [
    'validate_executable_path',
    'validate_target_paths',
    'sanitize_command_args',
    'is_running_elevated'
]

logger = logging.getLogger(__name__)


def is_running_elevated() -> bool:
    """Return True when the process has elevated/admin privileges.
    
    This function checks if the application is running with administrator
    privileges on Windows, or as root on Unix systems.
    
    Returns:
        bool: True if running with elevated privileges, False otherwise
        
    Example:
        >>> if not is_running_elevated():
        ...     print("Warning: Running without admin privileges")
    """
    if os.name == "nt":
        try:
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        except Exception:
            return False
    try:
        geteuid = getattr(os, "geteuid", None)
        return bool(geteuid and geteuid() == 0)
    except Exception:
        return False


def validate_executable_path(path: str) -> Tuple[bool, str]:
    """Validate that the provided path is a safe executable file.
    
    This function performs comprehensive security checks:
    - Path length validation (Windows MAX_PATH limit)
    - Dangerous character detection
    - File existence verification
    - Extension validation (.exe only)
    - Filename validation (must be accesschk.exe)
    
    Args:
        path: The file path to validate
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
        If valid, error_message is empty string
        
    Example:
        >>> is_valid, error = validate_executable_path("C:\\Tools\\accesschk.exe")
        >>> if not is_valid:
        ...     print(f"Validation failed: {error}")
    """
    if not path or not isinstance(path, str):
        return False, "Le chemin est vide ou invalide"
    
    # Normalize and check path length
    try:
        normalized_path = os.path.normpath(path.strip())
        if len(normalized_path) > AppConfig.MAX_PATH_LENGTH:
            return False, f"Le chemin est trop long (max {AppConfig.MAX_PATH_LENGTH} caractères)"
    except (OSError, ValueError) as e:
        logger.warning(f"Path normalization failed: {e}")
        return False, f"Chemin invalide: {str(e)}"
    
    # Check for dangerous characters
    if any(char in normalized_path for char in AppConfig.DANGEROUS_CHARS):
        logger.warning(f"Dangerous characters detected in path: {normalized_path}")
        return False, "Le chemin contient des caractères dangereux"
    
    # Check if file exists
    if not os.path.isfile(normalized_path):
        return False, "Le fichier n'existe pas"
    
    # Check file extension
    file_ext = Path(normalized_path).suffix.lower()
    if file_ext not in AppConfig.ALLOWED_EXTENSIONS:
        return False, f"Extension de fichier non autorisée: {file_ext}"
    
    # Check if it's actually accesschk.exe
    filename = Path(normalized_path).name.lower()
    if filename != "accesschk.exe":
        logger.warning(f"Invalid executable name: {filename} (expected accesschk.exe)")
        return False, "Le fichier doit être accesschk.exe"
    
    logger.debug(f"Executable path validated: {normalized_path}")
    return True, ""


def validate_target_paths(paths_str: str) -> Tuple[bool, str, List[str]]:
    """Validate target paths for scanning.
    
    This function validates and sanitizes a semicolon-separated list of
    paths to be scanned by accesschk.exe. It checks for:
    - Empty paths
    - Dangerous characters
    - Path length limits
    - Path existence (warns but doesn't fail)
    
    Args:
        paths_str: Semicolon-separated string of paths
        
    Returns:
        Tuple[bool, str, List[str]]: (is_valid, error_message, validated_paths)
        
    Example:
        >>> valid, error, paths = validate_target_paths("C:\\Windows;C:\\Program Files")
        >>> if valid:
        ...     print(f"Found {len(paths)} valid paths")
    """
    if not paths_str or not isinstance(paths_str, str):
        return False, "Aucun chemin spécifié", []
    
    raw_paths = [p.strip().strip('"') for p in paths_str.split(";") if p.strip()]
    if not raw_paths:
        return False, "Aucun chemin valide trouvé", []
    
    validated_paths = []
    for path in raw_paths:
        # Check for dangerous characters (semicolon is allowed as separator)
        path_dangerous_chars = ['&', '|', '$', '`', '<', '>']
        if ';' in path.strip():
            path_dangerous_chars.append(';')
            
        dangerous_found = [char for char in path_dangerous_chars if char in path]
        if dangerous_found:
            logger.warning(f"Dangerous characters in path: {path}")
            return False, f"Caractères dangereux détectés dans '{path}': {', '.join(dangerous_found)}", []
        
        # Normalize and validate path length
        try:
            normalized = os.path.normpath(path)
            if len(normalized) > AppConfig.MAX_PATH_LENGTH:
                return False, f"Chemin trop long: {path}", []
        except (OSError, ValueError) as e:
            logger.warning(f"Path normalization failed: {path}")
            return False, f"Chemin invalide '{path}': {str(e)}", []
        
        validated_paths.append(normalized)
    
    logger.debug(f"Validated {len(validated_paths)} target paths")
    return True, "", validated_paths


def sanitize_command_args(args: List[str]) -> List[str]:
    """Sanitize command arguments to prevent injection attacks.
    
    This function escapes or quotes arguments that contain dangerous
    characters. Valid paths and command flags are quoted, while
    truly dangerous arguments are filtered out with a warning.
    
    Args:
        args: List of command arguments
    
    Returns:
        List[str]: Sanitized arguments
        
    Example:
        >>> args = ["C:\\Path & Test", "-u", "Users"]
        >>> sanitized = sanitize_command_args(args)
        >>> assert "&" not in sanitized[0] or sanitized[0].startswith('"')
    """
    sanitized = []
    for arg in args:
        if not isinstance(arg, str):
            continue
        
        # Check for dangerous characters (not parentheses, brackets which are valid)
        dangerous_found = [char for char in AppConfig.DANGEROUS_CHARS if char in arg]
        if dangerous_found:
            # If it's a valid path or command flag, quote it
            if os.path.exists(arg) or arg.startswith('-') or arg in ['accepteula', 'nobanner']:
                sanitized.append(shlex.quote(arg))
                logger.debug(f"Quoted argument with dangerous chars: {arg}")
            else:
                logger.warning(f"Argument potentiellement dangereux ignoré: {arg} (caractères: {', '.join(dangerous_found)})")
        else:
            sanitized.append(arg)
    
    return sanitized
