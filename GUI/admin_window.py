# admin_window.py - Complete Sidebar Layout Version with styles.py integration

import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QTableWidget, QTableWidgetItem, QAbstractItemView, QMessageBox,
    QListWidget, QDialog, QDialogButtonBox, QTreeWidget, QTreeWidgetItem, 
    QMenu, QInputDialog, QFileDialog, QStackedWidget, QScrollArea, QFrame,
    QSizePolicy, QHeaderView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

# Force matplotlib backend BEFORE importing matplotlib components
import openpyxl
from datetime import datetime
import os
import GUI.styles as styles

logger = logging.getLogger(__name__)

# How many rows to try to show by default in split-screen
try:
    DEFAULT_VISIBLE_ROWS = int(os.environ.get('LT_VISIBLE_ROWS', '20'))
except Exception:
    DEFAULT_VISIBLE_ROWS = 15

class SidebarButton(QPushButton):
    """Custom sidebar navigation button"""
    def __init__(self, icon, text, parent=None):
        super().__init__(f"{icon}  {text}", parent)
        self.setCheckable(True)
        self.setMinimumHeight(50)
        self.setStyleSheet(styles.SIDEBAR_BUTTON_STYLE)


class ContentPanel(QWidget):
    """Base class for content panels with max-width container"""
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        
        center_layout = QHBoxLayout()
        center_layout.addStretch()
        
        self.content_widget = QWidget()
        self.content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        content_outer = QVBoxLayout(self.content_widget)
        content_outer.setContentsMargins(30, 30, 30, 30)

        title_label = QLabel(title)
        title_font = QFont("Segoe UI", 20, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #64b5f6; margin-bottom: 20px;")
        content_outer.addWidget(title_label)

        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(20)
        content_outer.addLayout(self.content_layout)
        content_outer.addStretch()

        center_layout.addWidget(self.content_widget, 1)
        center_layout.addStretch()
        
        container_layout.addLayout(center_layout)
        scroll.setWidget(container)
        self.main_layout.addWidget(scroll)


class BlockingOrdersDialog(QDialog):
    """Dialog that lists orders referencing a board"""
    def __init__(self, parent, orders):
        super().__init__(parent)
        self.setWindowTitle("Orders referencing board")
        self.orders = orders

        layout = QVBoxLayout()
        msg = QLabel(f"The following order(s) reference this board ({len(orders)}):")
        layout.addWidget(msg)

        self.list_widget = QListWidget()
        for order_number, file_path in orders:
            display = f"{order_number} — {file_path}"
            self.list_widget.addItem(display)
        layout.addWidget(self.list_widget)

        btn_box = QDialogButtonBox()
        self.copy_btn = btn_box.addButton("Copy List", QDialogButtonBox.ActionRole)
        self.open_btn = btn_box.addButton("Open Selected File", QDialogButtonBox.ActionRole)
        self.close_btn = btn_box.addButton(QDialogButtonBox.Close)

        self.copy_btn.clicked.connect(self.copy_list)
        self.open_btn.clicked.connect(self.open_selected)
        self.close_btn.clicked.connect(self.reject)

        layout.addWidget(btn_box)
        self.setLayout(layout)

    def copy_list(self):
        try:
            from PyQt5.QtWidgets import QApplication
            lines = [self.list_widget.item(i).text() for i in range(self.list_widget.count())]
            QApplication.clipboard().setText("\n".join(lines))
        except Exception:
            pass

    def open_selected(self):
        sel = self.list_widget.currentItem()
        if not sel:
            return
        text = sel.text()
        parts = text.split(' — ', 1)
        if len(parts) == 2:
            file_path = parts[1]
            try:
                if os.path.exists(file_path):
                    os.startfile(file_path)
                else:
                    QMessageBox.warning(self, "File Not Found", f"File not found:\n{file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Open Failed", f"Could not open file:\n{e}")


class AdminWindow(QWidget):
    def __init__(self, username: str, user_id: int, db_manager, xlsx_manager, on_logout=None):
        super().__init__()
        self.username = username
        self.user_id = user_id
        self.db_manager = db_manager
        self.xlsx_manager = xlsx_manager
        self.on_logout = on_logout
        
        self.setWindowTitle("Label Tracker - Admin")
        self.setMinimumSize(1200, 700)
        
        # Apply combined stylesheet from styles.py
        self.setStyleSheet(styles.FULL_APP_STYLE)

        logger.info(f"Admin window initialized for user: {username}")
        self.setup_ui()
        self.load_initial_data()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Sidebar
        sidebar = QWidget()
        sidebar.setFixedWidth(280)
        sidebar.setStyleSheet(styles.SIDEBAR_STYLE)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setSpacing(5)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)
        
        # App title
        title_label = QLabel("Label Tracker")
        title_label.setStyleSheet("""
            color: #64b5f6;
            font-size: 18pt;
            font-weight: bold;
            padding: 20px;
        """)
        sidebar_layout.addWidget(title_label)
        
        # User info
        user_label = QLabel(f"Admin: {self.username}")
        user_label.setStyleSheet("color: #aaa; padding: 0 20px 20px 20px;")
        sidebar_layout.addWidget(user_label)
        
        # Navigation buttons
        self.nav_buttons = []
        
        self.btn_create_order = SidebarButton("📦", "Create Order", self)
        self.btn_companies = SidebarButton("🏢", "Companies", self)
        self.btn_boards = SidebarButton("⚡", "Part Numbers", self)
        self.btn_awaiting = SidebarButton("⏳", "Awaiting Review", self)
        self.btn_archive = SidebarButton("📂", "Archive", self)
        self.btn_users = SidebarButton("👥", "Users", self)
        
        self.nav_buttons = [
            self.btn_create_order, self.btn_companies, self.btn_boards,
            self.btn_awaiting, self.btn_archive, self.btn_users
        ]
        
        for btn in self.nav_buttons:
            sidebar_layout.addWidget(btn)
            btn.clicked.connect(self.on_nav_clicked)
        
        sidebar_layout.addStretch()
        
        # Logout button
        self.logout_button = QPushButton("Logout")
        self.logout_button.setStyleSheet(styles.BUTTON_LOGOUT_STYLE)
        self.logout_button.clicked.connect(self.handle_logout)
        sidebar_layout.addWidget(self.logout_button)
        
        # Content area
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background-color: #0f1419;")
        
        # Create panels
        self.panel_create_order = self.build_create_order_panel()
        self.panel_companies = self.build_companies_panel()
        self.panel_boards = self.build_boards_panel()
        self.panel_awaiting = self.build_awaiting_panel()
        self.panel_archive = self.build_archive_panel()
        self.panel_users = self.build_users_panel()
        
        self.content_stack.addWidget(self.panel_create_order)
        self.content_stack.addWidget(self.panel_companies)
        self.content_stack.addWidget(self.panel_boards)
        self.content_stack.addWidget(self.panel_awaiting)
        self.content_stack.addWidget(self.panel_archive)
        self.content_stack.addWidget(self.panel_users)
        
        # Add to main layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.content_stack)
        
        # Set initial view
        self.btn_create_order.setChecked(True)
        self.content_stack.setCurrentIndex(0)

    def on_nav_clicked(self):
        """Handle navigation button clicks"""
        sender = self.sender()
        
        for btn in self.nav_buttons:
            if btn != sender:
                btn.setChecked(False)
        
        if sender == self.btn_create_order:
            self.content_stack.setCurrentIndex(0)
        elif sender == self.btn_companies:
            self.content_stack.setCurrentIndex(1)
        elif sender == self.btn_boards:
            self.content_stack.setCurrentIndex(2)
        elif sender == self.btn_awaiting:
            self.content_stack.setCurrentIndex(3)
            self.load_awaiting_confirmation_orders()
        elif sender == self.btn_archive:
            self.content_stack.setCurrentIndex(4)
            self.load_all_orders()
        elif sender == self.btn_users:
            self.content_stack.setCurrentIndex(5)

    def build_create_order_panel(self):
        """Build the create order content panel"""
        panel = ContentPanel("Create New Order")

        # Form fields in two columns
        form_outer = QHBoxLayout()
        left_col = QVBoxLayout()
        left_col.setSpacing(14)
        right_col = QVBoxLayout()
        right_col.setSpacing(14)

        # Left column
        left_col.addWidget(QLabel("Company"))
        self.company_dropdown = QComboBox()
        self.company_dropdown.addItem("Select company...", None)
        self.company_dropdown.currentIndexChanged.connect(self.on_company_selected)
        self.company_dropdown.setMinimumWidth(240)
        left_col.addWidget(self.company_dropdown)

        left_col.addWidget(QLabel("Order Number"))
        self.order_number_input = QLineEdit()
        self.order_number_input.setPlaceholderText("Enter order number...")
        self.order_number_input.returnPressed.connect(self.create_order)
        left_col.addWidget(self.order_number_input)

        left_col.addWidget(QLabel("Output Directory"))
        self.output_path_input = QLineEdit()
        self.output_path_input.setPlaceholderText("Optional: defaults to company path")
        left_col.addWidget(self.output_path_input)

        self.browse_output_button = QPushButton("Browse")
        self.browse_output_button.clicked.connect(self.browse_output_path)
        self.browse_output_button.setStyleSheet(styles.BUTTON_STYLE)
        left_col.addWidget(self.browse_output_button)

        # Right column
        right_col.addWidget(QLabel("Part Number"))
        self.board_dropdown = QComboBox()
        self.board_dropdown.addItem("Select part...", None)
        self.board_dropdown.setMinimumWidth(240)
        right_col.addWidget(self.board_dropdown)

        right_col.addWidget(QLabel("Total Boards"))
        self.total_boards_input = QLineEdit()
        self.total_boards_input.setPlaceholderText("100")
        self.total_boards_input.returnPressed.connect(self.create_order)
        right_col.addWidget(self.total_boards_input)

        right_col.addWidget(QLabel("Customer Code"))
        self.cust_code_input = QLineEdit()
        self.cust_code_input.setPlaceholderText("e.g. QTX")
        self.cust_code_input.returnPressed.connect(self.create_order)
        right_col.addWidget(self.cust_code_input)

        right_col.addWidget(QLabel("Serialized Prefix"))
        self.prefix_input = QLineEdit()
        self.prefix_input.setPlaceholderText("EXA-123456-")
        self.prefix_input.returnPressed.connect(self.create_order)
        right_col.addWidget(self.prefix_input)

        left_widget = QWidget()
        left_widget.setLayout(left_col)
        left_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        left_widget.setMinimumWidth(420)

        right_widget = QWidget()
        right_widget.setLayout(right_col)
        right_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        right_widget.setMinimumWidth(420)

        form_outer.addWidget(left_widget)
        form_outer.addSpacing(30)
        form_outer.addWidget(right_widget)

        inputs = (self.company_dropdown, self.board_dropdown, self.order_number_input,
                  self.total_boards_input, self.cust_code_input, self.output_path_input)
        for w in inputs:
            try:
                w.setMinimumHeight(48)
                w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                w.setMinimumWidth(360)
            except Exception:
                pass

        panel.content_layout.addLayout(form_outer)
        
        # Action buttons
        btn_row = QHBoxLayout()
        self.preview_button = QPushButton("Preview")
        self.preview_button.clicked.connect(self.preview_order)
        self.preview_button.setStyleSheet(styles.BUTTON_LINK_STYLE)
        btn_row.addWidget(self.preview_button)

        self.create_order_button = QPushButton("Create Order")
        self.create_order_button.clicked.connect(self.create_order)
        self.create_order_button.setStyleSheet(styles.BUTTON_LINK_STYLE)
        btn_row.addWidget(self.create_order_button)
        btn_row.addStretch()

        panel.content_layout.addLayout(btn_row)
        
        # Preview table
        self.preview_label = QLabel("Preview (first 50 rows)")
        self.preview_label.setVisible(False)
        panel.content_layout.addWidget(self.preview_label)
        
        self.preview_table = QTableWidget()
        self.preview_table.setColumnCount(8)
        self.preview_table.setHorizontalHeaderLabels([
            "User ID", "Company ID", "Board ID", "Serial Number",
            "Pass/Fail", "Timestamp", "Fail Explanation", "Fix Explanation"
        ])
        self.preview_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.preview_table.setVisible(False)
        try:
            self.preview_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.preview_table.horizontalHeader().setStretchLastSection(True)
        except Exception:
            pass
        self.preview_table.setWordWrap(True)
        self.preview_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.preview_table.setMinimumHeight(DEFAULT_VISIBLE_ROWS * 24 + 48)
        panel.content_layout.addWidget(self.preview_table)
        
        panel.content_layout.addStretch()
        return panel

    def build_companies_panel(self):
        """Build companies management panel"""
        panel = ContentPanel("Manage Companies")
        
        add_layout = QHBoxLayout()
        self.new_company_input = QLineEdit()
        self.new_company_input.setPlaceholderText("Company name")
        self.new_company_input.returnPressed.connect(self.add_company)
        add_layout.addWidget(self.new_company_input)
        
        self.new_company_cust_input = QLineEdit()
        self.new_company_cust_input.setPlaceholderText("Customer Code (e.g. QTX)")
        self.new_company_cust_input.returnPressed.connect(self.add_company)
        add_layout.addWidget(self.new_company_cust_input)
        
        add_btn = QPushButton("Add Company")
        add_btn.clicked.connect(self.add_company)
        add_btn.setStyleSheet(styles.BUTTON_LINK_STYLE)
        add_layout.addWidget(add_btn)
        
        panel.content_layout.addLayout(add_layout)
        
        self.show_archived_checkbox = QPushButton("Show Archived Companies")
        self.show_archived_checkbox.setCheckable(True)
        self.show_archived_checkbox.toggled.connect(self.on_toggle_show_archived)
        self.show_archived_checkbox.setStyleSheet(styles.BUTTON_STYLE)
        panel.content_layout.addWidget(self.show_archived_checkbox)
        
        self.company_tree = QTreeWidget()
        self.company_tree.setHeaderLabels(["Company", "Orders & Boards"])
        self.company_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.company_tree.customContextMenuRequested.connect(self.open_context_menu)
        self.company_tree.setMinimumHeight(DEFAULT_VISIBLE_ROWS * 24 + 48)
        panel.content_layout.addWidget(self.company_tree)
        
        return panel

    def build_boards_panel(self):
        """Build boards management panel"""
        panel = ContentPanel("Manage Part Numbers")
        
        add_layout = QHBoxLayout()
        self.company_for_board_dropdown = QComboBox()
        self.company_for_board_dropdown.addItem("Select Company", None)
        add_layout.addWidget(self.company_for_board_dropdown)
        
        self.new_board_input = QLineEdit()
        self.new_board_input.setPlaceholderText("Part number / board name")
        self.new_board_input.returnPressed.connect(self.add_board)
        add_layout.addWidget(self.new_board_input)
        
        add_btn = QPushButton("Add Part Number")
        add_btn.clicked.connect(self.add_board)
        add_btn.setStyleSheet(styles.BUTTON_LINK_STYLE)
        add_layout.addWidget(add_btn)
        
        panel.content_layout.addLayout(add_layout)
        panel.content_layout.addStretch()
        
        return panel

    def build_awaiting_panel(self):
        """Build awaiting confirmation panel with order details and pie chart"""
        panel = ContentPanel("Order Review")

        # Split into two sections: order list (left) and details (right)
        main_layout = QHBoxLayout()

        # Left side - Order list
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_widget.setMinimumWidth(500)

        info = QLabel("All Orders - Click to view details")
        info.setStyleSheet("color: #aaa; margin-bottom: 10px;")
        left_layout.addWidget(info)

        # Filter buttons
        filter_layout = QHBoxLayout()
        self.filter_all_btn = QPushButton("All")
        self.filter_pending_btn = QPushButton("Pending")
        self.filter_active_btn = QPushButton("Active")
        self.filter_complete_btn = QPushButton("Complete")

        filter_buttons = [self.filter_all_btn, self.filter_pending_btn, 
                         self.filter_active_btn, self.filter_complete_btn]

        for btn in filter_buttons:
            btn.setCheckable(True)
            btn.setStyleSheet(styles.BUTTON_STYLE)
            btn.clicked.connect(self.apply_order_filter)
            filter_layout.addWidget(btn)

        self.filter_all_btn.setChecked(True)
        left_layout.addLayout(filter_layout)

        self.await_table = QTableWidget()
        self.await_table.setColumnCount(5)
        self.await_table.setHorizontalHeaderLabels([
            "Order ID", "Order Number", "Company", "Board", "Status"
        ])
        self.await_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.await_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.await_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.await_table.itemSelectionChanged.connect(self.on_order_selected)
        try:
            self.await_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        except Exception:
            pass
        left_layout.addWidget(self.await_table)

        # Right side - Order details and pie chart
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_widget.setMinimumWidth(400)

        self.order_details_label = QLabel("Select an order to view details")
        self.order_details_label.setStyleSheet("color: #64b5f6; font-size: 14pt; font-weight: bold;")
        right_layout.addWidget(self.order_details_label)

        # Order info
        self.order_info_widget = QWidget()
        self.order_info_layout = QVBoxLayout(self.order_info_widget)
        self.order_number_label = QLabel()
        self.order_company_label = QLabel()
        self.order_board_label = QLabel()
        self.order_total_label = QLabel()

        for label in [self.order_number_label, self.order_company_label, 
                      self.order_board_label, self.order_total_label]:
            label.setStyleSheet("color: #ccc; font-size: 11pt; margin: 5px 0;")
            self.order_info_layout.addWidget(label)

        right_layout.addWidget(self.order_info_widget)
        self.order_info_widget.setVisible(False)

        # Pie chart
        self.stats_widget = QWidget()
        self.stats_layout = QVBoxLayout(self.stats_widget)
        self.stats_widget.setStyleSheet("background-color: #1a1a2e; padding: 10px; border-radius: 8px;")
        right_layout.addWidget(self.stats_widget)
        self.stats_widget.setVisible(False)

        # Action buttons
        btn_row = QHBoxLayout()
        self.view_await_btn = QPushButton("Open File")
        self.view_await_btn.clicked.connect(self.view_selected_awaiting_file)
        self.view_await_btn.setStyleSheet(styles.BUTTON_STYLE)
        self.view_await_btn.setEnabled(False)
        btn_row.addWidget(self.view_await_btn)

        self.confirm_archive_btn = QPushButton("Mark Complete & Archive")
        self.confirm_archive_btn.clicked.connect(self.confirm_and_archive_selected)
        self.confirm_archive_btn.setStyleSheet(styles.BUTTON_STYLE)
        self.confirm_archive_btn.setEnabled(False)
        btn_row.addWidget(self.confirm_archive_btn)
        btn_row.addStretch()

        right_layout.addLayout(btn_row)
        right_layout.addStretch()

        # Add to main layout
        main_layout.addWidget(left_widget)
        main_layout.addWidget(right_widget)

        panel.content_layout.addLayout(main_layout)

        return panel
    
    def build_archive_panel(self):
        """Build archive panel"""
        panel = ContentPanel("Archive")
        
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search orders...")
        self.search_input.returnPressed.connect(self.search_archived_orders)
        search_layout.addWidget(self.search_input)
        
        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.search_archived_orders)
        search_btn.setStyleSheet(styles.BUTTON_LINK_STYLE)
        search_layout.addWidget(search_btn)
        
        load_btn = QPushButton("Load All")
        load_btn.clicked.connect(self.load_all_orders)
        load_btn.setStyleSheet(styles.BUTTON_LINK_STYLE)
        search_layout.addWidget(load_btn)
        
        panel.content_layout.addLayout(search_layout)
        
        orders_label = QLabel("Archived Orders")
        orders_label.setStyleSheet("color: #64b5f6; font-size: 14pt; font-weight: bold; margin-top: 10px;")
        panel.content_layout.addWidget(orders_label)

        order_btn_row = QHBoxLayout()
        restore_order_btn = QPushButton("Restore Order")
        restore_order_btn.clicked.connect(self.restore_selected_order)
        restore_order_btn.setStyleSheet(styles.BUTTON_STYLE)
        order_btn_row.addWidget(restore_order_btn)
        
        delete_order_btn = QPushButton("Delete Order Permanently")
        delete_order_btn.clicked.connect(self.delete_selected_order_permanently)
        delete_order_btn.setStyleSheet(styles.BUTTON_LOGOUT_STYLE)
        order_btn_row.addWidget(delete_order_btn)
        order_btn_row.addStretch()
        
        panel.content_layout.addLayout(order_btn_row)
        
        self.archived_table = QTableWidget()
        self.archived_table.setColumnCount(6)
        self.archived_table.setHorizontalHeaderLabels([
            "Order ID", "Order Number", "Company", "Board", "Status", "File Path"
        ])
        self.archived_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.archived_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.archived_table.setSelectionMode(QAbstractItemView.SingleSelection)
        try:
            self.archived_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        except Exception:
            pass
        self.archived_table.setMinimumHeight(DEFAULT_VISIBLE_ROWS * 24 + 48)
        panel.content_layout.addWidget(self.archived_table)
        
        
        boards_label = QLabel("Archived Boards")
        boards_label.setStyleSheet("color: #64b5f6; font-size: 14pt; font-weight: bold; margin-top: 5px; margin-bottom: 10px;")
        panel.content_layout.addWidget(boards_label)



        board_btn_row = QHBoxLayout()
        self.restore_board_button = QPushButton("Restore Board")
        self.restore_board_button.clicked.connect(self.restore_selected_board)
        self.restore_board_button.setStyleSheet(styles.BUTTON_STYLE)
        board_btn_row.addWidget(self.restore_board_button)

        delete_board_btn = QPushButton("Delete Board Permanently")
        delete_board_btn.clicked.connect(self.delete_selected_board_permanently)
        delete_board_btn.setStyleSheet(styles.BUTTON_LOGOUT_STYLE)
        board_btn_row.addWidget(delete_board_btn)
        board_btn_row.addStretch()
        panel.content_layout.addLayout(board_btn_row)

        self.archived_boards_table = QTableWidget()
        self.archived_boards_table.setColumnCount(3)
        self.archived_boards_table.setHorizontalHeaderLabels(["Board ID", "Board Name", "Company"])
        self.archived_boards_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.archived_boards_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.archived_boards_table.setSelectionMode(QAbstractItemView.SingleSelection)
        try:
            self.archived_boards_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.archived_boards_table.horizontalHeader().setStretchLastSection(True)
        except Exception:
            pass
        self.archived_boards_table.setWordWrap(True)
        self.archived_boards_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.archived_boards_table.setMinimumHeight(DEFAULT_VISIBLE_ROWS * 24 + 48)
        panel.content_layout.addWidget(self.archived_boards_table)
        
        
        companies_label = QLabel("Archived Companies")
        companies_label.setStyleSheet("color: #64b5f6; font-size: 14pt; font-weight: bold; margin-top: 20px;")
        panel.content_layout.addWidget(companies_label)
        
        comp_btn_layout = QHBoxLayout()
        self.restore_company_button = QPushButton("Restore Company")
        self.restore_company_button.clicked.connect(self.restore_selected_company)
        self.restore_company_button.setStyleSheet(styles.BUTTON_STYLE)
        comp_btn_layout.addWidget(self.restore_company_button)
        
        self.delete_company_permanent_button = QPushButton("Delete Company Permanently")
        self.delete_company_permanent_button.clicked.connect(self.delete_selected_company_permanently)
        self.delete_company_permanent_button.setStyleSheet(styles.BUTTON_LOGOUT_STYLE)
        comp_btn_layout.addWidget(self.delete_company_permanent_button)
        comp_btn_layout.addStretch()
        
        panel.content_layout.addLayout(comp_btn_layout)

        self.archived_companies_table = QTableWidget()
        self.archived_companies_table.setColumnCount(3)
        self.archived_companies_table.setHorizontalHeaderLabels(["Company ID", "Company Name", "Client Path"])
        self.archived_companies_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.archived_companies_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.archived_companies_table.setSelectionMode(QAbstractItemView.SingleSelection)
        try:
            self.archived_companies_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.archived_companies_table.horizontalHeader().setStretchLastSection(True)
        except Exception:
            pass
        self.archived_companies_table.setWordWrap(True)
        self.archived_companies_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.archived_companies_table.setMinimumHeight(DEFAULT_VISIBLE_ROWS * 24 + 48)
        panel.content_layout.addWidget(self.archived_companies_table)
        
        
        return panel

    def build_users_panel(self):
        """Build users management panel"""
        panel = ContentPanel("Manage Users")
        
        add_layout = QHBoxLayout()
        self.new_user_input = QLineEdit()
        self.new_user_input.setPlaceholderText("Username")
        add_layout.addWidget(self.new_user_input)
        
        self.new_user_password = QLineEdit()
        self.new_user_password.setPlaceholderText("Password")
        self.new_user_password.setEchoMode(QLineEdit.Password)
        add_layout.addWidget(self.new_user_password)
        
        self.user_role_dropdown = QComboBox()
        self.user_role_dropdown.addItem("user")
        self.user_role_dropdown.addItem("admin")
        add_layout.addWidget(self.user_role_dropdown)
        
        add_btn = QPushButton("Add User")
        add_btn.clicked.connect(self.add_user)
        add_btn.setStyleSheet(styles.BUTTON_LINK_STYLE)
        add_layout.addWidget(add_btn)
        
        panel.content_layout.addLayout(add_layout)
        
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(3)
        self.user_table.setHorizontalHeaderLabels(["User ID", "Username", "Role"])
        self.user_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.user_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.user_table.setSelectionMode(QAbstractItemView.SingleSelection)
        try:
            self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.user_table.horizontalHeader().setStretchLastSection(True)
        except Exception:
            pass
        self.user_table.setWordWrap(True)
        self.user_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.user_table.setMinimumHeight(DEFAULT_VISIBLE_ROWS * 24 + 48)
        panel.content_layout.addWidget(self.user_table)
        
        btn_row = QVBoxLayout()
        self.update_password_button = QPushButton("Update Password")
        self.update_password_button.clicked.connect(self.update_password)
        self.update_password_button.setStyleSheet(styles.BUTTON_STYLE)
        btn_row.addWidget(self.update_password_button)
        
        self.delete_user_button = QPushButton("Delete User")
        self.delete_user_button.clicked.connect(self.delete_user)
        self.delete_user_button.setStyleSheet(styles.BUTTON_LOGOUT_STYLE)
        btn_row.addWidget(self.delete_user_button)
        btn_row.addStretch()
        
        panel.content_layout.addLayout(btn_row)
        
        return panel

    def load_initial_data(self):
        """Load all data from database on startup"""
        try:
            self.refresh_company_tree()
            self.refresh_dropdowns()
            self.load_users()
            self.load_awaiting_confirmation_orders()
            logger.info("Initial data loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load initial data: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to load data:\n{str(e)}")

    def handle_logout(self):
        try:
            self.close()
            if callable(self.on_logout):
                self.on_logout()
        except Exception as e:
            logger.error(f"Error during logout: {e}", exc_info=True)

    def refresh_dropdowns(self):
        """Refresh company and board dropdowns from database"""
        try:
            include_archived = getattr(self, 'show_archived_checkbox', None) and self.show_archived_checkbox.isChecked()
            try:
                companies = self.db_manager.get_companies_all(include_archived=include_archived)
            except Exception:
                companies = self.db_manager.get_companies()
            
            # Clear and repopulate company dropdowns
            self.company_dropdown.clear()
            self.company_dropdown.addItem("Select Company", None)
            self.company_for_board_dropdown.clear()
            self.company_for_board_dropdown.addItem("Select Company", None)
            
            for company in companies:
                company_id, company_name = company[0], company[1]
                self.company_dropdown.addItem(company_name, company_id)
                self.company_for_board_dropdown.addItem(company_name, company_id)
            
            logger.info("Dropdowns refreshed")
        except Exception as e:
            logger.error(f"Failed to refresh dropdowns: {e}", exc_info=True)

    def on_company_selected(self, index):
        """When company is selected, load its boards"""
        company_id = self.company_dropdown.currentData()
        self.board_dropdown.clear()
        self.board_dropdown.addItem("Select Board", None)
        
        if company_id:
            try:
                boards = self.db_manager.get_boards_by_company(company_id)
                for b in boards:
                    board_id = b[0]
                    board_name = b[1]
                    archived = b[2] if len(b) > 2 else 0
                    if archived:
                        continue
                    self.board_dropdown.addItem(board_name, board_id)
                
                # Populate output path and customer code
                include_archived = getattr(self, 'show_archived_checkbox', None) and self.show_archived_checkbox.isChecked()
                try:
                    companies = self.db_manager.get_companies_all(include_archived=include_archived)
                except Exception:
                    companies = self.db_manager.get_companies()
                company = next((c for c in companies if c[0] == company_id), None)
                if company:
                    client_path = company[2] if len(company) > 2 else None
                    cust_id = company[3] if len(company) > 3 else None
                    if client_path:
                        self.output_path_input.setText(client_path)
                    if cust_id:
                        self.cust_code_input.setText(str(cust_id))
            except Exception as e:
                logger.error(f"Failed to load boards: {e}", exc_info=True)

    def on_order_selected(self):
        """Handle order selection - show details and pie chart"""
        row = self.await_table.currentRow()
        if row < 0:
            self.order_info_widget.setVisible(False)
            self.stats_widget.setVisible(False)
            self.view_await_btn.setEnabled(False)
            self.confirm_archive_btn.setEnabled(False)
            self.order_details_label.setText("Select an order to view details")
            return
        
        try:
            order_id = int(self.await_table.item(row, 0).text())
            order_number = self.await_table.item(row, 1).text()
            company = self.await_table.item(row, 2).text()
            board = self.await_table.item(row, 3).text()
            
            # Get file path
            orders = self.db_manager.get_orders()
            order = next((o for o in orders if o[0] == order_id), None)
            if not order:
                return
            
            file_path = order[5]
            
            # Calculate status
            status_str, pass_count, fail_count, pending_count, total_count = self.calculate_order_status(file_path)
            
            # Update labels
            self.order_details_label.setText(f"Order Details: {order_number}")
            self.order_number_label.setText(f"Order #: {order_number}")
            self.order_company_label.setText(f"Company: {company}")
            self.order_board_label.setText(f"Board: {board}")
            self.order_total_label.setText(f"Total Quantity: {total_count}")
            
            self.order_info_widget.setVisible(True)
            self.view_await_btn.setEnabled(True)
            self.confirm_archive_btn.setEnabled(status_str == "Complete")
            
            # Draw pie chart
            self.draw_pie_chart(pass_count, fail_count, pending_count)
            
        except Exception as e:
            logger.error(f"Failed to display order details: {e}", exc_info=True)
    
    def draw_pie_chart(self, pass_count, fail_count, pending_count):
        """Display pass/fail/pending statistics"""
        # Clear previous widgets
        while self.stats_layout.count():
            child = self.stats_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        total = pass_count + fail_count + pending_count

        if total == 0:
            no_data = QLabel("No data available")
            no_data.setStyleSheet("color: #aaa; font-size: 14pt;")
            no_data.setAlignment(Qt.AlignCenter)
            self.stats_layout.addWidget(no_data)
            self.stats_widget.setVisible(True)
            return

        # Title
        title = QLabel("Order Statistics")
        title.setStyleSheet("color: #64b5f6; font-size: 16pt; font-weight: bold; margin-bottom: 20px;")
        self.stats_layout.addWidget(title)

        # Pass
        if pass_count > 0:
            pct = (pass_count / total) * 100
            pass_label = QLabel(f"✓ Pass: {pass_count} ({pct:.1f}%)")
            pass_label.setStyleSheet("color: #4CAF50; font-size: 14pt; font-weight: bold; margin: 10px;")
            self.stats_layout.addWidget(pass_label)

        # Fail
        if fail_count > 0:
            pct = (fail_count / total) * 100
            fail_label = QLabel(f"✗ Fail: {fail_count} ({pct:.1f}%)")
            fail_label.setStyleSheet("color: #F44336; font-size: 14pt; font-weight: bold; margin: 10px;")
            self.stats_layout.addWidget(fail_label)

        # Pending
        if pending_count > 0:
            pct = (pending_count / total) * 100
            pending_label = QLabel(f"⏳ Pending: {pending_count} ({pct:.1f}%)")
            pending_label.setStyleSheet("color: #FFC107; font-size: 14pt; font-weight: bold; margin: 10px;")
            self.stats_layout.addWidget(pending_label)

        self.stats_layout.addStretch()
        self.stats_widget.setVisible(True)

    def refresh_company_tree(self):
        """Refresh company/board tree from database"""
        try:
            self.company_tree.clear()
            include_archived = getattr(self, 'show_archived_checkbox', None) and self.show_archived_checkbox.isChecked()
            try:
                companies = self.db_manager.get_companies_all(include_archived=include_archived)
            except Exception:
                companies = self.db_manager.get_companies()
            
            for company in companies:
                company_id = company[0]
                company_name = company[1]
                company_item = QTreeWidgetItem([company_name, ""])
                company_item.setData(0, Qt.UserRole, company_id)
                
                # Load boards
                boards = self.db_manager.get_boards_by_company(company_id)
                board_items = {}
                for b in boards:
                    board_id = b[0]
                    board_name = b[1]
                    archived = b[2] if len(b) > 2 else 0
                    if archived:
                        continue
                    board_item = QTreeWidgetItem(["", board_name])
                    board_item.setData(1, Qt.UserRole, board_id)
                    company_item.addChild(board_item)
                    board_items[board_id] = board_item

                # Load orders
                all_orders = self.db_manager.get_orders(company_id=company_id)
                for order in all_orders:
                    order_id, order_number, c_id, board_id, status, file_path, created_at, created_by = order
                    order_text = f"Order: {order_number} [{status}]"
                    order_item = QTreeWidgetItem(["", order_text])
                    order_item.setData(0, Qt.UserRole + 1, ("order", order_id))
                    order_item.setData(0, Qt.UserRole + 2, file_path)
                    
                    if board_id and board_id in board_items:
                        board_items[board_id].addChild(order_item)
                    else:
                        company_item.addChild(order_item)
                
                self.company_tree.addTopLevelItem(company_item)
                company_item.setExpanded(True)
            
            logger.info("Company tree refreshed")
        except Exception as e:
            logger.error(f"Failed to refresh company tree: {e}", exc_info=True)

    def open_context_menu(self, position):
        item = self.company_tree.itemAt(position)
        if not item:
            return
            
        menu = QMenu()
        
        # Check if order node
        try:
            data_order = item.data(0, Qt.UserRole + 1)
        except Exception:
            data_order = None

        if data_order and isinstance(data_order, tuple) and data_order[0] == 'order':
            order_id = data_order[1]
            view_action = menu.addAction("View Order File")
            archive_action = menu.addAction("Archive Order")
            action = menu.exec_(self.company_tree.viewport().mapToGlobal(position))
            
            if action == view_action:
                file_path = item.data(0, Qt.UserRole + 2)
                if file_path:
                    import os
                    try:
                        if os.path.exists(file_path):
                            os.startfile(file_path)
                        else:
                            QMessageBox.warning(self, "File not found", f"File not found:\n{file_path}")
                    except Exception as e:
                        QMessageBox.warning(self, "Open Failed", f"Could not open file:\n{e}")
                else:
                    QMessageBox.warning(self, "No file", "No file path recorded for this order.")

            elif action == archive_action:
                try:
                    self.db_manager.archive_order(order_id)
                    QMessageBox.information(self, "Archived", "Order archived and moved to Archive tab.")
                    self.load_all_orders()
                    self.refresh_company_tree()
                except Exception as e:
                    logger.error(f"Failed to archive order: {e}", exc_info=True)
                    QMessageBox.critical(self, "Error", f"Failed to archive order:\n{e}")
            return

        if not item.parent():  # Company
            company_name = item.text(0)
            company_id = item.data(0, Qt.UserRole)
            
            edit_action = menu.addAction("Edit Company Path")
            delete_action = menu.addAction("Archive Company")
            action = menu.exec_(self.company_tree.viewport().mapToGlobal(position))

            if action == edit_action:
                self.edit_company_path(company_id, company_name)
            elif action == delete_action:
                self.delete_company(company_id, company_name)
        else:  # Board
            board_name = item.text(1)
            board_id = item.data(1, Qt.UserRole)
            company_item = item.parent()
            company_name = company_item.text(0)
            company_id = company_item.data(0, Qt.UserRole)
            
            edit_action = menu.addAction("Edit Board")
            archive_action = menu.addAction("Archive Board")
            action = menu.exec_(self.company_tree.viewport().mapToGlobal(position))

            if action == edit_action:
                self.edit_board(company_id, board_id, board_name)
            elif action == archive_action:
                self.archive_board(company_id, board_id, board_name)

    def create_order(self):
        """Create a new order with XLSX file"""
        company_id = self.company_dropdown.currentData()
        board_id = self.board_dropdown.currentData()
        total = self.total_boards_input.text().strip()

        board_name = None
        try:
            with self.db_manager.get_connection() as conn:
                query = conn.cursor()
                query.execute("SELECT board_name FROM boards WHERE board_id=?", (board_id,))
                result = query.fetchone()
                if result:
                    board_name = result[0]
        except Exception as e:
            logger.error(f"Failed to fetch board name: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to fetch board name:\n{str(e)}")
            return

        if not company_id:
            QMessageBox.warning(self, "Error", "Please select a company.")
            return

        if not total.isdigit() or int(total) <= 0:
            QMessageBox.warning(self, "Error", "Total boards must be a positive number.")
            return

        order_number = self.order_number_input.text().strip()
        if not order_number:
            QMessageBox.warning(self, "Error", "Please enter an order number.")
            return

        # Check uniqueness
        try:
            with self.db_manager.get_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT order_id FROM orders WHERE order_number=?", (order_number,))
                if cur.fetchone():
                    QMessageBox.warning(self, "Error", f"Order number '{order_number}' already exists.")
                    return
        except Exception as e:
            logger.error(f"Failed to validate order number: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to validate order number:\n{str(e)}")
            return

        dest_dir = self.output_path_input.text().strip() or None

        try:
            cust_code = self.cust_code_input.text().strip() or None
            serial_prefix = self.prefix_input.text().strip() or None
            if not serial_prefix.endswith('-'):
                serial_prefix += '-'
                
            if cust_code:
                cust_code = cust_code.upper()

            if cust_code and board_name:
                serial_prefix = f"{cust_code}-{board_name}-{order_number}-"

            file_path, count = self.xlsx_manager.create_order_file(
                order_number=order_number,
                created_by=self.user_id,
                user_id=self.user_id,
                company_id=company_id,
                pass_fail=True,
                pass_fail_timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                failure_explanation="",
                fix_explanation="",
                board_id=board_id,
                serial_count=int(total),
                dest_dir=dest_dir,
                serial_prefix=serial_prefix,
            )

            logger.info(f"Order {order_number} created with {count} serial numbers")
            QMessageBox.information(
                self, 
                "Order Created", 
                f"Order {order_number} created successfully!\n"
                f"File: {file_path}\n"
                f"Serial numbers: {count}"
            )

            # Clear inputs
            self.company_dropdown.setCurrentIndex(0)
            self.board_dropdown.setCurrentIndex(0)
            self.total_boards_input.clear()
            self.order_number_input.clear()
            self.cust_code_input.clear()

        except Exception as e:
            logger.error(f"Failed to create order: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to create order:\n{str(e)}")

    def preview_order(self):
        """Generate preview of XLSX rows"""
        company_id = self.company_dropdown.currentData()
        board_id = self.board_dropdown.currentData()
        total = self.total_boards_input.text().strip()

        board_name = None
        try:
            with self.db_manager.get_connection() as conn:
                query = conn.cursor()
                query.execute("SELECT board_name FROM boards WHERE board_id=?", (board_id,))
                result = query.fetchone()
                if result:
                    board_name = result[0]
        except Exception as e:
            logger.error(f"Failed to preview order with correct SN:  {e}")
            raise


        if not company_id:
            QMessageBox.warning(self, "Error", "Please select a company to preview.")
            return

        if not total.isdigit() or int(total) <= 0:
            QMessageBox.warning(self, "Error", "Total boards must be a positive number.")
            return

        order_number = self.order_number_input.text().strip() or "PREVIEW"
        cust_code = self.cust_code_input.text().strip() or None
        if cust_code:
            cust_code = cust_code.upper()

        serial_prefix = None
        if cust_code:
            serial_prefix = f"{cust_code}-{board_name}-{order_number}-"

        serials = self.xlsx_manager._generate_serial_numbers(prefix=serial_prefix, start=1, count=int(total))

        show_count = min(len(serials), 50)
        self.preview_table.setRowCount(0)
        for i in range(show_count):
            sn = serials[i]
            row_idx = i
            self.preview_table.insertRow(row_idx)
            self.preview_table.setItem(row_idx, 0, QTableWidgetItem(str(self.user_id)))
            self.preview_table.setItem(row_idx, 1, QTableWidgetItem(str(company_id)))
            self.preview_table.setItem(row_idx, 2, QTableWidgetItem(str(board_id) if board_id else ""))
            self.preview_table.setItem(row_idx, 3, QTableWidgetItem(sn))
            self.preview_table.setItem(row_idx, 4, QTableWidgetItem("Pending"))
            self.preview_table.setItem(row_idx, 5, QTableWidgetItem(""))
            self.preview_table.setItem(row_idx, 6, QTableWidgetItem(""))
            self.preview_table.setItem(row_idx, 7, QTableWidgetItem(""))

        self.preview_label.setVisible(True)
        self.preview_table.setVisible(True)

    def browse_output_path(self):
        """Open folder picker for output directory"""
        selected = QFileDialog.getExistingDirectory(self, "Select Output Directory", "")
        if selected:
            self.output_path_input.setText(selected)

    def add_company(self):
        """Add a new company to database"""
        company_name = self.new_company_input.text().strip()
        cust_code = self.new_company_cust_input.text().strip()
        
        if not company_name:
            QMessageBox.warning(self, "Error", "Please enter a company name.")
            return
        if not cust_code:
            QMessageBox.warning(self, "Error", "Please enter a Customer Code (e.g. QTX).")
            return
        
        client_path = QFileDialog.getExistingDirectory(
            self,
            "Select Client Storage Path",
            "P:/Label Tracking"
        )
        
        if not client_path:
            return
        
        try:
            self.db_manager.add_company(company_name, client_path, cust_code.upper())
            logger.info(f"Company added: {company_name} (cust_id={cust_code.upper()})")
            QMessageBox.information(self, "Success", f"Company '{company_name}' added successfully!")
            
            self.refresh_company_tree()
            self.refresh_dropdowns()
            self.new_company_input.clear()
            self.new_company_cust_input.clear()
            
        except Exception as e:
            logger.error(f"Failed to add company: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to add company:\n{str(e)}")

    def edit_company_path(self, company_id, company_name):
        """Edit company storage path"""
        new_path = QFileDialog.getExistingDirectory(
            self,
            f"Select New Path for {company_name}",
            "P:/EMS Testing & Repair/clients"
        )
        
        if new_path is None or new_path == "":
            return

        try:
            companies = self.db_manager.get_companies()
            company = next((c for c in companies if c[0] == company_id), None)
            current_cust = company[3] if company and len(company) > 3 else ""
            new_cust, ok = QInputDialog.getText(self, "Edit Customer Code", "Customer Code:", text=str(current_cust))
            if not ok:
                return

            new_cust = new_cust.strip().upper() if new_cust else None

            with self.db_manager.get_connection() as conn:
                conn.execute(
                    "UPDATE companies SET client_path=?, cust_id=? WHERE company_id=?",
                    (new_path, new_cust, company_id)
                )
                conn.commit()

            logger.info(f"Company updated for {company_name}")
            QMessageBox.information(self, "Success", "Company updated!")
            self.refresh_company_tree()
            self.refresh_dropdowns()

        except Exception as e:
            logger.error(f"Failed to update company: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to update company:\n{str(e)}")

    def delete_company(self, company_id, company_name):
        """Archive a company"""
        confirm = QMessageBox.question(
            self,
            "Archive Company",
            f"Archive company '{company_name}' and hide it from normal lists?\n\nThis preserves boards and orders. Permanent deletion is available in the Archive tab.",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            try:
                self.db_manager.archive_company(company_id)
                logger.info(f"Company archived: {company_name}")
                QMessageBox.information(self, "Archived", "Company archived and hidden from normal lists.")
                self.refresh_company_tree()
                self.refresh_dropdowns()
            except Exception as e:
                logger.error(f"Failed to archive company: {e}", exc_info=True)
                QMessageBox.critical(self, "Error", f"Failed to archive company:\n{str(e)}")

    def on_toggle_show_archived(self, checked: bool):
        """Toggle showing archived companies"""
        try:
            self.refresh_company_tree()
            self.refresh_dropdowns()
        except Exception as e:
            logger.error(f"Failed to toggle show archived: {e}", exc_info=True)

    def add_board(self):
        """Add a new board to a company"""
        board_name = self.new_board_input.text().strip()
        company_id = self.company_for_board_dropdown.currentData()
        
        if not company_id:
            QMessageBox.warning(self, "Error", "Select a company first.")
            return
            
        if not board_name:
            QMessageBox.warning(self, "Error", "Please enter a board name.")
            return
        
        board_path = QFileDialog.getExistingDirectory(
            self,
            "Select Board/Part number Path",
            f"P:/Label Tracking/{company_id}"
        )

        if not board_path:
            return

        try:
            self.db_manager.add_board(company_id, board_name, board_path)
            logger.info(f"Board: {board_name} added with path {board_path}")
            QMessageBox.information(self, "Success", f"Board '{board_name}' added successfully!")
            
            self.refresh_company_tree()
            self.refresh_dropdowns()
            self.new_board_input.clear()
            
        except Exception as e:
            logger.error(f"Failed to add board: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to add board:\n{str(e)}")

    def edit_board(self, company_id, board_id, board_name):
        """Edit board name"""
        new_name, ok = QInputDialog.getText(
            self,
            "Edit Board",
            "New board name:",
            text=board_name
        )
        
        if ok and new_name.strip():
            try:
                with self.db_manager.get_connection() as conn:
                    conn.execute(
                        "UPDATE boards SET board_name=? WHERE board_id=?",
                        (new_name.strip(), board_id)
                    )
                    conn.commit()
                
                logger.info(f"Board updated: {board_name}")
                QMessageBox.information(self, "Success", "Board updated!")
                self.refresh_company_tree()
                self.refresh_dropdowns()
                
            except Exception as e:
                logger.error(f"Failed to update board: {e}", exc_info=True)
                QMessageBox.critical(self, "Error", f"Failed to update board:\n{str(e)}")

    def archive_board(self, company_id, board_id, board_name):
        """Mark a board as archived"""
        confirm = QMessageBox.question(
            self,
            "Archive Board",
            f"Archive board '{board_name}'?\n\nThis will hide it from normal lists but preserve existing orders.",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm != QMessageBox.Yes:
            return

        try:
            self.db_manager.archive_board(board_id)
            logger.info(f"Board archived: {board_name}")
            QMessageBox.information(self, "Archived", "Board archived successfully.")
            self.refresh_company_tree()
            self.refresh_dropdowns()
        except Exception as e:
            logger.error(f"Failed to archive board: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to archive board:\n{str(e)}")

    def load_all_orders(self):
        """Load all orders from database"""
        try:
            orders = self.db_manager.get_orders()
            self.populate_archive_orders(orders)
            try:
                self.populate_archived_boards()
                try:
                    self.populate_archived_companies()
                except Exception:
                    logger.exception("Failed to populate archived companies")
            except Exception:
                logger.exception("Failed to populate archived boards")
            logger.info(f"Loaded {len(orders)} orders")
            
        except Exception as e:
            logger.error(f"Failed to load orders: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to load orders:\n{str(e)}")

    def load_awaiting_confirmation_orders(self):
        """Load all orders with calculated status"""
        try:
            self.await_table.setRowCount(0)
            orders = self.db_manager.get_orders()

            companies = {c[0]: c[1] for c in self.db_manager.get_companies()}
            boards = {}
            for company_id in companies:
                for b in self.db_manager.get_boards_by_company(company_id):
                    board_id = b[0]
                    board_name = b[1]
                    archived = b[2] if len(b) > 2 else 0
                    if archived:
                        continue
                    boards[board_id] = board_name
            
            row_idx = 0
            for order in orders:
                order_id, order_number, company_id, board_id, db_status, file_path, created_at, created_by = order

                if db_status == "Archived":
                    continue  # Skip archived orders

                status_str, pass_count, fail_count, pending_count, total_count = self.calculate_order_status(file_path)

                company_name = companies.get(company_id, "Unknown")
                board_name = boards.get(board_id, "N/A") if board_id else "N/A"

                self.await_table.insertRow(row_idx)
                self.await_table.setItem(row_idx, 0, QTableWidgetItem(str(order_id)))
                self.await_table.setItem(row_idx, 1, QTableWidgetItem(order_number))
                self.await_table.setItem(row_idx, 2, QTableWidgetItem(company_name))
                self.await_table.setItem(row_idx, 3, QTableWidgetItem(board_name))

                status_item = QTableWidgetItem(status_str)
                if status_str == "Complete - All Pass":
                    status_item.setForeground(QColor("green"))
                    status_item.setFont(QFont("", weight=QFont.Bold))
                elif status_str == "Active":
                    status_item.setForeground(QColor("blue"))
                    status_item.setFont(QFont("", weight=QFont.Bold))
                elif status_str == "Pending":
                    status_item.setForeground(QColor("yellow"))
                    status_item.setFont(QFont("", weight=QFont.Bold))

                self.await_table.setItem(row_idx, 4, status_item)
                row_idx += 1
            logger.info(f"Loaded {row_idx} awaiting confirmation orders")
        except Exception as e:
            logger.error(f"Failed to load awaiting confirmation orders: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to load orders:\n{str(e)}")
        
        finally:
            try:
                self.await_table.resizeRowsToContents()
            except Exception:
                logger.exception("Failed to resize await table rows")
                pass

    def apply_order_filter(self):
        """Filter Orders based on seleted status"""
        sender = self.sender()

        filter_buttons = [self.filter_all_btn, self.filter_pending_btn, self.filter_active_btn, self.filter_complete_btn]
        for btn in filter_buttons:
            if btn != sender:
                btn.setChecked(False)
        
        sender.setChecked(True)

        filter_text = sender.text()

        for row in range(self.await_table.rowCount()):
            status_item = self.await_table.item(row, 4)
            if filter_text == "All":
                self.await_table.setRowHidden(row, False)
            else:
                status = status_item.text() if status_item else ""
                self.await_table.setRowHidden(row, status != filter_text)

    def search_archived_orders(self):
        """Search orders by order number or company"""
        search_term = self.search_input.text().strip().lower()
        
        if not search_term:
            self.load_all_orders()
            return
        
        try:
            all_orders = self.db_manager.get_orders()
            companies = {c[0]: c[1] for c in self.db_manager.get_companies()}
            boards = {}
            for company_id in companies:
                for b in self.db_manager.get_boards_by_company(company_id):
                    board_id = b[0]
                    board_name = b[1]
                    archived = b[2] if len(b) > 2 else 0
                    if archived:
                        continue
                    boards[board_id] = board_name
            
            filtered_orders = []
            for order in all_orders:
                order_id, order_number, company_id, board_id, status, file_path, created_at, created_by = order
                company_name = companies.get(company_id, "Unknown")
                board_name = boards.get(board_id, "N/A") if board_id else "N/A"
                
                if (search_term in order_number.lower() or 
                    search_term in company_name.lower() or
                    search_term in board_name.lower()):
                    filtered_orders.append(order)
            
            self.populate_archive_orders(filtered_orders)
            logger.info(f"Search found {len(filtered_orders)} orders")
            
        except Exception as e:
            logger.error(f"Failed to search orders: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to search:\n{str(e)}")

    def populate_archive_orders(self, orders):
        """Populate the archive table with orders"""
        self.archived_boards_table.clearContents()
        self.archived_table.setRowCount(0)
        
        try:
            archived_orders = self.db_manager.get_archived_orders()
            if not archived_orders:
                return 
            
            
            for row_idx, order in enumerate(archived_orders):
                self.archived_table.insertRow(row_idx)
                order_id, order_number, company_id, board_id, status, file_path, created_at, created_by = order

                if status != "Archived":
                    continue

                self.archived_table.setItem(row_idx, 0, QTableWidgetItem(str(order_id)))
                self.archived_table.setItem(row_idx, 1, QTableWidgetItem(order_number))
                self.archived_table.setItem(row_idx, 2, QTableWidgetItem(str(company_id)))
                self.archived_table.setItem(row_idx, 3, QTableWidgetItem(str(board_id)))
                self.archived_table.setItem(row_idx, 4, QTableWidgetItem(status))
                self.archived_table.setItem(row_idx, 5, QTableWidgetItem(file_path))
                self.archived_table.setItem(row_idx, 6, QTableWidgetItem(created_at))
                self.archived_table.setItem(row_idx, 7, QTableWidgetItem(str(created_by)))

                
        except Exception as e:
            logger.error(f"Failed to populate archive table: {e}", exc_info=True)
        finally:
            # Adjust row heights to fit content
            try:
                fm = self.archived_table.fontMetrics()
                default_h = int(fm.height() * 1.3)
                if default_h < 20:
                    default_h = 20
                self.archived_table.verticalHeader().setDefaultSectionSize(default_h)
                self.archived_table.resizeRowsToContents()
            except Exception:
                pass

    def populate_archived_boards(self):
        """Populate archived boards table"""
        try:
            self.archived_boards_table.setRowCount(0)
            companies = {c[0]: c[1] for c in self.db_manager.get_companies()}
            row_idx = 0
            for company_id, company_name in companies.items():
                boards = self.db_manager.get_boards_by_company(company_id)
                for b in boards:
                    board_id = b[0]
                    board_name = b[1]
                    archived = b[2] if len(b) > 2 else 0
                    if archived:
                        self.archived_boards_table.insertRow(row_idx)
                        self.archived_boards_table.setItem(row_idx, 0, QTableWidgetItem(str(board_id)))
                        self.archived_boards_table.setItem(row_idx, 1, QTableWidgetItem(board_name))
                        self.archived_boards_table.setItem(row_idx, 2, QTableWidgetItem(company_name))
                        row_idx += 1
        except Exception as e:
            logger.error(f"Failed to populate archived boards: {e}", exc_info=True)
        finally:
            try:
                fm = self.archived_boards_table.fontMetrics()
                default_h = int(fm.height() * 1.3)
                if default_h < 18:
                    default_h = 18
                self.archived_boards_table.verticalHeader().setDefaultSectionSize(default_h)
                self.archived_boards_table.resizeRowsToContents()
            except Exception:
                pass

    def populate_archived_companies(self):
        """Populate archived companies table"""
        try:
            self.archived_companies_table.setRowCount(0)
            companies = self.db_manager.get_companies_all(include_archived=True)
            row_idx = 0
            for c in companies:
                company_id = c[0]
                company_name = c[1]
                client_path = c[2] if len(c) > 2 else ""
                archived_flag = c[4] if len(c) > 4 else 0
                if archived_flag:
                    self.archived_companies_table.insertRow(row_idx)
                    self.archived_companies_table.setItem(row_idx, 0, QTableWidgetItem(str(company_id)))
                    self.archived_companies_table.setItem(row_idx, 1, QTableWidgetItem(company_name))
                    self.archived_companies_table.setItem(row_idx, 2, QTableWidgetItem(client_path))
                    row_idx += 1
        except Exception as e:
            logger.error(f"Failed to populate archived companies: {e}", exc_info=True)
        finally:
            try:
                fm = self.archived_companies_table.fontMetrics()
                default_h = int(fm.height() * 1.3)
                if default_h < 18:
                    default_h = 18
                self.archived_companies_table.verticalHeader().setDefaultSectionSize(default_h)
                self.archived_companies_table.resizeRowsToContents()
            except Exception:
                pass

    def get_selected_order_id(self):
        row = self.archived_table.currentRow()
        if row < 0:
            return None
        try:
            return int(self.archived_table.item(row, 0).text())
        except Exception:
            return None

    def restore_selected_order(self):
        order_id = self.get_selected_order_id()
        if not order_id:
            QMessageBox.warning(self, "No selection", "Please select an order to restore.")
            return
        try:
            self.db_manager.unarchive_order(order_id)
            QMessageBox.information(self, "Restored", "Order restored successfully.")
            self.load_all_orders()
        except Exception as e:
            logger.error(f"Failed to restore order: {e}")
            QMessageBox.critical(self, "Error", f"Failed to restore order: {e}")

    def delete_selected_order_permanently(self):
        order_id = self.get_selected_order_id()
        if not order_id:
            QMessageBox.warning(self, "No selection", "Please select an order to delete permanently.")
            return
        ok = QMessageBox.question(self, "Confirm Permanent Delete",
                                  "This will permanently delete the order and cannot be undone. Are you sure?",
                                  QMessageBox.Yes | QMessageBox.No)
        if ok != QMessageBox.Yes:
            return
        try:
            self.db_manager.delete_order_permanently(order_id)
            QMessageBox.information(self, "Deleted", "Order permanently deleted.")
            self.load_all_orders()
        except Exception as e:
            logger.error(f"Failed to permanently delete order: {e}")
            QMessageBox.critical(self, "Error", f"Failed to permanently delete order: {e}")

    def restore_selected_board(self):
        row = self.archived_boards_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Please select an archived board first.")
            return
        board_id = int(self.archived_boards_table.item(row, 0).text())
        try:
            self.db_manager.unarchive_board(board_id)
            QMessageBox.information(self, "Restored", "Board restored successfully.")
            self.refresh_company_tree()
            self.refresh_dropdowns()
            self.load_all_orders()
        except Exception as e:
            logger.error(f"Failed to restore board: {e}")
            QMessageBox.critical(self, "Error", f"Failed to restore board: {e}")

    def delete_selected_board_permanently(self):
        row = self.archived_boards_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Please select an archived board first.")
            return
        board_id = int(self.archived_boards_table.item(row, 0).text())
        confirm = QMessageBox.question(self, "Confirm Permanent Delete", 
                                       "This will permanently delete the board and cannot be undone. Continue?", 
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm != QMessageBox.Yes:
            return
        try:
            self.db_manager.delete_board_permanently(board_id)
            QMessageBox.information(self, "Deleted", "Board permanently deleted.")
            self.refresh_company_tree()
            self.refresh_dropdowns()
            self.load_all_orders()
        except Exception as e:
            logger.error(f"Failed to permanently delete board: {e}")
            QMessageBox.critical(self, "Error", f"Failed to delete board: {e}")

    def restore_selected_company(self):
        row = self.archived_companies_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Please select an archived company first.")
            return
        try:
            company_id = int(self.archived_companies_table.item(row, 0).text())
        except Exception:
            QMessageBox.warning(self, "Error", "Invalid company selection.")
            return

        try:
            self.db_manager.unarchive_company(company_id)
            QMessageBox.information(self, "Restored", "Company restored successfully.")
            self.refresh_company_tree()
            self.refresh_dropdowns()
            self.load_all_orders()
        except Exception as e:
            logger.error(f"Failed to restore company: {e}")
            QMessageBox.critical(self, "Error", f"Failed to restore company: {e}")

    def delete_selected_company_permanently(self):
        row = self.archived_companies_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Please select an archived company first.")
            return
        try:
            company_id = int(self.archived_companies_table.item(row, 0).text())
        except Exception:
            QMessageBox.warning(self, "Error", "Invalid company selection.")
            return

        confirm = QMessageBox.question(self, "Confirm Permanent Delete", 
                                       "This will permanently delete the company and all associated boards and orders. This cannot be undone. Continue?", 
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm != QMessageBox.Yes:
            return

        try:
            self.db_manager.delete_company_permanently(company_id)
            QMessageBox.information(self, "Deleted", "Company permanently deleted.")
            self.refresh_company_tree()
            self.refresh_dropdowns()
            self.load_all_orders()
        except Exception as e:
            logger.error(f"Failed to permanently delete company: {e}")
            QMessageBox.critical(self, "Error", f"Failed to delete company: {e}")

    def load_awaiting_confirmation_orders(self):
        """Load all orders with calculated status"""
        try:
            self.await_table.setRowCount(0)
            orders = self.db_manager.get_orders()

            companies = {c[0]: c[1] for c in self.db_manager.get_companies()}
            boards = {}
            for company_id in companies:
                for b in self.db_manager.get_boards_by_company(company_id):
                    board_id = b[0]
                    board_name = b[1]
                    boards[board_id] = board_name

            row_idx = 0
            for order in orders:
                order_id, order_number, company_id, board_id, db_status, file_path, created_at, created_by = order

                # Skip archived orders
                if db_status == 'Archived':
                    continue
                
                # Calculate actual status from file
                status_str, pass_count, fail_count, pending_count, total_count = self.calculate_order_status(file_path)

                company_name = companies.get(company_id, "Unknown")
                board_name = boards.get(board_id, "N/A") if board_id else "N/A"

                self.await_table.insertRow(row_idx)
                self.await_table.setItem(row_idx, 0, QTableWidgetItem(str(order_id)))
                self.await_table.setItem(row_idx, 1, QTableWidgetItem(order_number))
                self.await_table.setItem(row_idx, 2, QTableWidgetItem(company_name))
                self.await_table.setItem(row_idx, 3, QTableWidgetItem(board_name))

                # Color code status
                status_item = QTableWidgetItem(status_str)
                if status_str == "Complete":
                    status_item.setForeground(QColor("green"))
                    status_item.setFont(QFont("", weight=QFont.Bold))
                elif status_str == "Active":
                    status_item.setForeground(QColor("#ccc"))
                    status_item.setFont(QFont("", weight=QFont.Bold))
                elif status_str == "Pending":
                    status_item.setForeground(QColor("orange"))
                    status_item.setFont(QFont("", weight=QFont.Bold))

                self.await_table.setItem(row_idx, 4, status_item)
                row_idx += 1

        except Exception as e:
            logger.error(f"Failed to load orders: {e}", exc_info=True)
        finally:
            try:
                self.await_table.resizeRowsToContents()
            except Exception:
                pass

    def get_selected_awaiting_order_id(self):
        row = self.await_table.currentRow()
        if row < 0:
            return None
        try:
            return int(self.await_table.item(row, 0).text())
        except Exception:
            return None

    def view_selected_awaiting_file(self):
        """Open the selected order's XLSX file"""
        row = self.await_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No selection", "Please select an order first.")
            return

        try:
            order_id = int(self.await_table.item(row, 0).text())
            orders = self.db_manager.get_orders()
            order = next((o for o in orders if o[0] == order_id), None)

            if not order or not order[5]:
                QMessageBox.warning(self, "No file", "Selected order has no file recorded.")
                return

            file_path = order[5]

            if os.path.exists(file_path):
                os.startfile(file_path)
            else:
                QMessageBox.warning(self, "File not found", f"File not found:\n{file_path}")
        except Exception as e:
            logger.error(f"Failed to open file: {e}")
            QMessageBox.warning(self, "Open Failed", f"Could not open file:\n{e}")
        
    def confirm_and_archive_selected(self):
        """Archive selected order (only enabled for Complete orders)"""
        row = self.await_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No selection", "Please select an order first.")
            return

        try:
            order_id = int(self.await_table.item(row, 0).text())
            order_number = self.await_table.item(row, 1).text()

            ok = QMessageBox.question(
                self, 
                "Confirm & Archive", 
                f"Archive order {order_number}?\n\nThis will mark it as complete.",
                QMessageBox.Yes | QMessageBox.No
            )

            if ok != QMessageBox.Yes:
                return

            self.db_manager.archive_order(order_id)
            QMessageBox.information(self, "Archived", "Order archived successfully.")
            self.load_awaiting_confirmation_orders()
            self.on_order_selected()  # Refresh details panel

        except Exception as e:
            logger.error(f"Failed to archive order: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to archive order:\n{e}")
    
    def calculate_order_status(self, file_path):
        """
        Calculate order status based on XLSX contents
        Returns: (status_string, pass_count, fail_count, pending_count, total_count)
        """
        if not file_path or not os.path.exists(file_path):
            return ("Unknown", 0, 0, 0, 0)

        try:
            wb = openpyxl.load_workbook(file_path, read_only=True)
            ws = wb.active

            pass_count = 0
            fail_count = 0
            pending_count = 0
            total_count = 0

            # Skip header row, start from row 2
            for row in ws.iter_rows(min_row=2, values_only=True):
                if not row or len(row) < 5:
                    continue
                
                total_count += 1
                status = str(row[4]).strip().lower() if row[4] else "pending"

                if status == "pass":
                    pass_count += 1
                elif status == "fail":
                    fail_count += 1
                else:
                    pending_count += 1

            wb.close()

            # Determine overall status
            if pending_count == total_count:
                status_str = "Pending"
            elif pass_count == total_count:
                status_str = "Complete"
            else:
                status_str = "Active"

            return (status_str, pass_count, fail_count, pending_count, total_count)

        except Exception as e:
            logger.error(f"Failed to calculate order status: {e}")
            return ("Error", 0, 0, 0, 0)
     
    def load_users(self):
        """Load all users from database"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT user_id, username, role FROM users")
                users = cursor.fetchall()
            
            self.user_table.setRowCount(0)
            for row_idx, (user_id, username, role) in enumerate(users):
                self.user_table.insertRow(row_idx)
                self.user_table.setItem(row_idx, 0, QTableWidgetItem(str(user_id)))
                self.user_table.setItem(row_idx, 1, QTableWidgetItem(username))
                self.user_table.setItem(row_idx, 2, QTableWidgetItem(role))
            
            logger.info(f"Loaded {len(users)} users")
            # Adjust users table rows to fit content
            try:
                fm = self.user_table.fontMetrics()
                default_h = int(fm.height() * 1.2)
                if default_h < 18:
                    default_h = 18
                self.user_table.verticalHeader().setDefaultSectionSize(default_h)
                self.user_table.resizeRowsToContents()
            except Exception:
                pass
            
        except Exception as e:
            logger.error(f"Failed to load users: {e}", exc_info=True)

    def add_user(self):
        """Add a new user to the database"""
        username = self.new_user_input.text().strip()
        password = self.new_user_password.text().strip()
        role = self.user_role_dropdown.currentText()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Enter username and password")
            return
        
        try:
            self.db_manager.add_user(username, password, role)
            logger.info(f"User added: {username} ({role})")
            QMessageBox.information(self, "Success", f"User '{username}' added successfully!")
            
            self.load_users()
            self.new_user_input.clear()
            self.new_user_password.clear()
            
        except Exception as e:
            logger.error(f"Failed to add user: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to add user:\n{str(e)}")

    def update_password(self):
        """Update password for selected user"""
        row = self.user_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Please select a user first.")
            return

        user_id = int(self.user_table.item(row, 0).text())
        username = self.user_table.item(row, 1).text()

        new_pass, ok = QInputDialog.getText(
            self, 
            "Update Password", 
            f"Enter new password for {username}:", 
            QLineEdit.Password
        )
        
        if ok and new_pass.strip():
            try:
                import hashlib
                pw_hash = hashlib.sha256(new_pass.encode()).hexdigest()
                
                with self.db_manager.get_connection() as conn:
                    conn.execute(
                        "UPDATE users SET password_hash=? WHERE user_id=?",
                        (pw_hash, user_id)
                    )
                    conn.commit()
                
                logger.info(f"Password updated for user: {username}")
                QMessageBox.information(self, "Success", f"Password updated for {username}")
                
            except Exception as e:
                logger.error(f"Failed to update password: {e}", exc_info=True)
                QMessageBox.critical(self, "Error", f"Failed to update password:\n{str(e)}")

    def delete_user(self):
        """Delete selected user"""
        row = self.user_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Please select a user first.")
            return
        
        user_id = int(self.user_table.item(row, 0).text())
        username = self.user_table.item(row, 1).text()
        
        if user_id == self.user_id:
            QMessageBox.warning(self, "Error", "You cannot delete your own account!")
            return
        
        confirm = QMessageBox.question(
            self,
            "Delete User",
            f"Delete user '{username}'?\n\nThis cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            try:
                with self.db_manager.get_connection() as conn:
                    conn.execute("DELETE FROM users WHERE user_id=?", (user_id,))
                    conn.commit()
                
                logger.info(f"User deleted: {username}")
                QMessageBox.information(self, "Success", "User deleted!")
                self.load_users()
                
            except Exception as e:
                logger.error(f"Failed to delete user: {e}", exc_info=True)
                QMessageBox.critical(self, "Error", f"Failed to delete user:\n{str(e)}")