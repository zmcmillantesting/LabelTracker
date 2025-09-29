# app.py

import sys
from PyQt5.QtWidgets import QApplication

from login_window import LoginWindow
from admin_window import AdminWindow
from standard_user_window import UserWindow


class AppController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.current_window = None
        self.show_login()

    def show_login(self):
        self.current_window = LoginWindow(self.handle_login_success)
        self.current_window.show()

    def handle_login_success(self, role: str, username: str):
        self.current_window.close()

        if role == "admin":
            self.current_window = AdminWindow(username)
        else:
            self.current_window = UserWindow(username)

        self.current_window.show()

    def run(self):
        sys.exit(self.app.exec_())


if __name__ == "__main__":
    controller = AppController()
    controller.run()