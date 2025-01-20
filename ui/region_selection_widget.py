from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QGroupBox, QFormLayout, QMessageBox
)

from process_manager import ScreenManager
from utils import ConfigManager


class RegionSelectionWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.config_manager = ConfigManager()
        self.screen_manager = ScreenManager()

        self.panels_region = self.config_manager.get("panels_region", None)
        self.map_region = self.config_manager.get("map_region", None)

        region_group = QGroupBox("Configurações de Regiões")
        region_layout = QFormLayout(region_group)

        self.panels_button = QPushButton("Definir Panels Region")
        self.panels_button.clicked.connect(self.set_panels_region)

        self.map_button = QPushButton("Definir Map Region")
        self.map_button.clicked.connect(self.set_map_region)

        # Labels para exibir as regiões atuais
        self.panels_label = QLabel(str(self.panels_region))
        self.map_label = QLabel(str(self.map_region))

        region_layout.addRow("Panels Region:", self.panels_button)
        region_layout.addRow("Panels Region (Atual):", self.panels_label)

        region_layout.addRow("Map Region:", self.map_button)
        region_layout.addRow("Map Region (Atual):", self.map_label)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(region_group)
        self.setLayout(main_layout)

    def set_panels_region(self):
        selected_regions = self.screen_manager.select_regions(
            title="Selecione a(s) região(ões) do painel",
            multiple=True,
            save_img=False
        )
        if selected_regions:
            self.panels_region = selected_regions
            self.panels_label.setText(str(self.panels_region))
            QMessageBox.information(self, "Panels Region", f"Panels Region definido: {self.panels_region}")

    def set_map_region(self):
        selected_regions = self.screen_manager.select_regions(
            title="Selecione a região do mapa",
            multiple=False,
            save_img=False
        )
        if selected_regions:
            self.map_region = selected_regions
            self.map_label.setText(str(self.map_region))
            QMessageBox.information(self, "Map Region", f"Map Region definido: {self.map_region}")

    def get_values(self):
        return {
            "panels_region": self.panels_region,
            "map_region": self.map_region
        }
