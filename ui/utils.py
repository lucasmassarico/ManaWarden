import random
import string
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt


def generate_random_string(length=10):
    characters = string.ascii_letters + string.digits
    random_string = "".join(random.choice(characters) for _ in range(length))
    return random_string


def enable_dark_mode_window():
    app_palette = QPalette()

    # Background geral
    app_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    app_palette.setColor(QPalette.WindowText, Qt.white)

    # Widgets interativos
    app_palette.setColor(QPalette.Base, QColor(42, 42, 42))
    app_palette.setColor(QPalette.AlternateBase, QColor(66, 66, 66))
    app_palette.setColor(QPalette.ToolTipBase, Qt.white)
    app_palette.setColor(QPalette.ToolTipText, Qt.white)
    app_palette.setColor(QPalette.Text, Qt.white)
    app_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    app_palette.setColor(QPalette.ButtonText, Qt.white)

    # Links
    app_palette.setColor(QPalette.Link, QColor(42, 130, 218))

    # Highlight
    app_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    app_palette.setColor(QPalette.HighlightedText, Qt.black)

    return app_palette
