from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QDialogButtonBox, QLabel, QFormLayout,
    QGroupBox, QDoubleSpinBox, QPushButton, QSpinBox, QCheckBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFont
from process_manager import ScreenManager
from utils import ConfigManager
from settings import BASE_DIR
import os
from ui.MainWindow.ShortcutDialog import ShortcutDialog


class ActionConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Configure Action")
        self.setModal(True)
        self.setMinimumSize(300, 200)

        self.layout = QVBoxLayout(self)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.button_box.accepted.connect(self.save_config)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

    def save_config(self):
        """Method to save configs"""
        pass


class MoveItemConfigDialog(ActionConfigDialog):
    def __init__(self, parent=None, action_instance=None):
        super().__init__(parent)
        self.action_instance = action_instance

        self.setWindowTitle(f"Configure M.V.{self.action_instance.instance_n}")

        self.config_manager = ConfigManager()
        self.screen_manager = ScreenManager()

        # initial values
        self.move_item_path = ""
        self.move_item_threshold = 0.8
        self.destination_region = None
        self.delay = 0.08
        self.steps = 30

        # try to load existing configs
        self.load_config()

        # GroupBox for configurations
        move_item_group = QGroupBox("Item to Move", self)
        move_item_layout = QFormLayout()
        move_item_group.setLayout(move_item_layout)

        # move_item_path (img)
        self.move_item_label = QLabel()
        self.move_item_label.setAlignment(Qt.AlignCenter)
        self.move_item_label.setFixedSize(64, 64)
        self.move_item_label.setStyleSheet("border: 1px solid black")
        self.move_item_label.setCursor(Qt.PointingHandCursor)
        self.move_item_label.mousePressEvent = self.select_move_item_path
        self.update_image_label(self.move_item_label, self.move_item_path)
        move_item_layout.addRow("Move Item Path:", self.move_item_label)

        # move_item_threshold
        self.threshold_spin = QDoubleSpinBox()
        self.threshold_spin.setRange(0.0, 1.0)
        self.threshold_spin.setSingleStep(0.1)
        self.threshold_spin.setValue(self.move_item_threshold)
        move_item_layout.addRow("Threshold:", self.threshold_spin)

        # destination_region (button to select the region)
        self.destination_button = QPushButton("Select Destination Region")
        self.destination_button.clicked.connect(self.select_destination_region)
        move_item_layout.addRow("Destination Region:", self.destination_button)

        # delay (time in seconds)
        self.delay_spin = QDoubleSpinBox()
        self.delay_spin.setRange(0.01, 5.0)
        self.delay_spin.setSingleStep(0.01)
        self.delay_spin.setDecimals(2)
        self.delay_spin.setValue(self.delay)
        move_item_layout.addRow("Delay (seconds):", self.delay_spin)

        # steps (number of steps)
        self.steps_spin = QSpinBox()
        self.steps_spin.setRange(1, 30)
        self.steps_spin.setValue(self.steps)
        move_item_layout.addRow("Steps:", self.steps_spin)

        # Add the GroupBox to the layout from the parent class
        self.layout.insertWidget(0, move_item_group)  # Insert above the button box

    def select_move_item_path(self, event):
        """Select the image path of the item to be moved"""
        select_region = self.screen_manager.select_regions(
            title="Select Move Item",
            multiple=False,
            save_img=True,
            default_path=os.path.join(BASE_DIR, "assets", "templates"),
            filename=f"move_item_selected_{self.action_instance.instance_n}"
        )
        if select_region:
            self.move_item_path = os.path.join(BASE_DIR, "assets", "templates", f"move_item_selected_{self.action_instance.instance_n}.png")
            self.update_image_label(self.move_item_label, self.move_item_path)

    def select_destination_region(self):
        """Select the region to move item"""
        select_region = self.screen_manager.select_regions(
            title="Select Destination Region",
            multiple=False,
            save_img=False
        )
        if select_region:
            self.destination_region = select_region[0]

    @staticmethod
    def update_image_label(label: QLabel, image_path: str):
        """Update a QLabel with a new path image"""
        if image_path and os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                label.setPixmap(pixmap)
            else:
                label.setText("No Image")
        else:
            label.setText("No Image")

    def save_config(self):
        """Save configs of action"""
        self.action_instance.move_item_path = self.move_item_path
        self.action_instance.move_item_threshold = self.threshold_spin.value()
        self.action_instance.destination_region = self.destination_region
        self.action_instance.delay = self.delay_spin.value()
        self.action_instance.steps = self.steps_spin.value()

        # Salve as configurações no gerenciador de configurações
        self.config_manager.set(f"move_item_path_{self.action_instance.instance_n}", self.move_item_path)
        self.config_manager.set(f"move_item_threshold_{self.action_instance.instance_n}", self.threshold_spin.value())
        self.config_manager.set(f"destination_region_m_{self.action_instance.instance_n}", self.destination_region)
        self.config_manager.set(f"delay_m_{self.action_instance.instance_n}", round(self.delay_spin.value(), 2))
        self.config_manager.set(f"steps_m_{self.action_instance.instance_n}", self.steps_spin.value())

        self.accept()

    def load_config(self):
        """Load existing configuration for the action instance."""
        instance_n = self.action_instance.instance_n
        self.move_item_path = self.config_manager.get(f"move_item_path_{instance_n}", "")
        self.move_item_threshold = self.config_manager.get(key=f"move_item_threshold_{instance_n}", default=0.8)
        self.destination_region = self.config_manager.get(f"destination_region_m_{instance_n}", default=())
        self.delay = self.config_manager.get(f"delay_m_{instance_n}", 0.08)
        self.steps = self.config_manager.get(f"steps_m_{instance_n}", 30)


