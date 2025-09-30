# app.py

import sys
import logging
from PyQt5.QtWidgets import QApplication

from GUI.login_window import LoginWindow
from GUI.admin_window import AdminWindow
from GUI.standard_user_window import UserWindow

logger = logging.getLogger(__name__)


class AppController:
    def __init__(self, db_manager, xlsx_manager):
        self.app = QApplication(sys.argv)
        self.db_manager = db_manager
        self.xlsx_manager = xlsx_manager
        self.current_window = None
        self.current_user = None  # Store user info (user_id, username, role)
        
        logger.info("AppController initialized with backend managers")
        self.show_login()

    def show_login(self):
        self.current_window = LoginWindow(self.handle_login_success, self.db_manager)
        self.current_window.show()
        logger.info("Login window displayed")

    def handle_login_success(self, user_data):
        """
        user_data is a tuple: (user_id, username, role)
        """
        self.current_user = user_data
        user_id, username, role = user_data
        
        logger.info(f"User {username} (ID: {user_id}) logged in as {role}")
        
        self.current_window.close()

        if role == "admin":
            self.current_window = AdminWindow(
                username=username,
                user_id=user_id,
                db_manager=self.db_manager,
                xlsx_manager=self.xlsx_manager,
                on_logout=self.show_login
            )
        else:
            self.current_window = UserWindow(
                username=username,
                user_id=user_id,
                db_manager=self.db_manager,
                xlsx_manager=self.xlsx_manager,
                on_logout=self.show_login
            )

        self.current_window.show()
        logger.info(f"{role.capitalize()} window displayed for {username}")

    def run(self):
        logger.info("Starting application event loop")
        sys.exit(self.app.exec_())


if __name__ == "__main__":
    # This allows the module to be run standalone for testing
    from managers.db_manager import DatabaseManager
    from managers.xlsx_manager import XLSXManager
    from utils.logger import setup_logging
    
    setup_logging()
    db = DatabaseManager()
    xlsx = XLSXManager(db)
    controller = AppController(db, xlsx)
    controller.run()