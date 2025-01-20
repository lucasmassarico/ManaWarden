from PySide6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QPushButton, QGroupBox, QSpacerItem, QSizePolicy, QLineEdit, QLabel, QDialog, QFrame
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from ui.MainWindow.MainToolBar import MainToolbar
from ui.MainWindow.ShortcutDialog import ShortcutDialog
from ui.MainWindow.ActionBaseUI import MoveItemUI, CastSpellUI, UseItemUI
from ui.MainWindow.RegionSelectionWidget import RegionSelectionWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ManaWarden")
        self.resize(500, 400)

        central_widget = QWidget()
        self.main_layout = QVBoxLayout(central_widget)

        # select regions widget
        self.region_selection_widget = RegionSelectionWidget()
        self.main_layout.addWidget(self.region_selection_widget)

        # Add a horizontal line (divider)
        self.divider = QFrame()
        self.divider.setFrameShape(QFrame.HLine)
        self.divider.setFrameShadow(QFrame.Sunken)
        self.main_layout.addWidget(self.divider)

        self.main_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.toolbar = MainToolbar(main_window=self)
        self.addToolBar(self.toolbar)

        self.setCentralWidget(central_widget)

    def add_action_widget(self, action_data):
        if not action_data:
            return None

        actions_mapping = {
            "move_item": MoveItemUI,
            "cast_spell": CastSpellUI,
            "use_item": UseItemUI
        }

        actions_class = actions_mapping.get(action_data["action"])
        if not actions_class:
            raise ValueError(f"Unknown action type: {action_data['action']}")

        action_widget = actions_class(action_data, self)

        self.main_layout.insertWidget(self.main_layout.count() - 1, action_widget, alignment=Qt.AlignVCenter)
