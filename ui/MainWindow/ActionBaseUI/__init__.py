from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QPushButton, QGroupBox, QWidget
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from abc import abstractmethod
from ui.MainWindow.ShortcutDialog import ShortcutDialog
from ui.MainWindow.ActionBaseUI.ActionConfigDialog import MoveItemConfigDialog, CastSpellConfigDialog, UseItemConfigDialog
from automation.actions import MoveItemAction, CastSpellAction, UseItemAction
from process_manager import ProcessManager
from utils import LogManager
import keyboard


class ActionWidget(QWidget):
    def __init__(self, action_data, parent=None):
        super().__init__(parent)
        self.action_data = action_data

        self.action = None

        self.logger = LogManager()
        self.process_manager = ProcessManager()

        self.shortcut = None

        self.setup_ui()

    @abstractmethod
    def setup_ui(self):
        pass

    def open_shortcut_dialog(self, button):
        dialog = ShortcutDialog(self)
        if dialog.exec() == ShortcutDialog.Accepted:
            self.shortcut = dialog.get_shortcut()
            if self.shortcut:
                font = QFont()
                font.setPointSize(15)
                button.setFont(font)
                button.setText(self.shortcut)
                keyboard.on_press_key(self.shortcut, lambda _: self.execute_action())

                button.setStyleSheet("color: green; font-weight: 700")
            else:
                button.setStyleSheet("color: red; font-weight: 700")

    def execute_action(self):
        self.action.execute()


class MoveItemUI(ActionWidget):
    def setup_ui(self):
        action_name = f"M.V.{self.action_data['number']}"

        self.action = MoveItemAction(instance_n=self.action_data['number'])

        # Header Layout
        header_layout = QHBoxLayout()
        name_label = QLabel(action_name)
        description_input = QLineEdit()
        description_input.setPlaceholderText("Description")
        description_input.setFixedWidth(100)
        header_layout.addWidget(name_label)
        header_layout.addWidget(description_input)
        header_layout.addStretch()

        # Action Layout
        action_layout = QHBoxLayout()
        shortcut_button = QPushButton("Set Shortcut")
        shortcut_button.setFixedSize(100, 30)
        shortcut_button.clicked.connect(lambda: self.open_shortcut_dialog(shortcut_button))
        config_button = QPushButton("...")
        config_button.clicked.connect(self.open_config_dialog)
        config_button.setFixedHeight(30)
        action_layout.addWidget(shortcut_button)
        action_layout.addWidget(config_button)

        # Group Box
        action_group = QGroupBox()
        action_group.setLayout(action_layout)
        action_group.setFixedHeight(60)
        action_group.setMinimumWidth(300)

        # Wrapper Layout
        wrapper_layout = QVBoxLayout()
        wrapper_layout.addLayout(header_layout)
        wrapper_layout.addWidget(action_group)

        # Set Layout for the Widget
        self.setLayout(wrapper_layout)

    def open_config_dialog(self):
        dialog = MoveItemConfigDialog(self, action_instance=self.action)
        dialog.exec()


class CastSpellUI(ActionWidget):
    def setup_ui(self):
        action_name = f"C.S.{self.action_data['number']}"

        self.action = CastSpellAction(instance_n=self.action_data['number'])

        # Header Layout
        header_layout = QHBoxLayout()
        name_label = QLabel(action_name)
        description_input = QLineEdit()
        description_input.setPlaceholderText("Description")
        description_input.setFixedWidth(100)
        header_layout.addWidget(name_label)
        header_layout.addWidget(description_input)
        header_layout.addStretch()

        # Action Layout
        action_layout = QHBoxLayout()
        shortcut_button = QPushButton("Set Shortcut")
        shortcut_button.setFixedSize(100, 30)
        shortcut_button.clicked.connect(lambda: self.open_shortcut_dialog(shortcut_button))
        config_button = QPushButton("...")
        config_button.clicked.connect(self.open_config_dialog)
        config_button.setFixedHeight(30)
        action_layout.addWidget(shortcut_button)
        action_layout.addWidget(config_button)

        # Group Box
        action_group = QGroupBox()
        action_group.setLayout(action_layout)
        action_group.setFixedHeight(60)
        action_group.setMinimumWidth(300)

        # Wrapper Layout
        wrapper_layout = QVBoxLayout()
        wrapper_layout.addLayout(header_layout)
        wrapper_layout.addWidget(action_group)

        # Set Layout for the Widget
        self.setLayout(wrapper_layout)

    def open_config_dialog(self):
        dialog = CastSpellConfigDialog(self, action_instance=self.action)
        dialog.exec()


class UseItemUI(ActionWidget):
    def setup_ui(self):
        action_name = f"U.I.{self.action_data['number']}"

        self.action = UseItemAction(instance_n=self.action_data['number'])

        # Header Layout
        header_layout = QHBoxLayout()
        name_label = QLabel(action_name)
        description_input = QLineEdit()
        description_input.setPlaceholderText("Description")
        description_input.setFixedWidth(100)
        header_layout.addWidget(name_label)
        header_layout.addWidget(description_input)
        header_layout.addStretch()

        # Action Layout
        action_layout = QHBoxLayout()
        shortcut_button = QPushButton("Set Shortcut")
        shortcut_button.setFixedSize(100, 30)
        shortcut_button.clicked.connect(lambda: self.open_shortcut_dialog(shortcut_button))
        config_button = QPushButton("...")
        config_button.clicked.connect(self.open_config_dialog)
        config_button.setFixedHeight(30)
        action_layout.addWidget(shortcut_button)
        action_layout.addWidget(config_button)

        # Group Box
        action_group = QGroupBox()
        action_group.setLayout(action_layout)
        action_group.setFixedHeight(60)
        action_group.setMinimumWidth(300)

        # Wrapper Layout
        wrapper_layout = QVBoxLayout()
        wrapper_layout.addLayout(header_layout)
        wrapper_layout.addWidget(action_group)

        # Set Layout for the Widget
        self.setLayout(wrapper_layout)

    def open_config_dialog(self):
        dialog = UseItemConfigDialog(self, action_instance=self.action)
        dialog.exec()