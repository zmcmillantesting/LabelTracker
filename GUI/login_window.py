# login_window.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QMessageBox, QLineEdit
from GUI.widgets import create_label, create_input, create_button
import GUI.styles as styles


class LoginWindow(QWidget):
    def __init__(self, on_login_success, db_manager=None):
        super().__init__()

        self.setWindowTitle("Label Tracker - Login")
        self.setStyleSheet(styles.WINDOW_STYLE)
        self.on_login_success = on_login_success  # callback after login
        self.db_manager = db_manager
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.username_label = create_label("Username:")
        self.username_input = create_input("Enter username")

        self.password_label = create_label("Password:")
        self.password_input = create_input("Enter password")
        # Use QLineEdit.Password enum for echo mode
        self.password_input.setEchoMode(QLineEdit.Password)

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
        # If a db_manager is provided, attempt real authentication
        if self.db_manager:
            try:
                user = self.db_manager.authenticate_user(username, password)
                if user:
                    # db returns (user_id, username, role)
                    self.on_login_success(user)
                else:
                    QMessageBox.critical(self, "Login Failed", "Invalid credentials.")
            except Exception as e:
                QMessageBox.critical(self, "Login Failed", f"Authentication error:\n{e}")
            return

        # Fallback stub authentication for local testing
        if username == "admin" and password == "admin123":
            # (user_id, username, role)
            self.on_login_success((1, "admin", "admin"))
        elif username == "user" and password == "user123":
            self.on_login_success((2, "user", "user"))
        else:
            QMessageBox.critical(self, "Login Failed", "Invalid credentials.")