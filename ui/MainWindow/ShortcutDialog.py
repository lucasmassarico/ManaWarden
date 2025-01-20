from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox, QLineEdit
from PySide6.QtCore import Qt


class ShortcutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Set Shortcut")
        self.setModal(True)
        self.setFixedSize(300, 150)

        self.shortcut = None

        layout = QVBoxLayout(self)

        self.info_label = QLabel("Press the key combination you want to set.")
        self.info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.info_label)

        self.shortcut_display = QLineEdit(self)
        self.shortcut_display.setReadOnly(True)
        self.shortcut_display.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.shortcut_display)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def keyPressEvent(self, event):
        key = event.key()
        modifiers = event.modifiers()

        # Obtenha o nome do modificador
        mod_text = []
        if modifiers & Qt.ControlModifier:
            mod_text.append("Ctrl")
        if modifiers & Qt.ShiftModifier:
            mod_text.append("Shift")
        if modifiers & Qt.AltModifier:
            mod_text.append("Alt")
        if modifiers & Qt.MetaModifier:
            mod_text.append("Meta")

        # Obtenha o nome da tecla
        key_text = self.get_key_name(key)

        # Combine modificadores e tecla
        shortcut_text = "+".join(mod_text + [key_text]) if mod_text else key_text

        # Atualize o atalho e o campo de texto
        self.shortcut = shortcut_text
        self.shortcut_display.setText(shortcut_text)

    @staticmethod
    def get_key_name(key):
        """Map keys to readable names."""
        if key in qt_key_map:
            return qt_key_map[key]

        # Verifica se a tecla é imprimível (ASCII visível)
        if 32 <= key <= 126:
            return chr(key).upper()

        # Caso contrário, retorna um nome genérico para a tecla
        return f"Key_{key}"

    def get_shortcut(self):
        return self.shortcut


qt_key_map = {
    Qt.Key_F1: "F1",
    Qt.Key_F2: "F2",
    Qt.Key_F3: "F3",
    Qt.Key_F4: "F4",
    Qt.Key_F5: "F5",
    Qt.Key_F6: "F6",
    Qt.Key_F7: "F7",
    Qt.Key_F8: "F8",
    Qt.Key_F9: "F9",
    Qt.Key_F10: "F10",
    Qt.Key_F11: "F11",
    Qt.Key_F12: "F12",
    Qt.Key_Delete: "Delete",
    Qt.Key_Insert: "Insert",
    Qt.Key_Home: "Home",
    Qt.Key_End: "End",
    Qt.Key_PageUp: "PageUp",
    Qt.Key_PageDown: "PageDown",
    Qt.Key_Up: "ArrowUp",
    Qt.Key_Down: "ArrowDown",
    Qt.Key_Left: "ArrowLeft",
    Qt.Key_Right: "ArrowRight",
    Qt.Key_Escape: "Escape",
    Qt.Key_Tab: "Tab",
    Qt.Key_Backspace: "Backspace",
    Qt.Key_Return: "Enter",
    Qt.Key_Enter: "Enter",
    Qt.Key_Space: "Space",
    Qt.Key_Print: "PrintScreen",
    Qt.Key_CapsLock: "CapsLock",
    Qt.Key_NumLock: "NumLock",
    Qt.Key_ScrollLock: "ScrollLock",
}