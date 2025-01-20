from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QCursor
from PySide6.QtCore import Qt


class ImageShow(QLabel):
    def __init__(self, width=64, height=64, callback=None):
        super().__init__()

        self.width = width
        self.height = height

        self.setFixedSize(w=self.width, h=self.height)
        self.setStyleSheet("border: 1px solid black")
        self.setCursor(QCursor(Qt.PointingHandCursor))

        self.callback = callback

    def mousePressEvent(self, ev):
        if self.callback:
            self.callback(ev)
        super().mousePressEvent(ev)
