# styles.py - Dark theme styles for Label Tracker

# Color palette
PRIMARY_COLOR = "#667eea"
PRIMARY_COLOR_HOVER = "#7b8fef"
PRIMARY_COLOR_PRESSED = "#5a6dd8"
SECONDARY_COLOR = "#764ba2"
BACKGROUND_DARK = "#0f1419"
BACKGROUND_MEDIUM = "#1a1a2e"
BACKGROUND_LIGHT = "#2a2a4e"
INPUT_BG = "#2b2240"
INPUT_BORDER = "#3a2f59"
INPUT_BORDER_FOCUS = "#8b6ef0"
ACCENT_COLOR = "#64b5f6"
SUCCESS_COLOR = "#4caf50"
DANGER_COLOR = "#f44336"
DANGER_COLOR_HOVER = "#da190b"
WARNING_COLOR = "#ff9800"
TEXT_PRIMARY = "#eee"
TEXT_SECONDARY = "#aaa"
TEXT_DISABLED = "#888"

# Typography
FONT_FAMILY = "Segoe UI"
FONT_SIZE = 12

# Main window style
WINDOW_STYLE = """
QWidget {
    background-color: #0f1419;
    color: #eee;
    font-family: 'Segoe UI';
    font-size: 12pt;
}
"""

# Input fields style (QLineEdit, QComboBox, QTextEdit)
INPUT_STYLE = """
QLineEdit, QComboBox, QTextEdit {
    padding: 12px;
    background-color: #2b2240;
    border: 2px solid #3a2f59;
    border-radius: 8px;
    color: #eee;
    min-height: 42px;
    font-size: 12pt;
}
QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
    border: 2px solid #8b6ef0;
}
QComboBox::drop-down {
    border: none;
}
QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #eee;
    width: 0;
    height: 0;
    margin-right: 10px;
}
"""

# Primary button style (gradient purple)
BUTTON_STYLE = """
QPushButton {
    padding: 12px 24px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #667eea, stop:1 #764ba2);
    border: none;
    border-radius: 6px;
    color: white;
    font-weight: bold;
    font-size: 12pt;
    min-height: 40px;
}
QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #7b8fef, stop:1 #8b5fb7);
}
QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #5a6dd8, stop:1 #664091);
}
QPushButton:disabled {
    background: #3a3a5e;
    color: #888;
}
"""

# Secondary button style (gray)
BUTTON_SECONDARY_STYLE = """
QPushButton {
    padding: 12px 24px;
    background: #3a3a5e;
    border: none;
    border-radius: 6px;
    color: #e6e6e6;
    font-weight: bold;
    font-size: 12pt;
    min-height: 40px;
}
QPushButton:hover {
    background: #4a4a6e;
}
QPushButton:pressed {
    background: #2a2a4e;
}
"""

# Danger button style (red)
BUTTON_DANGER_STYLE = """
QPushButton {
    padding: 12px 24px;
    background: #d32f2f;
    border: none;
    border-radius: 6px;
    color: white;
    font-weight: bold;
    font-size: 12pt;
    min-height: 40px;
}
QPushButton:hover {
    background: #f44336;
}
QPushButton:pressed {
    background: #b71c1c;
}
"""

# Link-style button (transparent)
BUTTON_LINK_STYLE = """
QPushButton {
    background: transparent;
    color: #8b6ef0;
    border: none;
    font-weight: bold;
    padding: 6px 12px;
    text-decoration: underline;
    min-height: 20px;
}
QPushButton:hover {
    color: #a88fff;
}
"""

# Logout button style
BUTTON_LOGOUT_STYLE = """
QPushButton {
    background: #f44336;
    padding: 10px 20px;
    border: none;
    border-radius: 6px;
    color: white;
    font-weight: bold;
    margin: 10px 20px;
}
QPushButton:hover {
    background: #da190b;
}
"""

# Table style
TABLE_STYLE = """
QTableWidget {
    background-color: #1a1a2e;
    alternate-background-color: #16213e;
    gridline-color: #2a2a4e;
    border: none;
}
QTableWidget::item {
    padding: 8px;
}
QTableWidget::item:selected {
    background-color: #667eea;
}
QHeaderView::section {
    background-color: #2a2a4e;
    padding: 10px;
    border: none;
    font-weight: bold;
    color: #64b5f6;
}
"""

# Tree widget style
TREE_STYLE = """
QTreeWidget {
    background-color: #1a1a2e;
    alternate-background-color: #16213e;
    border: none;
}
QTreeWidget::item {
    padding: 5px;
}
QTreeWidget::item:selected {
    background-color: #667eea;
}
"""

# Sidebar button style
SIDEBAR_BUTTON_STYLE = """
QPushButton {
    text-align: left;
    padding: 15px 20px;
    border: none;
    background-color: transparent;
    color: #ccc;
    font-size: 14pt;
    border-left: 4px solid transparent;
}
QPushButton:hover {
    background-color: #2a2a4e;
    color: white;
}
QPushButton:checked {
    background-color: #667eea;
    color: white;
    border-left: 4px solid #4caf50;
}
"""

# Sidebar container style
SIDEBAR_STYLE = """
QWidget {
    background-color: #1a1a2e;
    border-right: 2px solid #2a2a4e;
}
"""

# Combined stylesheet for entire app
FULL_APP_STYLE = WINDOW_STYLE + INPUT_STYLE + BUTTON_STYLE + TABLE_STYLE + TREE_STYLE