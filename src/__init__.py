"""AccessChk GUI - Windows Permissions Scanner.

This package provides a graphical interface for the Sysinternals accesschk.exe tool,
enabling easy scanning and analysis of Windows file system permissions.

Modules:
    config: Application configuration and constants
    validation: Input validation and security functions
    utils: Utility functions for encoding, paths, etc.
    scanner: AccessChk execution logic
    export: Multi-format export functionality
    history: Scan history management
    gui: Tkinter graphical user interface
"""

__version__ = "2.0.0"
__author__ = "AccessChk GUI Team"
__all__ = [
    "config",
    "validation",
    "utils",
    "scanner",
    "export",
    "history",
    "gui",
]
