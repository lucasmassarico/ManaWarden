from PySide6.QtGui import QAction, QIcon
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QToolBar, QDialog, QLabel, QComboBox, QPushButton, QVBoxLayout, QSpinBox, QHBoxLayout
import os
from settings import BASE_DIR


class MainToolbar(QToolBar):
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)

        self.setMovable(False)
        self.main_window = main_window

        self.icons_path = os.path.join(BASE_DIR, "assets", "icons")

        self.add_tool(text="Salvar Configurações", icon_path=os.path.join(self.icons_path, "save.png"), callback=self.new_action_example)
        self.add_tool(text="Nova ação", icon_path=os.path.join(self.icons_path, "new.png"), callback=self.create_new_action)

    def add_tool(self, text, icon_path, callback):
        """Add tool to a bar"""
        action = QAction(QIcon(icon_path), text, self)
        action.triggered.connect(callback)
        self.addAction(action)

    def create_new_action(self):
        """Create a new action in MainWindow"""
        if self.main_window:
            # Criar a função na main window para criar a ação.
            select_action = NewActionModal()
            result = select_action.exec()

            if result == NewActionModal.Accepted:
                new_action = select_action.get_selected_action()

                if isinstance(new_action, int):
                    return None
                self.main_window.add_action_widget(new_action)

    @staticmethod
    def new_action_example():
        print("Nova ação!")


class NewActionModal(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Action")
        self.resize(400, 200)

        self.label = QLabel("Select the action")
        self.actions_combo = QComboBox()

        self.instance_number = QSpinBox()
        self.instance_number.setMinimum(1)
        self.instance_number.setMaximum(100)
        self.instance_number.setValue(1)

        self.select_button = QPushButton("Select")
        self.select_button.clicked.connect(self.accept)

        self._current_actions = ["", "Move Item", "Cast Spell", "Use Item"]

        centralized = Qt.AlignCenter

        self.horizontal_layout = QHBoxLayout()
        self.horizontal_layout.addWidget(self.actions_combo)
        self.horizontal_layout.addWidget(self.instance_number)

        layout = QVBoxLayout()
        layout.setAlignment(centralized)
        layout.addWidget(self.label, alignment=centralized)
        layout.addLayout(self.horizontal_layout)
        layout.addWidget(self.select_button, alignment=centralized)

        self.setLayout(layout)

        self.populate_actions_list()

    def populate_actions_list(self):
        self.actions_combo.clear()

        for item in self._current_actions:
            self.actions_combo.addItem(item)

    def get_selected_action(self):
        """Return the selected action"""
        current_selection = self.actions_combo.currentText().lower().replace(" ", "_")
        instance_number = self.instance_number.value()

        if current_selection == "":
            return 0

        return {
            "action": current_selection,
            "number": instance_number
        }
