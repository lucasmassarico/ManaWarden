import os
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QCursor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QDoubleSpinBox, QGroupBox, QFormLayout
)

from process_manager import ScreenManager
from utils import ConfigManager


class FishingActionConfigWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.config_manager = ConfigManager()
        self.screen_manager = ScreenManager()

        # Valores iniciais (serão substituídos via set_values)
        self.fishing_rod_path = ""
        self.water_path = ""
        self.fishing_rod_threshold = 0.5
        self.water_threshold = 0.8

        # Criação do group box
        fishing_group = QGroupBox("Configurações de Pesca (FishAction)", self)
        self.fishing_layout = QFormLayout(fishing_group)

        # fishing_rod_path (imagem)
        self.fishing_rod_label = QLabel()
        self.fishing_rod_label.setFixedSize(64, 64)
        self.fishing_rod_label.setStyleSheet("border: 1px solid black;")
        self.fishing_rod_label.setCursor(QCursor(Qt.PointingHandCursor))
        self.fishing_rod_label.mousePressEvent = self.select_fishing_rod_path
        self.fishing_layout.addRow("Fishing Rod Path:", self.fishing_rod_label)

        # water_path (imagem)
        self.water_label = QLabel()
        self.water_label.setFixedSize(64, 64)
        self.water_label.setStyleSheet("border: 1px solid black;")
        self.water_label.setCursor(QCursor(Qt.PointingHandCursor))
        self.water_label.mousePressEvent = self.select_water_path
        self.fishing_layout.addRow("Water Path:", self.water_label)

        # fishing_rod_threshold e water_threshold
        self.rod_threshold_spin = QDoubleSpinBox()
        self.rod_threshold_spin.setRange(0.0, 1.0)
        self.rod_threshold_spin.setSingleStep(0.1)
        self.fishing_layout.addRow("Fishing Rod Threshold:", self.rod_threshold_spin)

        self.water_threshold_spin = QDoubleSpinBox()
        self.water_threshold_spin.setRange(0.0, 1.0)
        self.water_threshold_spin.setSingleStep(0.1)
        self.fishing_layout.addRow("Water Threshold:", self.water_threshold_spin)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(fishing_group)
        self.setLayout(main_layout)

    def set_values(self, values: dict):
        self.fishing_rod_path = values.get("fishing_rod_path", "")
        self.water_path = values.get("water_path", "")
        self.fishing_rod_threshold = values.get("fishing_rod_threshold", 0.5)
        self.water_threshold = values.get("water_threshold", 0.8)

        self.update_image_label(self.fishing_rod_label, self.fishing_rod_path)
        self.update_image_label(self.water_label, self.water_path)
        self.rod_threshold_spin.setValue(self.fishing_rod_threshold)
        self.water_threshold_spin.setValue(self.water_threshold)

    def update_image_label(self, label: QLabel, image_path: str):
        """Atualiza o QLabel com a imagem do caminho fornecido."""
        if image_path and os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                label.setPixmap(pixmap)
            else:
                label.setText("No Image")
        else:
            label.setText("No Image")

    def select_fishing_rod_path(self, event):
        selected_regions = self.screen_manager.select_regions(
            title="Selecione a região da Fishing Rod",
            multiple=False,
            save_img=True,
            default_path="./assets/templates",
            filename="fishing_rod_selected"
        )
        if selected_regions:
            self.fishing_rod_path = os.path.join("./assets/templates", "fishing_rod_selected.png")
            self.update_image_label(self.fishing_rod_label, self.fishing_rod_path)

    def select_water_path(self, event):
        selected_regions = self.screen_manager.select_regions(
            title="Selecione a região da Água",
            multiple=False,
            save_img=True,
            default_path="./assets/templates",
            filename="water_selected"
        )
        if selected_regions:
            self.water_path = os.path.join("./assets/templates", "water_selected.png")
            self.update_image_label(self.water_label, self.water_path)

    def get_values(self):
        return {
            "fishing_rod_path": self.fishing_rod_path,
            "water_path": self.water_path,
            "fishing_rod_threshold": self.rod_threshold_spin.value(),
            "water_threshold": self.water_threshold_spin.value(),
        }