class CastSpellConfigDialog(ActionConfigDialog):
    def __init__(self, parent=None, action_instance=None):
        super().__init__(parent)
        self.action_instance = action_instance

        self.setWindowTitle(f"Configure C.S.{self.action_instance.instance_n}")

        self.config_manager = ConfigManager()

        self.hotkey_to_cast = None

        self.load_config()

        # GroupBox for configurations
        cast_spell_group = QGroupBox("Hotkey in game to cast", self)
        cast_spell_layout = QFormLayout()
        cast_spell_group.setLayout(cast_spell_layout)

        # shortcut set button
        self.shortcut_button = QPushButton("Set hotkey")
        self.shortcut_button.setFixedSize(100, 30)
        self.shortcut_button.clicked.connect(lambda: self.open_hotkey_set(self.shortcut_button))
        cast_spell_layout.addRow("Set Hotkey", self.shortcut_button)

        self.layout.setAlignment(Qt.AlignCenter)
        self.layout.insertWidget(0, cast_spell_group)

    def open_hotkey_set(self, button):
        dialog = ShortcutDialog(self)
        if dialog.exec() == ShortcutDialog.Accepted:
            self.hotkey_to_cast = dialog.get_shortcut()
            if self.hotkey_to_cast:
                font = QFont()
                font.setPointSize(15)
                button.setFont(font)
                button.setText(self.hotkey_to_cast)

    def load_config(self):
        """Load existing configuration for the action instance."""
        instance_n = self.action_instance.instance_n
        self.hotkey_to_cast = self.config_manager.get(key=f"hotkey_to_cast_{instance_n}", default=None)

    def save_config(self):
        """Save configs of action"""""
        self.action_instance.hotkey_to_cast = self.hotkey_to_cast

        self.config_manager.set(key=f"hotkey_to_cast_{self.action_instance.instance_n}", value=self.hotkey_to_cast)

        self.accept()


