#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""AccessChk GUI Application Launcher.

This is the main entry point for the AccessChk GUI application.
It sets up logging, imports the GUI class, and starts the Tkinter mainloop.

Usage:
    python AccessChkGUI.py

Requirements:
    - Python 3.10+
    - Tkinter (bundled with Python on Windows)
    - accesschk.exe from Microsoft Sysinternals (in tools/ directory)

Author: AccessChk GUI Development Team
Version: 1.10
"""

import sys
import os
import logging
from pathlib import Path

# Add project root to Python path if needed
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            project_root / 'accesschk_gui.log',
            mode='a',
            encoding='utf-8'
        )
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main application entry point."""
    try:
        logger.info("Starting AccessChk GUI v1.10")
        logger.info(f"Project root: {project_root}")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Platform: {sys.platform}")
        
        # Check elevation BEFORE creating UI (critical security check)
        from src.validation import is_running_elevated
        if is_running_elevated():
            logger.error("Application launched with elevated privileges - DENIED")
            print("ERREUR: Cette application doit être lancée avec un utilisateur standard.")
            print("Ne PAS exécuter en tant qu'administrateur.")
            input("Appuyez sur Entrée pour quitter...")
            sys.exit(1)
        
        # Import GUI class
        from src.gui import AccessChkGUI
        
        # Create and run application
        app = AccessChkGUI()
        logger.info("AccessChk GUI initialized successfully")
        
        # Start Tkinter event loop
        app.mainloop()
        
        logger.info("AccessChk GUI closed")
        
    except ImportError as e:
        logger.error(f"Import error: {e}", exc_info=True)
        print(f"ERROR: Could not import required modules: {e}")
        print("Make sure all dependencies are installed and the src/ directory exists.")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"ERROR: An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
