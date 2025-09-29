# login_window.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QMessageBox
from widgets import create_label, create_input, create_button
import styles


class LoginWindow(QWidget):
    def __init__(self, on_login_success):
        super().__init__()

        self.setWindowTitle("Label Tracker - Login")
        self.setStyleSheet(styles.WINDOW_STYLE)
        self.on_login_success = on_login_success  # callback after login
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.username_label = create_label("Username:")
        self.username_input = create_input("Enter username")

        self.password_label = create_label("Password:")
        self.password_input = create_input("Enter password")
        self.password_input.setEchoMode(self.password_input.Password)

        self.login_button = create_button("Login")
        self.login_button.clicked.connect(self.handle_login)

        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Login Failed", "Please enter both username and password.")
            return

        # 🔧 Placeholder for backend authentication
        # Simulate user roles: 'admin' vs 'user'
        #TODO: update link to db for authentication
        if username == "admin" and password == "admin123":
            self.on_login_success("admin", username)
        elif username == "user" and password == "user123":
            self.on_login_success("user", username)
        else:
            QMessageBox.critical(self, "Login Failed", "Invalid credentials.")