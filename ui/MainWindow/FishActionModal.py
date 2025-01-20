from PySide6.QtWidgets import (
    QWidget, QGroupBox, QFormLayout
)
from settings import BASE_DIR
import os


class FishActionModal(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Fish Action")

        fishing_group = QGroupBox("Fish Configurations", self)
        self.fishing_layout = QFormLayout(fishing_group)

