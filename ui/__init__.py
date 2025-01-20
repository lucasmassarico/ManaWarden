from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QGroupBox, QMessageBox, QCheckBox, QDialog, QDialogButtonBox
)

from process_manager import ScreenManager
from ui.fishing_action_widget import FishingActionConfigWidget
from ui.region_selection_widget import RegionSelectionWidget
from utils import ConfigManager
from ui.components_MainWindow import MainToolBar


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ManaWarden")

        self.config_manager = ConfigManager()
        self.screen_manager = ScreenManager()

        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)

        # Toolbar
        self.tool_bar = MainToolBar()
        self.addToolBar(self.tool_bar)

        # Widget para seleção de regiões
        self.region_selection_widget = RegionSelectionWidget()
        main_layout.addWidget(self.region_selection_widget)

        # Grupo de controle da pesca
        self.fishing_control_group = QGroupBox("Fish Action")
        fish_layout = QHBoxLayout(self.fishing_control_group)

        self.fish_checkbox = QCheckBox()
        # Por enquanto, a checkbox não faz nada além de existir
        fish_layout.addWidget(self.fish_checkbox)

        self.config_fish_button = QPushButton("Config. Fish")
        self.config_fish_button.clicked.connect(self.open_fishing_config_dialog)
        fish_layout.addWidget(self.config_fish_button)

        main_layout.addWidget(self.fishing_control_group)

        # Botão de salvar config
        save_button = QPushButton("Salvar Configurações")
        save_button.clicked.connect(self.save_config)
        main_layout.addWidget(save_button)

        self.setCentralWidget(central_widget)

        # Inicializa o dicionário de pesca com valores do config_manager
        self.fishing_values = {
            "fishing_rod_path": self.config_manager.get("fishing_rod_path", ""),
            "water_path": self.config_manager.get("water_path", ""),
            "fishing_rod_threshold": self.config_manager.get("fishing_rod_threshold", 0.5),
            "water_threshold": self.config_manager.get("water_threshold", 0.8),
        }

    def open_fishing_config_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Configurações de Pesca")
        layout = QVBoxLayout(dialog)

        # Cria o widget de configuração de pesca
        self.fishing_action_widget = FishingActionConfigWidget()
        # Atualiza o widget com valores atuais
        self.fishing_action_widget.set_values(self.fishing_values)
        layout.addWidget(self.fishing_action_widget)

        # Botões OK/Cancel do diálogo
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        if dialog.exec() == QDialog.Accepted:
            # Ao aceitar, atualizamos os valores
            self.fishing_values = self.fishing_action_widget.get_values()

    def save_config(self):
        # Obtém valores do widget de regiões
        region_values = self.region_selection_widget.get_values()

        # Salva no config_manager
        self.config_manager.set("fishing_rod_path", self.fishing_values["fishing_rod_path"])
        self.config_manager.set("water_path", self.fishing_values["water_path"])
        self.config_manager.set("fishing_rod_threshold", self.fishing_values["fishing_rod_threshold"])
        self.config_manager.set("water_threshold", self.fishing_values["water_threshold"])

        if region_values["panels_region"] is not None:
            self.config_manager.set("panels_region", region_values["panels_region"])
        if region_values["map_region"] is not None:
            self.config_manager.set("map_region", region_values["map_region"])

        QMessageBox.information(self, "Configurações", "Configurações salvas com sucesso!")
