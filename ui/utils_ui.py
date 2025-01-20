import random
import string
from PySide6.QtGui import QIcon, QPixmap, QPainter
from PySide6.QtSvg import QSvgRenderer


def generate_random_string(length=10):
    characters = string.ascii_letters + string.digits
    random_string = "".join(random.choice(characters) for _ in range(length))
    return random_string


def create_svg_icon(svg_path, width=32, height=32):
    pixmap = QPixmap(width, height)
    pixmap.fill()

    renderer = QSvgRenderer(svg_path)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()

    return QIcon(pixmap)
