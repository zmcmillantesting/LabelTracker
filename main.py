# main.py

import sys
import os

# Add project root to Python path for imports
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from utils.logger import setup_logging
from managers.db_manager import DatabaseManager
from managers.xlsx_manager import XLSXManager
from GUI.app import AppController

def main():
    # Setup logging
    logger = setup_logging()
    logger.info("Starting Label Tracker Application...")
    
    try:
        # Initialize database manager
        db_manager = DatabaseManager()
        logger.info("Database manager initialized")
        
        # Initialize XLSX manager
        xlsx_manager = XLSXManager(db_manager)
        logger.info("XLSX manager initialized")
        
        # Start the application with managers
        controller = AppController(db_manager, xlsx_manager)
        logger.info("Application controller started")
        
        controller.run()
        
    except Exception as e:
        logger.error(f"Application failed to start: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()