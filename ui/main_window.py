import random

from PySide6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QTextEdit,
    QHBoxLayout,
    QWidget,
)
from ui.utils import generate_random_string, enable_dark_mode_window


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(generate_random_string(length=random.randint(4, 10)))
        self.resize(400, 300)

        # Layout principal
        main_layout = QVBoxLayout()

        # Botões com estados ativado/desativado
        self.move_rune_btn = QPushButton("Mover Blank Rune")
        self.cast_spell_btn = QPushButton("Lançar Spell")
        self.fish_btn = QPushButton("Pescar")
        self.eat_btn = QPushButton("Comer Comida")

        # Configuração de botões
        self.configure_button(self.move_rune_btn)
        self.configure_button(self.cast_spell_btn)
        self.configure_button(self.fish_btn)
        self.configure_button(self.eat_btn)

        # Campos para tempo
        self.cast_spell_time = QLineEdit()
        self.cast_spell_time.setPlaceholderText("Tempo (s)")
        self.cast_spell_time.setMaximumWidth(100)

        self.eat_time = QLineEdit()
        self.eat_time.setPlaceholderText("Tempo (s)")
        self.eat_time.setMaximumWidth(100)

        # Layouts para botões com campos
        spell_layout = QHBoxLayout()
        spell_layout.addWidget(self.cast_spell_btn)
        spell_layout.addWidget(self.cast_spell_time)

        eat_layout = QHBoxLayout()
        eat_layout.addWidget(self.eat_btn)
        eat_layout.addWidget(self.eat_time)

        # Logs
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)

        # Adicionar ao layout
        main_layout.addWidget(self.move_rune_btn)
        main_layout.addLayout(spell_layout)
        main_layout.addWidget(self.fish_btn)
        main_layout.addLayout(eat_layout)
        main_layout.addWidget(self.log_output)

        # Container principal
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Ativar Dark Mode
        self.setPalette(enable_dark_mode_window())

    def configure_button(self, button):
        """Configura o comportamento do botão com mudança de estado visual."""
        button.setCheckable(True)
        button.clicked.connect(lambda: self.toggle_button_state(button))
        button.setStyleSheet(self.get_button_style(False))

    def toggle_button_state(self, button):
        """Altera a aparência do botão com base no estado ativado/desativado."""
        is_active = button.isChecked()
        button.setStyleSheet(self.get_button_style(is_active))

    @staticmethod
    def get_button_style(is_active):
        """Retorna o estilo CSS do botão com base no estado."""
        if is_active:
            return """
            QPushButton {
                background-color: #4CAF50; /* Verde */
                color: white;
                border: 2px solid #4CAF50;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:pressed {
                background-color: #45a049;
            }
            """
        else:
            return """
            QPushButton {
                background-color: #f44336; /* Vermelho */
                color: white;
                border: 2px solid #f44336;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:pressed {
                background-color: #e53935;
            }
            """
