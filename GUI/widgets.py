from PyQt5.QtWidgets import QLabel, QPushButton, QLineEdit
import GUI.styles as styles

def create_label(text: str) -> QLabel:
    label = QLabel(text)
    return label

def create_input(placeholder: str = "") -> QLineEdit:
    input_field = QLineEdit()
    input_field.setPlaceholderText(placeholder)
    input_field.setStyleSheet(styles.INPUT_STYLE)
    return input_field

def create_button(text: str) -> QPushButton:
    button = QPushButton(text)
    button.setStyleSheet(styles.BUTTON_STYLE)
    return button