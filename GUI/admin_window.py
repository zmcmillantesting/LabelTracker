# admin_window.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QTableWidget, QTableWidgetItem, QAbstractItemView, QMessageBox,
    QTreeWidget, QTreeWidgetItem, QMenu, QInputDialog, QTabWidget
)
from PyQt5.QtCore import Qt
import styles


class AdminWindow(QWidget):
    def __init__(self, username: str):
        super().__init__()
        self.username = username
        self.setWindowTitle("Label Tracker - Admin")
        self.setStyleSheet(styles.WINDOW_STYLE)

        # Store company → boards in memory
        self.company_boards = {
            "Example Corp A": ["Board Type A"],
            "Example Corp B": ["Board Type B"]
        }

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        welcome = QLabel(f"Welcome, Admin {self.username}")
        layout.addWidget(welcome)

        # Tabs
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Tab 1: Orders
        self.tabs.addTab(self.build_orders_tab(), "Orders")

        # Tab 2: Companies & Boards
        self.tabs.addTab(self.build_companies_boards_tab(), "Companies & Boards")

        # Tab 3: Archive
        self.tabs.addTab(self.build_archive_tab(), "Archive")

        # Tab 4: Users
        self.tabs.addTab(self.build_users_tab(), "Users")

        self.setLayout(layout)
        self.refresh_company_tree()
        self.refresh_dropdowns()

    # --- Orders Tab ---
    def build_orders_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        layout.addWidget(QLabel("Create New Order"))

        order_layout = QHBoxLayout()
        self.company_dropdown = QComboBox()
        self.company_dropdown.addItem("Select Company")

        self.board_dropdown = QComboBox()
        self.board_dropdown.addItem("Select Board")

        self.total_boards_input = QLineEdit()
        self.total_boards_input.setPlaceholderText("Enter total boards")
        self.total_boards_input.returnPressed.connect(self.create_order)

        self.create_order_button = QPushButton("Create Order")
        self.create_order_button.setStyleSheet(styles.BUTTON_STYLE)
        self.create_order_button.clicked.connect(self.create_order)

        order_layout.addWidget(self.company_dropdown)
        order_layout.addWidget(self.board_dropdown)
        order_layout.addWidget(self.total_boards_input)
        order_layout.addWidget(self.create_order_button)
        layout.addLayout(order_layout)

        return tab

    # --- Companies & Boards Tab ---
    def build_companies_boards_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Add company
        layout.addWidget(QLabel("Create New Company"))
        company_layout = QHBoxLayout()
        self.new_company_input = QLineEdit()
        self.new_company_input.setPlaceholderText("Enter new company name")
        self.new_company_input.returnPressed.connect(self.add_company)
        self.add_company_button = QPushButton("Add Company")
        self.add_company_button.setStyleSheet(styles.BUTTON_STYLE)
        self.add_company_button.clicked.connect(self.add_company)
        company_layout.addWidget(self.new_company_input)
        company_layout.addWidget(self.add_company_button)
        layout.addLayout(company_layout)

        # Add board
        layout.addWidget(QLabel("Create New Board"))
        board_layout = QHBoxLayout()
        self.company_for_board_dropdown = QComboBox()
        self.company_for_board_dropdown.addItem("Select Company")

        self.new_board_input = QLineEdit()
        self.new_board_input.setPlaceholderText("Enter new board name/ID")
        self.new_board_input.returnPressed.connect(self.add_board)

        self.add_board_button = QPushButton("Add Board")
        self.add_board_button.setStyleSheet(styles.BUTTON_STYLE)
        self.add_board_button.clicked.connect(self.add_board)

        board_layout.addWidget(self.company_for_board_dropdown)
        board_layout.addWidget(self.new_board_input)
        board_layout.addWidget(self.add_board_button)
        layout.addLayout(board_layout)

        # Company → Board tree
        layout.addWidget(QLabel("Company & Board List"))
        self.company_tree = QTreeWidget()
        self.company_tree.setHeaderLabels(["Company", "Boards"])
        self.company_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.company_tree.customContextMenuRequested.connect(self.open_context_menu)
        layout.addWidget(self.company_tree)

        return tab

    # --- Archive Tab ---
    def build_archive_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search archived orders...")
        self.search_input.returnPressed.connect(self.search_archived_orders)
        self.search_button = QPushButton("Search")
        self.search_button.setStyleSheet(styles.BUTTON_STYLE)
        self.search_button.clicked.connect(self.search_archived_orders)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        layout.addLayout(search_layout)

        # Archived orders table
        self.archived_table = QTableWidget()
        self.archived_table.setColumnCount(3)
        self.archived_table.setHorizontalHeaderLabels(["Order ID", "Company", "Board"])
        self.archived_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.archived_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.archived_table.setSelectionMode(QAbstractItemView.SingleSelection)
        layout.addWidget(self.archived_table)

        self.archive_button = QPushButton("Archive Selected Order")
        self.archive_button.setStyleSheet(styles.BUTTON_STYLE)
        self.archive_button.clicked.connect(self.archive_order)
        layout.addWidget(self.archive_button)

        return tab

    # --- Users Tab ---
    def build_users_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        layout.addWidget(QLabel("Add new user"))
        user_layout = QHBoxLayout()
        self.new_user_input = QLineEdit()
        self.new_user_input.setPlaceholderText("Enter username")
        self.new_user_password = QLineEdit()
        self.new_user_password.setPlaceholderText("Enter password")
        self.new_user_password.setEchoMode(QLineEdit.Password)
        self.add_user_button = QPushButton("Add User")
        self.add_user_button.setStyleSheet(styles.BUTTON_STYLE)
        self.add_user_button.clicked.connect(self.add_user)
        user_layout.addWidget(self.new_user_input)
        user_layout.addWidget(self.new_user_password)
        user_layout.addWidget(self.add_user_button)
        layout.addLayout(user_layout)

        layout.addWidget(QLabel("Manage users"))
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(2)
        self.user_table.setHorizontalHeaderLabels(["Username", "Role"])
        self.user_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.user_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.user_table.setSelectionMode(QAbstractItemView.SingleSelection)
        layout.addWidget(self.user_table)
        
        button_layout = QHBoxLayout()
        self.update_password_button = QPushButton("Update Password")
        self.update_password_button.setStyleSheet(styles.BUTTON_STYLE)
        self.update_password_button.clicked.connect(self.update_password)

        self.delete_user_button = QPushButton("Delete Selected User")
        self.delete_user_button.setStyleSheet(styles.BUTTON_STYLE)
        self.delete_user_button.clicked.connect(self.delete_user)

        button_layout.addWidget(self.update_password_button)
        button_layout.addWidget(self.delete_user_button)
        layout.addLayout(button_layout)

        return tab

    # --- Helper: Refresh dropdowns ---
    def refresh_dropdowns(self):
        # Companies
        self.company_dropdown.clear()
        self.company_dropdown.addItem("Select Company")
        self.company_for_board_dropdown.clear()
        self.company_for_board_dropdown.addItem("Select Company")
        for company in self.company_boards:
            self.company_dropdown.addItem(company)
            self.company_for_board_dropdown.addItem(company)

        # Boards
        self.board_dropdown.clear()
        self.board_dropdown.addItem("Select Board")
        for boards in self.company_boards.values():
            for board in boards:
                self.board_dropdown.addItem(board)

    # --- Helper: Refresh tree ---
    def refresh_company_tree(self):
        self.company_tree.clear()
        for company, boards in self.company_boards.items():
            company_item = QTreeWidgetItem([company])
            for board in boards:
                QTreeWidgetItem(company_item, ["", board])
            self.company_tree.addTopLevelItem(company_item)

    # --- Context Menu ---
    def open_context_menu(self, position):
        item = self.company_tree.itemAt(position)
        if not item:
            return
        menu = QMenu()
        if not item.parent():  # Company
            edit_action = menu.addAction("Edit Company")
            delete_action = menu.addAction("Delete Company")
            action = menu.exec_(self.company_tree.viewport().mapToGlobal(position))
            if action == edit_action:
                self.edit_company(item.text(0))
            elif action == delete_action:
                self.delete_company(item.text(0))
        else:  # Board
            company = item.parent().text(0)
            board = item.text(1)
            edit_action = menu.addAction("Edit Board")
            delete_action = menu.addAction("Delete Board")
            action = menu.exec_(self.company_tree.viewport().mapToGlobal(position))
            if action == edit_action:
                self.edit_board(company, board)
            elif action == delete_action:
                self.delete_board(company, board)

    # --- Placeholder Logic ---
    def create_order(self):
        company = self.company_dropdown.currentText()
        board = self.board_dropdown.currentText()
        total = self.total_boards_input.text().strip()
        if not total.isdigit():
            QMessageBox.warning(self, "Error", "Total boards must be a number.")
            return
        QMessageBox.information(self, "Order", f"Creating order: {company}, {board}, {total}")

    def add_company(self):
        company = self.new_company_input.text().strip()
        if not company:
            QMessageBox.warning(self, "Error", "Please enter a company name.")
            return
        self.company_boards[company] = []
        self.refresh_company_tree()
        self.refresh_dropdowns()
        self.new_company_input.clear()

    def add_board(self):
        board = self.new_board_input.text().strip()
        company = self.company_for_board_dropdown.currentText()
        if company == "Select Company":
            QMessageBox.warning(self, "Error", "Select a company first.")
            return
        if not board:
            QMessageBox.warning(self, "Error", "Please enter a board name.")
            return
        self.company_boards[company].append(board)
        self.refresh_company_tree()
        self.refresh_dropdowns()
        self.new_board_input.clear()
        self.company_for_board_dropdown.setCurrentIndex(0)

    def edit_company(self, company):
        new_name, ok = QInputDialog.getText(self, "Edit Company", "New name:", text=company)
        if ok and new_name.strip():
            self.company_boards[new_name.strip()] = self.company_boards.pop(company)
            self.refresh_company_tree()
            self.refresh_dropdowns()

    def delete_company(self, company):
        confirm = QMessageBox.question(self, "Delete", f"Delete {company}?")
        if confirm == QMessageBox.Yes:
            self.company_boards.pop(company, None)
            self.refresh_company_tree()
            self.refresh_dropdowns()

    def edit_board(self, company, board):
        new_name, ok = QInputDialog.getText(self, "Edit Board", "New name:", text=board)
        if ok and new_name.strip():
            boards = self.company_boards[company]
            boards[boards.index(board)] = new_name.strip()
            self.refresh_company_tree()
            self.refresh_dropdowns()

    def delete_board(self, company, board):
        confirm = QMessageBox.question(self, "Delete", f"Delete {board}?")
        if confirm == QMessageBox.Yes:
            self.company_boards[company].remove(board)
            self.refresh_company_tree()
            self.refresh_dropdowns()

    def search_archived_orders(self):
        self.archived_table.setRowCount(2)
        self.archived_table.setItem(0, 0, QTableWidgetItem("ORD001"))
        self.archived_table.setItem(0, 1, QTableWidgetItem("Example Corp A"))
        self.archived_table.setItem(0, 2, QTableWidgetItem("Board Type A"))

    def archive_order(self):
        row = self.archived_table.currentRow()
        if row >= 0:
            order_id = self.archived_table.item(row, 0).text()
            QMessageBox.information(self, "Archive", f"Archived order {order_id}")

    def add_user(self):
        username = self.new_user_input.text().strip()
        password = self.new_user_password.text().strip()
        if not username or not password:
            QMessageBox.warning(self, "Error", "Enter username and password")
            return
        row = self.user_table.rowCount()
        self.user_table.insertRow(row)
        self.user_table.setItem(row, 0, QTableWidgetItem(username))
        self.user_table.setItem(row, 1, QTableWidgetItem("Standard"))
        self.new_user_input.clear()
        self.new_user_password.clear()

    def update_password(self):
        row = self.user_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Please select a user first.")
            return

        username = self.user_table.item(row, 0).text()

        new_pass, ok = QInputDialog.getText(
            self, "Update Password", f"Enter new password for {username}:", QLineEdit.Password
        )
        if ok and new_pass.strip():
            # 🔧 Later: send update to backend
            QMessageBox.information(self, "Password Updated", f"Password updated for {username}")

    def delete_user(self):
        row = self.user_table.currentRow()
        if row >= 0:
            username = self.user_table.item(row, 0).text()
            confirm = QMessageBox.question(self, "Delete", f"Delete user {username}?")
            if confirm == QMessageBox.Yes:
                self.user_table.removeRow(row)