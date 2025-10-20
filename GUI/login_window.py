from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QMessageBox, QLineEdit, QHBoxLayout, QPushButton
)
from GUI.widgets import create_label, create_input, create_button
import GUI.styles as styles
from PyQt5.QtCore import Qt


class LoginWindow(QWidget):
    def __init__(self, on_login_success, db_manager=None):
        super().__init__()

        self.setWindowTitle("Label Tracker - Login")
        self.setStyleSheet(styles.WINDOW_STYLE)
        self.on_login_success = on_login_success
        self.db_manager = db_manager
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # --- Username field ---
        self.username_label = create_label("Username:")
        self.username_input = create_input("Enter username")

        # --- Password field with eye button ---
        self.password_label = create_label("Password:")

        # Create a container layout so we can put the eye button next to the input
        pw_layout = QHBoxLayout()
        self.password_input = create_input("Enter password")
        self.password_input.setEchoMode(QLineEdit.Password)

        # 👁️ Button to show/hide password
        self.toggle_pw_button = QPushButton("👁️")
        self.toggle_pw_button.setCheckable(True)
        self.toggle_pw_button.setFixedWidth(40)
        self.toggle_pw_button.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
                font-size: 16px;
            }
            QPushButton:hover {
                color: #0078d4;
            }
        """)
        self.toggle_pw_button.clicked.connect(self.toggle_password_visibility)

        # Add to layout
        pw_layout.addWidget(self.password_input)
        pw_layout.addWidget(self.toggle_pw_button)

        # --- Login button ---
        self.login_button = create_button("Login")
        self.login_button.clicked.connect(self.handle_login)

        # --- Add widgets to main layout ---
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addLayout(pw_layout)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def toggle_password_visibility(self):
        """Toggle password visibility when the eye button is clicked."""
        if self.toggle_pw_button.isChecked():
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.toggle_pw_button.setText("🙈")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.toggle_pw_button.setText("👁️")

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Login Failed", "Please enter both username and password.")
            return

        if self.db_manager:
            try:
                user = self.db_manager.authenticate_user(username, password)
                if user:
                    self.on_login_success(user)
                else:
                    QMessageBox.critical(self, "Login Failed", "Invalid credentials.")
            except Exception as e:
                QMessageBox.critical(self, "Login Failed", f"Authentication error:\n{e}")
            return

        # Fallback for local testing
        if username == "admin" and password == "admin123":
            self.on_login_success((1, "admin", "admin"))
        elif username == "user" and password == "user123":
            self.on_login_success((2, "user", "user"))
        else:
            QMessageBox.critical(self, "Login Failed", "Invalid credentials.")
