# app.py

import sys, os
import logging
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QGraphicsOpacityEffect
)
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QTimer
from PyQt5.QtGui import QIcon

from GUI.login_window import LoginWindow
from GUI.admin_window import AdminWindow
from GUI.standard_user_window import UserWindow

logger = logging.getLogger(__name__)

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(".")

icon_path = os.path.join(base_path, "GUI", "label_tracker_logo.ico")


class AppController(QMainWindow):
    def __init__(self, db_manager, xlsx_manager):
        super().__init__()

        self.setWindowTitle("Label Tracker")
        self.setWindowIcon(QIcon(base_path))
        self.resize(1000, 700)

        self.db_manager = db_manager
        self.xlsx_manager = xlsx_manager
        self.current_user = None
        
        # Store animation objects to prevent garbage collection
        self.fade_out_anim = None
        self.fade_in_anim = None
        self.fade_out_effect = None
        self.fade_in_effect = None
        self.opacity_out_anim = None
        self.opacity_in_anim = None
        self.opacity_out_effect = None
        self.opacity_in_effect = None

        # --- Central stacked widget ---
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Create the different views
        self.login_window = LoginWindow(self.handle_login_success, self.db_manager)
        self.admin_window = AdminWindow(
            username=None,
            user_id=None,
            db_manager=self.db_manager,
            xlsx_manager=self.xlsx_manager,
            on_logout=self.handle_logout
        )
        self.user_window = UserWindow(
            username=None,
            user_id=None,
            db_manager=self.db_manager,
            xlsx_manager=self.xlsx_manager,
            on_logout=self.handle_logout
        )

        # Add them to the stack
        self.stack.addWidget(self.login_window)
        self.stack.addWidget(self.admin_window)
        self.stack.addWidget(self.user_window)
        self.stack.setCurrentWidget(self.login_window)

        # logger.info("AppController initialized with fade transitions")

    # --- Transition Animation ---
    def fade_transition_to(self, new_widget):
        """Smoothly transition with purple fade effect."""
        from PyQt5.QtWidgets import QGraphicsColorizeEffect
        from PyQt5.QtGui import QColor
        
        current_widget = self.stack.currentWidget()
        
        # logger.info(f"Starting transition from {current_widget.__class__.__name__} to {new_widget.__class__.__name__}")

        # Create purple colorize effect that fades to purple
        self.fade_out_effect = QGraphicsColorizeEffect(current_widget)
        self.fade_out_effect.setColor(QColor("#764ba2"))  # Purple from your theme
        current_widget.setGraphicsEffect(self.fade_out_effect)
        
        # Animate strength from 0 (normal) to 1 (full purple)
        self.fade_out_anim = QPropertyAnimation(self.fade_out_effect, b"strength", self)
        self.fade_out_anim.setDuration(350)
        self.fade_out_anim.setStartValue(0.0)
        self.fade_out_anim.setEndValue(1.0)
        self.fade_out_anim.setEasingCurve(QEasingCurve.InOutQuad)
        
        # Also fade out opacity for smoother transition
        self.opacity_out_effect = QGraphicsOpacityEffect(current_widget)
        current_widget.setGraphicsEffect(self.opacity_out_effect)
        
        self.opacity_out_anim = QPropertyAnimation(self.opacity_out_effect, b"opacity", self)
        self.opacity_out_anim.setDuration(350)
        self.opacity_out_anim.setStartValue(1.0)
        self.opacity_out_anim.setEndValue(0.0)
        self.opacity_out_anim.setEasingCurve(QEasingCurve.InOutQuad)

        # When fade out finishes, switch page and fade in from purple
        def on_fade_out_finished():
            # logger.info("Purple fade out complete, switching widget")
            # Switch to new widget
            self.stack.setCurrentWidget(new_widget)
            
            # Remove effect from old widget
            current_widget.setGraphicsEffect(None)
            
            # Create purple colorize effect for new widget
            self.fade_in_effect = QGraphicsColorizeEffect(new_widget)
            self.fade_in_effect.setColor(QColor("#764ba2"))
            self.fade_in_effect.setStrength(1.0)  # Start fully purple
            new_widget.setGraphicsEffect(self.fade_in_effect)
            
            # Animate from purple back to normal
            self.fade_in_anim = QPropertyAnimation(self.fade_in_effect, b"strength", self)
            self.fade_in_anim.setDuration(350)
            self.fade_in_anim.setStartValue(1.0)
            self.fade_in_anim.setEndValue(0.0)
            self.fade_in_anim.setEasingCurve(QEasingCurve.InOutQuad)
            
            # Also fade in opacity
            self.opacity_in_effect = QGraphicsOpacityEffect(new_widget)
            new_widget.setGraphicsEffect(self.opacity_in_effect)
            
            self.opacity_in_anim = QPropertyAnimation(self.opacity_in_effect, b"opacity", self)
            self.opacity_in_anim.setDuration(350)
            self.opacity_in_anim.setStartValue(0.0)
            self.opacity_in_anim.setEndValue(1.0)
            self.opacity_in_anim.setEasingCurve(QEasingCurve.InOutQuad)
            
            # Clean up after fade in
            def on_fade_in_finished():
                # logger.info("Purple fade in complete, transition finished")
                new_widget.setGraphicsEffect(None)
            
            self.opacity_in_anim.finished.connect(on_fade_in_finished)
            self.fade_in_anim.start()
            self.opacity_in_anim.start()

        self.opacity_out_anim.finished.connect(on_fade_out_finished)
        self.fade_out_anim.start()
        self.opacity_out_anim.start()

    # --- Login + Logout Logic ---
    def handle_login_success(self, user_data):
        """Triggered when user logs in successfully."""
        self.current_user = user_data
        user_id, username, role = user_data
        # logger.info(f"User {username} (ID: {user_id}) logged in as {role}")
        
        print(f"DEBUG: About to transition to {role} window")  # Debug

        if role == "admin":
            self.admin_window.username = username
            self.admin_window.user_id = user_id
            print(f"DEBUG: Calling fade_transition_to(admin_window)")  # Debug
            self.fade_transition_to(self.admin_window)
        else:
            self.user_window.username = username
            self.user_window.user_id = user_id
            print(f"DEBUG: Calling fade_transition_to(user_window)")  # Debug
            self.fade_transition_to(self.user_window)

    def handle_logout(self):
        """Switch back to login view smoothly."""
        # logger.info("User logged out — returning to login view")
        self.current_user = None
        self.fade_transition_to(self.login_window)

    def run(self):
        self.show()


# --- Entry Point ---
if __name__ == "__main__":
    from managers.db_manager import DatabaseManager
    from managers.xlsx_manager import XLSXManager
    from utils.logger import setup_logging

    setup_logging()
    db = DatabaseManager()
    xlsx = XLSXManager(db)
    print("About to create QApplication")
    app = QApplication(sys.argv)

    from GUI.login_window import LoginWindow
    from GUI.admin_window import AdminWindow
    from GUI.standard_user_window import UserWindow

    controller = AppController(db, xlsx)
    controller.show()
    sys.exit(app.exec_())