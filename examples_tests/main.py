import ctypes
import time
import keyboard
import threading
from hex_codes import WM_MOUSEMOVE, MK_LBUTTON, WM_LBUTTONDOWN, WM_LBUTTONUP, WM_RBUTTONUP, WM_RBUTTONDOWN
from ctypes import wintypes

hwnd = ctypes.windll.user32.FindWindowW(0, "Miracle 7.4 - Niih")


BlockInput = ctypes.windll.user32.BlockInput
BlockInput.argtypes = [wintypes.BOOL]
BlockInput.restype = wintypes.BOOL


def is_window_foreground(hwnd):
    foreground_hwnd = ctypes.windll.user32.GetForegroundWindow()
    return hwnd == foreground_hwnd


def moveTo(hwnd, x: int, y: int):
    lParam = (y << 16) | x
    ctypes.windll.user32.PostMessageW(hwnd, WM_MOUSEMOVE, MK_LBUTTON, lParam)


def click(hwnd, x: int, y: int, button="left"):
    lParam = (y << 16) | x
    if button == "left":
        ctypes.windll.user32.SendMessageW(hwnd, WM_LBUTTONDOWN, 1, lParam)
        time.sleep(0.1)
        ctypes.windll.user32.SendMessageW(hwnd, WM_LBUTTONUP, 0, lParam)
        return
    ctypes.windll.user32.SendMessageW(hwnd, WM_RBUTTONDOWN, 1, lParam)
    time.sleep(0.1)
    ctypes.windll.user32.SendMessageW(hwnd, WM_RBUTTONUP, 1, lParam)


keyboard.wait("b")
while True:
    if not is_window_foreground(hwnd):
        print("Em outra janela")
        moveTo(hwnd, 954, 561)
        time.sleep(0.2)
        click(hwnd, 954, 561, "right")
    else:
        blocked = BlockInput(True)
        if blocked:
            try:
                time.sleep(0.1)
                moveTo(hwnd, 954, 561)
                time.sleep(0.1)
                click(hwnd, 954, 561, "right")
                time.sleep(0.1)
            finally:
                unblocked = BlockInput(False)
                time.sleep(2)
        else:
            raise RuntimeError("Input is already blocked by another thread!")
