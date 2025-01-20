from PySide6.QtWidgets import QToolBar
from PySide6.QtGui import QAction, QIcon
import os
from settings import BASE_DIR


class MainToolBar(QToolBar):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Toolbar")
        self.setMovable(False)

        self.icons_path = os.path.join(BASE_DIR, "assets", "icons")

        self.add_tool(text="Salvar Configurações", icon_path=os.path.join(self.icons_path, "save.png"), callback=self.save_configs)

    def add_tool(self, text, icon_path, callback):
        """Add tool to a toolbar"""
        if not os.path.exists(icon_path):
            print(f"Ícone não encontrado: {icon_path}")
            return
        action = QAction(QIcon(icon_path), text, self)
        action.triggered.connect(callback)
        self.addAction(action)

    def new_action(self):
        print("Nova ação!!")
        
    def save_configs(self):
        pass
