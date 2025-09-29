# standard_user_window.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QLabel, QCheckBox, QMessageBox, QTextEdit, QDialog, QDialogButtonBox
)
from PyQt5.QtCore import Qt
import styles


class FailureDialog(QDialog):
    """Popup dialog for entering failure explanation"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Failure Explanation")
        self.setModal(True)

        layout = QVBoxLayout()

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Enter failure explanation...")
        layout.addWidget(self.text_edit)

        # Buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self.setLayout(layout)

        # Shortcut: Enter submits (Save), Escape cancels
        self.button_box.button(QDialogButtonBox.Save).setShortcut(Qt.Key_Return)
        self.button_box.button(QDialogButtonBox.Save).setShortcut(Qt.Key_Enter)
        self.button_box.button(QDialogButtonBox.Cancel).setShortcut(Qt.Key_Escape)

    def get_text(self):
        return self.text_edit.toPlainText().strip()


class UserWindow(QWidget):
    def __init__(self, username: str):
        super().__init__()
        self.username = username
        self.setWindowTitle("Label Tracker - User")
        self.setStyleSheet(styles.WINDOW_STYLE)

        # Track fail history per board
        self.board_history = {}  # {board_id: {"was_failed": bool}}
        self.current_board = None

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Welcome message
        welcome = QLabel(f"Welcome, {self.username}")
        layout.addWidget(welcome)

        # --- Order number input ---
        order_layout = QHBoxLayout()
        self.order_input = QLineEdit()
        self.order_input.setPlaceholderText("Enter order number")
        self.order_input.returnPressed.connect(self.load_order_info)  # Enter = search
        self.search_button = QPushButton("Search Order")
        self.search_button.setStyleSheet(styles.BUTTON_STYLE)
        self.search_button.clicked.connect(self.load_order_info)
        order_layout.addWidget(self.order_input)
        order_layout.addWidget(self.search_button)
        layout.addLayout(order_layout)

        # --- Company & Board info labels ---
        self.company_label = QLabel("Company: ---") #TODO: pull company info from db
        self.board_label = QLabel("Board Number: ---") #TODO: pull board info from db
        layout.addWidget(self.company_label)
        layout.addWidget(self.board_label)

        # --- Order info table ---
        self.order_table = QTableWidget()
        self.order_table.setColumnCount(3) #TODO: update to show all columns from xlsx files
        self.order_table.setHorizontalHeaderLabels(["Board ID", "Description", "Status"]) #TODO: update to show all headers from xlsx files
        self.order_table.cellClicked.connect(self.select_board)
        layout.addWidget(self.order_table)

        self.order_table.setEditTriggers(QTableWidget.NoEditTriggers)  # read-only
        self.order_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.order_table.setSelectionMode(QTableWidget.SingleSelection)


        # --- SN input ---
        sn_layout = QHBoxLayout()
        self.sn_input = QLineEdit()
        self.sn_input.setPlaceholderText("Scan/enter board SN")
        self.sn_input.returnPressed.connect(self.submit_sn)  # Enter = submit
        sn_layout.addWidget(self.sn_input)
        layout.addLayout(sn_layout)

        # --- Pass/Fail checkboxes ---
        check_layout = QHBoxLayout()
        self.pass_checkbox = QCheckBox("Pass")
        self.fail_checkbox = QCheckBox("Fail")
        self.pass_checkbox.stateChanged.connect(self.toggle_checkboxes)
        self.fail_checkbox.stateChanged.connect(self.toggle_checkboxes)
        check_layout.addWidget(self.pass_checkbox)
        check_layout.addWidget(self.fail_checkbox)
        layout.addLayout(check_layout)

        # --- Submit button ---
        self.sn_button = QPushButton("Submit SN")
        self.sn_button.setStyleSheet(styles.BUTTON_STYLE)
        self.sn_button.setEnabled(False)
        self.sn_button.clicked.connect(self.submit_sn)
        layout.addWidget(self.sn_button)

        self.setLayout(layout)

    def load_order_info(self):
        """ Placeholder for fetching order info from backend """
        order_number = self.order_input.text().strip()
        if not order_number:
            QMessageBox.warning(self, "Error", "Please enter an order number.")
            return

        # 🔧 Placeholder: pretend to fetch company and board info
        self.company_label.setText("Company: Example Corp")
        self.board_label.setText(f"Board Number: {order_number}-001")

        # 🔧 Placeholder: populate dummy data until backend is ready
        data = [
            ("B001", "Board Type A", "Pending"),
            ("B002", "Board Type B", "Pending"),
            ("B003", "Board Type C", "Pending"),
        ]
        self.order_table.setRowCount(len(data))
        self.board_history.clear()

        for row, (board_id, desc, status) in enumerate(data):
            self.order_table.setItem(row, 0, QTableWidgetItem(board_id))
            self.order_table.setItem(row, 1, QTableWidgetItem(desc))
            self.order_table.setItem(row, 2, QTableWidgetItem(status))
            self.board_history[board_id] = {"was_failed": False}

    def select_board(self, row, column):
        """ Select a board from the table """
        board_id_item = self.order_table.item(row, 0)
        if board_id_item:
            self.current_board = board_id_item.text()
        else:
            self.current_board = None

        # Reset fields when switching boards
        self.sn_input.clear()
        self.pass_checkbox.setChecked(False)
        self.fail_checkbox.setChecked(False)
        self.sn_button.setEnabled(False)

    def toggle_checkboxes(self, state):
        """ Ensure only one checkbox is active, handle fail popup """
        if not self.current_board:
            QMessageBox.warning(self, "Error", "Please select a board first.")
            self.pass_checkbox.setChecked(False)
            self.fail_checkbox.setChecked(False)
            return

        if self.sender() == self.pass_checkbox and state == 2:
            self.fail_checkbox.setChecked(False)
            self.sn_button.setEnabled(True)  # pass only needs SN
        elif self.sender() == self.fail_checkbox and state == 2:
            self.pass_checkbox.setChecked(False)
            self.open_failure_dialog()

    def open_failure_dialog(self):
        """ Popup dialog for failure explanation """
        dialog = FailureDialog(self)
        result = dialog.exec_()

        if result == QDialog.Accepted:
            explanation = dialog.get_text()
            if not explanation:
                QMessageBox.warning(self, "Error", "Failure explanation is required.")
                self.fail_checkbox.setChecked(False)
                return

            # Auto-submit with failure reason
            self.submit_sn(failure_reason=explanation)
        else:
            # Cancel pressed → reset
            self.fail_checkbox.setChecked(False)

    def submit_sn(self, failure_reason="", fix_reason=""):
        """ Submit SN + result for current board """
        if not self.current_board:
            QMessageBox.warning(self, "Error", "Please select a board first.")
            return

        sn = self.sn_input.text().strip()
        if not sn:
            QMessageBox.warning(self, "Error", "Please enter an SN before submitting.")
            return

        result = "Pass" if self.pass_checkbox.isChecked() else "Fail"

        # Update board history
        if result == "Fail":
            self.board_history[self.current_board]["was_failed"] = True

        # 🔧 Backend call goes here
        msg = f"Board {self.current_board} → SN {sn} recorded as {result}."
        if failure_reason:
            msg += f"\nFailure reason: {failure_reason}"
        if fix_reason:
            msg += f"\nFix explanation: {fix_reason}"

        QMessageBox.information(self, "SN Submitted", msg)

        # Update status in table
        self.update_board_status(result)

        # Reset input fields but keep board selected
        self.sn_input.clear()
        self.pass_checkbox.setChecked(False)
        self.fail_checkbox.setChecked(False)
        self.sn_button.setEnabled(False)

    def update_board_status(self, status):
        """Update the board's status in the table"""
        for row in range(self.order_table.rowCount()):
            if self.order_table.item(row, 0).text() == self.current_board:
                self.order_table.setItem(row, 2, QTableWidgetItem(status))
                break