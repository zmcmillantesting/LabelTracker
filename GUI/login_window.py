from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QMessageBox, QLineEdit, 
    QPushButton, QLabel, QFrame
)
from PyQt5.QtCore import Qt
from GUI.widgets import create_label, create_input, create_button
import GUI.styles as styles


class LoginWindow(QWidget):
    def __init__(self, on_login_success, db_manager=None):
        super().__init__()
        self.on_login_success = on_login_success
        self.db_manager = db_manager
        self.setup_ui()

    def setup_ui(self):
        # Main container with dark background
        main_container = QWidget(self)
        main_container.setStyleSheet("background-color: #0f1419;")
        
        # Main layout for the entire window
        window_layout = QVBoxLayout(self)
        window_layout.setContentsMargins(0, 0, 0, 0)
        window_layout.addWidget(main_container)
        
        # Layout to center the login card
        center_layout = QVBoxLayout(main_container)
        center_layout.setAlignment(Qt.AlignCenter)
        
        # Create login card frame
        card = QFrame()
        card.setObjectName("loginCard")
        card.setFixedWidth(400)
        card.setStyleSheet("""
            QFrame#loginCard {
                background-color: #1a1a2e;
                border-radius: 12px;
                border: 1px solid #2a2a4e;
            }
        """)
        
        # Card layout
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(20)
        card_layout.setContentsMargins(40, 50, 40, 50)
        
        # --- Header ---
        title = QLabel("Label Tracker")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 34pt;
                font-weight: bold;
                color: #764ba2;
                background: transparent;
                border: none;
            }
        """)
        
        subtitle = QLabel("Sign in to continue")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("""
            QLabel {
                font-size: 11pt;
                color: #888;
                background: transparent;
                border: none;
                margin-bottom: 10px;
            }
        """)
        
        # --- Username ---
        username_label = QLabel("Username")
        username_label.setStyleSheet("""
            QLabel {
                font-size: 10pt;
                font-weight: 600;
                color: #aaa;
                background: transparent;
                border: none;
            }
        """)
        
        self.username_input = create_input("Enter your username")
        
        # --- Password ---
        password_label = QLabel("Password")
        password_label.setStyleSheet("""
            QLabel {
                font-size: 10pt;
                font-weight: 600;
                color: #aaa;
                background: transparent;
                border: none;
            }
        """)
        
        # Password container
        pw_container = QWidget()
        pw_container.setStyleSheet("""
            QWidget {
                background-color: #2b2240;
                border: 2px solid #3a2f59;
                border-radius: 8px;
            }
        """)
        pw_layout = QHBoxLayout(pw_container)
        pw_layout.setContentsMargins(0, 0, 0, 0)
        pw_layout.setSpacing(0)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 12px 16px;
                background-color: transparent;
                border: none;
                color: #eee;
                min-height: 42px;
                font-size: 12pt;
            }
            QLineEdit::placeholder {
                color: #666;
            }
        """)
        
        self.toggle_pw_button = QPushButton("👁️")
        self.toggle_pw_button.setCheckable(True)
        self.toggle_pw_button.setFixedSize(46, 46)
        self.toggle_pw_button.setCursor(Qt.PointingHandCursor)
        self.toggle_pw_button.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
                font-size: 18px;
                border-radius: 6px;
                margin-right: 6px;
            }
            QPushButton:hover {
                background-color: rgba(138, 110, 240, 0.2);
            }
        """)
        self.toggle_pw_button.clicked.connect(self.toggle_password_visibility)
        
        pw_layout.addWidget(self.password_input)
        pw_layout.addWidget(self.toggle_pw_button)
        
        # --- Login Button ---
        self.login_button = create_button("Sign In")
        self.login_button.setMinimumHeight(48)
        self.login_button.clicked.connect(self.handle_login)
        self.login_button.setCursor(Qt.PointingHandCursor)
        
        # Enable Enter key
        self.username_input.returnPressed.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)
        
        # --- Assemble Card ---
        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(10)
        card_layout.addWidget(username_label)
        card_layout.addWidget(self.username_input)
        card_layout.addSpacing(5)
        card_layout.addWidget(password_label)
        card_layout.addWidget(pw_container)
        card_layout.addSpacing(15)
        card_layout.addWidget(self.login_button)
        
        # Add card to center layout
        center_layout.addWidget(card, 0, Qt.AlignCenter)

    def toggle_password_visibility(self):
        """Toggle password visibility when the eye button is clicked."""
        if self.toggle_pw_button.isChecked():
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.toggle_pw_button.setText("🙈")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.toggle_pw_button.setText("👁️")

    def handle_login(self):
        """Handle login button click - authenticate and call success callback"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Login Failed", "Please enter both username and password.")
            return

        # Try database authentication first
        if self.db_manager:
            try:
                user = self.db_manager.authenticate_user(username, password)
                if user:
                    self.on_login_success(user)
                    return
                else:
                    QMessageBox.critical(self, "Login Failed", "Invalid credentials.")
                    return
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