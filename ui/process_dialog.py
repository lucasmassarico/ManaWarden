import ctypes
import os
import sys

import win32api
import win32con
import win32gui
import win32process
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap, QImage
from PySide6.QtWidgets import (
    QMainWindow, QVBoxLayout, QLabel, QComboBox, QPushButton,
    QWidget, QMessageBox, QDialog
)

from process_manager import ProcessManager, ScreenManager


class ProcessSelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select a process")
        self.resize(300, 150)  # Ajuste do tamanho

        self.process_manager = ProcessManager()
        self.screen_manager = ScreenManager()

        # Criação dos widgets
        self.label = QLabel("Select a process")
        self.process_combo = QComboBox()
        self.select_button = QPushButton("Select")
        self.select_button.clicked.connect(self.accept)  # Confirma seleção

        # Layout para os widgets
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label, alignment=Qt.AlignCenter)
        layout.addWidget(self.process_combo, alignment=Qt.AlignCenter)
        layout.addWidget(self.select_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)

        # Popula a lista de processos
        self.populate_process_list()

    def populate_process_list(self):
        """Populate the combobox with active windows titles for the current user."""
        self.process_combo.clear()
        windows = []

        ignored_titles = [
            "Reprodutor Multimídia",
            "Calculadora",
            "WhatsApp",
            "NVIDIA GeForce Overlay",
            "Configurações",
            "Program Manager",
            "Microsoft Text Input Application",
        ]

        ignored_executables = [
            "explorer.exe",
            "nvcontainer.exe",
            "Spotify.exe",
            "Photoshop.exe",
            "Taskmgr.exe"
        ]

        def enum_window_titles(hwnd_intern, _):
            """Callback function to enumerate windows."""
            if win32gui.IsWindowVisible(hwnd_intern) and win32gui.GetWindowText(hwnd_intern):
                windows.append(hwnd_intern)

        win32gui.EnumWindows(enum_window_titles, None)

        if not windows:
            self.process_combo.addItem("Nenhum aplicativo ativo disponível")
            return

        for hwnd in windows:
            title = win32gui.GetWindowText(hwnd)
            pid = win32process.GetWindowThreadProcessId(hwnd)[1]

            if any(ignore in title for ignore in ignored_titles):
                continue

            try:
                # Obter caminho do executável
                process_handle = win32api.OpenProcess(
                    win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, pid
                )
                exe_path = win32process.GetModuleFileNameEx(process_handle, 0)
                win32api.CloseHandle(process_handle)

                # Ignorar executáveis específicos
                if any(exe.lower() in exe_path.lower() for exe in ignored_executables):
                    continue
            except Exception as e:
                print(f"Erro ao verificar executável para ignorar: {e}")

            icon = self.get_window_icon(hwnd)

            if icon:
                self.process_combo.addItem(QIcon(icon), f"{pid} - {title}")
            else:
                no_icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../assets/icons/noicon_32.png"))
                self.process_combo.addItem(QIcon(no_icon_path), f"{pid} - {title}")

    @staticmethod
    def get_window_icon(hwnd):
        """Retrieve the icon for the given window handle."""
        try:
            # Tentativa de capturar ícone pela janela
            hicon = win32gui.SendMessage(hwnd, win32con.WM_GETICON, win32con.ICON_SMALL, 0)
            if not hicon:
                hicon = win32gui.SendMessage(hwnd, win32con.WM_GETICON, win32con.ICON_BIG, 0)
            if not hicon:
                hicon = win32gui.GetClassLong(hwnd, win32con.GCL_HICON)

            if hicon:
                return ProcessSelectionDialog.icon_handle_to_pixmap(hicon)

            # Caso não consiga obter o ícone pela janela, tente pelo executável
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process_handle = win32api.OpenProcess(
                win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, pid
            )
            exe_path = win32process.GetModuleFileNameEx(process_handle, 0)
            win32api.CloseHandle(process_handle)

            if os.path.exists(exe_path):
                large_icons, small_icons = win32gui.ExtractIconEx(exe_path, 0)
                if small_icons:
                    return ProcessSelectionDialog.icon_handle_to_pixmap(small_icons[0])
                elif large_icons:
                    return ProcessSelectionDialog.icon_handle_to_pixmap(large_icons[0])

        except Exception as e:
            print(f"Erro ao capturar ícone: {e}")

        return None

    @staticmethod
    def icon_handle_to_pixmap(hicon):
        """Convert an HICON handle to QPixmap."""
        try:
            # Estruturas BITMAPINFO para criar um DIB
            class BITMAPINFOHEADER(ctypes.Structure):
                _fields_ = [
                    ("biSize", ctypes.c_uint32),
                    ("biWidth", ctypes.c_int32),
                    ("biHeight", ctypes.c_int32),
                    ("biPlanes", ctypes.c_uint16),
                    ("biBitCount", ctypes.c_uint16),
                    ("biCompression", ctypes.c_uint32),
                    ("biSizeImage", ctypes.c_uint32),
                    ("biXPelsPerMeter", ctypes.c_int32),
                    ("biYPelsPerMeter", ctypes.c_int32),
                    ("biClrUsed", ctypes.c_uint32),
                    ("biClrImportant", ctypes.c_uint32),
                ]

            class BITMAPINFO(ctypes.Structure):
                _fields_ = [
                    ("bmiHeader", BITMAPINFOHEADER),
                    ("bmiColors", ctypes.c_uint32 * 3),
                ]

            # Tamanho do ícone
            ICON_SIZE = 32
            hdc = win32gui.GetDC(0)
            memdc = ctypes.windll.gdi32.CreateCompatibleDC(hdc)

            # Criar DIB
            bmi = BITMAPINFO()
            bmi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
            bmi.bmiHeader.biWidth = ICON_SIZE
            bmi.bmiHeader.biHeight = -ICON_SIZE  # Valor negativo para orientá-lo corretamente
            bmi.bmiHeader.biPlanes = 1
            bmi.bmiHeader.biBitCount = 32
            bmi.bmiHeader.biCompression = 0  # BI_RGB
            bmi.bmiHeader.biSizeImage = 0

            dib = ctypes.windll.gdi32.CreateDIBSection(
                hdc, ctypes.byref(bmi), 0, ctypes.byref(ctypes.c_void_p()), None, 0
            )
            ctypes.windll.gdi32.SelectObject(memdc, dib)

            # Renderizar o ícone no DC de memória
            ctypes.windll.user32.DrawIconEx(memdc, 0, 0, hicon, ICON_SIZE, ICON_SIZE, 0, None, 3)

            # Criar um QImage com os dados do DIB
            data = ctypes.create_string_buffer(ICON_SIZE * ICON_SIZE * 4)
            ctypes.windll.gdi32.GetDIBits(hdc, dib, 0, ICON_SIZE, data, ctypes.byref(bmi), 0)

            image = QImage(data, ICON_SIZE, ICON_SIZE, QImage.Format_ARGB32)

            # Limpeza
            ctypes.windll.gdi32.DeleteObject(dib)
            ctypes.windll.gdi32.DeleteDC(memdc)
            win32gui.ReleaseDC(0, hdc)

            return QPixmap.fromImage(image)
        except Exception as e:
            print(f"Erro ao converter HICON para QPixmap: {e}")
            return None

    def select_process(self):
        """Handle process selection."""
        selected_process = self.process_combo.currentText()
        if selected_process and selected_process != "Nenhum aplicativo ativo disponível":
            try:
                pid, name = selected_process.split(" - ", 1)

                hwnd = self.process_manager.find_hWnd_by_name(name)
                if not hwnd:
                    raise ValueError(f"Not possible to find window for process '{name}'.")

                if name.lower() == "medivia":
                    self.process_manager.medivia = True

                self.process_manager.set_hwnd(hwnd)
                self.screen_manager.set_window_handle(hwnd)
                QMessageBox.information(
                    self, "Processo Selecionado",
                    f"Processo {name} (PID: {pid}) foi selecionado corretamente."
                )
                self.accept()  # Fecha o diálogo com sucesso

            except Exception as e:
                QMessageBox.critical(
                    self, "Erro ao anexar",
                    f"Erro ao selecionar o processo: {str(e)}"
                )
        else:
            QMessageBox.warning(self, "Seleção Inválida", "Selecione um processo válido!")

    def get_selected_process(self):
        """Return the currently selected process."""
        return self.process_combo.currentText()