class UseItemConfigDialog(ActionConfigDialog):
    def __init__(self, parent=None, action_instance=None):
        super().__init__(parent)
        self.action_instance = action_instance

        self.setWindowTitle(f"Configure U.I.{self.action_instance.instance_n}")

        self.config_manager = ConfigManager()
        self.screen_manager = ScreenManager()

        # Valores iniciais
        self.use_item = 0
        self.item_path = ""
        self.item_threshold = 0.8
        self.destination_region = None
        self.delay = 0.08

        # Tenta carregar configs existentes
        self.load_config()

        # Agrupador para configurações
        use_item_group = QGroupBox("Item to Select", self)
        use_item_layout = QFormLayout()
        use_item_group.setLayout(use_item_layout)

        # item_path (imagem do item)
        self.item_label = QLabel()
        self.item_label.setAlignment(Qt.AlignCenter)
        self.item_label.setFixedSize(64, 64)
        self.item_label.setStyleSheet("border: 1px solid black")
        self.item_label.setCursor(Qt.PointingHandCursor)
        self.item_label.mousePressEvent = self.select_item_path
        self.update_image_label(self.item_label, self.item_path)
        use_item_layout.addRow("Item Path:", self.item_label)

        # item_threshold
        self.threshold_spin = QDoubleSpinBox()
        self.threshold_spin.setRange(0.0, 1.0)
        self.threshold_spin.setSingleStep(0.1)
        self.threshold_spin.setValue(self.item_threshold)
        use_item_layout.addRow("Threshold:", self.threshold_spin)

        # use_item (0 ou 1) - pode ser CheckBox
        self.use_item_checkbox = QCheckBox("Use item after selecting?")
        self.use_item_checkbox.setChecked(bool(self.use_item))
        use_item_layout.addRow("Use Item:", self.use_item_checkbox)

        # destination_region (botão para selecionar região)
        self.destination_button = QPushButton("Select Destination Region")
        self.destination_button.clicked.connect(self.select_destination_region)
        use_item_layout.addRow("Destination Region:", self.destination_button)

        # delay (tempo em segundos)
        self.delay_spin = QDoubleSpinBox()
        self.delay_spin.setRange(0.01, 5.0)
        self.delay_spin.setSingleStep(0.01)
        self.delay_spin.setDecimals(2)
        self.delay_spin.setValue(self.delay)
        use_item_layout.addRow("Delay (seconds):", self.delay_spin)

        # Adiciona o GroupBox ao layout da classe pai
        self.layout.insertWidget(0, use_item_group)

    def select_item_path(self, event):
        """Selecionar a imagem do item"""
        select_region = self.screen_manager.select_regions(
            title="Select Item Image",
            multiple=False,
            save_img=True,
            default_path=os.path.join(BASE_DIR, "assets", "templates"),
            filename=f"use_item_selected_{self.action_instance.instance_n}"
        )
        if select_region:
            self.item_path = os.path.join(BASE_DIR, "assets", "templates", f"use_item_selected_{self.action_instance.instance_n}.png")
            self.update_image_label(self.item_label, self.item_path)

    def select_destination_region(self):
        """Selecionar a região destino"""
        select_region = self.screen_manager.select_regions(
            title="Select Destination Region",
            multiple=False,
            save_img=False
        )
        if select_region:
            self.destination_region = select_region[0]

    @staticmethod
    def update_image_label(label: QLabel, image_path: str):
        """Atualizar o QLabel com nova imagem"""
        if image_path and os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                label.setPixmap(pixmap)
            else:
                label.setText("No Image")
        else:
            label.setText("No Image")

    def save_config(self):
        """Salvar configurações da ação"""
        self.use_item = 1 if self.use_item_checkbox.isChecked() else 0
        self.item_threshold = self.threshold_spin.value()
        self.delay = round(self.delay_spin.value(), 2)

        # Salva no action_instance
        self.action_instance.use_item = self.use_item
        self.action_instance.item_path = self.item_path
        self.action_instance.item_threshold = self.item_threshold
        self.action_instance.destination_region = self.destination_region
        self.action_instance.delay = self.delay

        # Salva no config_manager
        instance_n = self.action_instance.instance_n
        self.config_manager.set(f"use_item_{instance_n}", self.use_item)
        self.config_manager.set(f"item_path_{instance_n}", self.item_path)
        self.config_manager.set(f"item_threshold_{instance_n}", self.item_threshold)
        self.config_manager.set(f"destination_region_{instance_n}", self.destination_region)
        self.config_manager.set(f"delay_{instance_n}", self.delay)

        self.accept()

    def load_config(self):
        """Carrega configurações existentes para a ação."""
        instance_n = self.action_instance.instance_n
        self.use_item = self.config_manager.get(key=f"use_item_{instance_n}", default=0)
        self.item_path = self.config_manager.get(key=f"item_path_{instance_n}", default="")
        self.item_threshold = self.config_manager.get(key=f"item_threshold_{instance_n}", default=0.8)
        self.destination_region = self.config_manager.get(key=f"destination_region_{instance_n}", default=None)
        self.delay = self.config_manager.get(key=f"delay_{instance_n}", default=0.08)
