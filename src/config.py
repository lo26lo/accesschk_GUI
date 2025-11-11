#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Application configuration and constants.

This module contains all configuration constants for the AccessChk GUI application,
including performance settings, UI dimensions, file paths, and security constraints.
"""

__all__ = ["AppConfig"]


class AppConfig:
    """Configuration centralisée de l'application.
    
    This class acts as a singleton for application-wide configuration.
    All constants are defined as class attributes for easy access.
    
    Attributes:
        BATCH_SIZE: Number of lines to process in each batch
        BATCH_TIMEOUT_MS: Timeout for batch processing in milliseconds
        UI_UPDATE_INTERVAL_MS: Interval for UI updates in milliseconds
        MAX_DISPLAYED_LINES: Maximum number of lines to display in GUI
        WINDOW_WIDTH: Default window width in pixels
        WINDOW_HEIGHT: Default window height in pixels
        MIN_WIDTH: Minimum window width in pixels
        MIN_HEIGHT: Minimum window height in pixels
        EXPORT_DEFAULT: Default filename for filtered exports
        DIFF_EXPORT_DEFAULT: Default filename for diff exports
        LOG_FILE: Name of the log file
        HISTORY_FILE: Name of the history file
        MAX_HISTORY_ENTRIES: Maximum number of history entries to keep
        MAX_PATH_LENGTH: Maximum path length (Windows limit)
        ALLOWED_EXTENSIONS: Set of allowed executable extensions
        DANGEROUS_CHARS: List of dangerous characters for validation
        PROGRESS_BAR_SPEED: Speed of progress bar animation
        SCAN_TIMEOUT_SECONDS: Timeout for scan operations
    """
    
    # Performance
    BATCH_SIZE = 50
    BATCH_TIMEOUT_MS = 25
    UI_UPDATE_INTERVAL_MS = 50
    MAX_DISPLAYED_LINES = 3000
    
    # UI
    WINDOW_WIDTH = 1100
    WINDOW_HEIGHT = 800
    MIN_WIDTH = 880
    MIN_HEIGHT = 620
    
    # Fichiers
    EXPORT_DEFAULT = "accesschk_filtered_logs.txt"
    DIFF_EXPORT_DEFAULT = "accesschk_diff.txt"
    LOG_FILE = "accesschk_gui.log"
    HISTORY_FILE = "scan_history.json"
    
    # History
    MAX_HISTORY_ENTRIES = 100
    
    # Sécurité
    MAX_PATH_LENGTH = 260
    ALLOWED_EXTENSIONS = {'.exe'}
    DANGEROUS_CHARS = ['&', '|', ';', '$', '`', '<', '>']
    
    # AccessChk
    PROGRESS_BAR_SPEED = 30
    SCAN_TIMEOUT_SECONDS = 300
    
    # Singleton pattern
    _instance = None
    
    def __new__(cls):
        """Ensure only one instance exists (Singleton pattern)."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
