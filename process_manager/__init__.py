import ctypes
import time
import cv2
from ctypes import windll
import threading
from process_manager.hex_codes import keys
from utils import LogManager
import numpy as np
import win32ui
import win32gui
import random
import ctypes.wintypes
from utils import LogManager
import keyboard
from pynput.keyboard import Key, Controller

SCREEN_WIDTH = ctypes.windll.user32.GetSystemMetrics(0)
SCREEN_HEIGHT = ctypes.windll.user32.GetSystemMetrics(1)

MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010


class MSG(ctypes.Structure):
    _fields_ = [
        ("hwnd", ctypes.wintypes.HWND),
        ("message", ctypes.wintypes.UINT),
        ("wParam", ctypes.wintypes.WPARAM),
        ("lParam", ctypes.wintypes.LPARAM),
        ("time", ctypes.wintypes.DWORD),
        ("pt", ctypes.wintypes.POINT)
    ]


class ProcessManager:
    # Singleton
    """A manager for interacting with a specific process using ctypes and Windows API."""
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ProcessManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.hWnd = None
        self._windll = ctypes.windll.user32

        self.medivia = False
        self.original_x = 0
        self.original_y = 0

        self.logger = LogManager()

    @staticmethod
    def _get_key(key_name):
        """Retrieve a key from the keys dictionary or raise an error if not found."""
        from process_manager.hex_codes import keys
        if key_name not in keys:
            raise KeyError(f"Key '{key_name}' not found in keys dictionary.")
        return keys[key_name]

    def is_foreground(self) -> bool:
        """Check if process window is currently in the foreground."""
        if not self.hWnd:
            raise ValueError("hWnd not defined.")

        foreground_hwnd = self._windll.GetForegroundWindow()

        return self.hWnd == foreground_hwnd

    def is_mouse_over_window(self) -> bool:
        """Check if the mouse is over the window, even if it's not in foreground."""
        if not self.hWnd:
            raise ValueError("hWnd not defined.")

        point = ctypes.wintypes.POINT()
        self._windll.GetCursorPos(ctypes.byref(point))

        hwnd_at_cursor = self._windll.WindowFromPoint(point)

        return hwnd_at_cursor == self.hWnd

    def is_minimized(self) -> bool:
        """Check if the application window is minimized."""
        if not self.hWnd:
            raise ValueError("hWnd not defined.")

        return self._windll.IsIconic(self.hWnd) != 0

    def find_hWnd_by_name(self, process_name: str):
        """Find hwnd of a process by its name."""
        handle = self._windll.FindWindowW(0, process_name)
        return handle

    def set_hwnd(self, hwnd):
        """Set hwnd for the target process"""
        self.hWnd = hwnd

    def get_hwnd(self):
        """Get the current hwnd"""
        return self.hWnd

    def send_key_to_window(self, scan_code):
        """Send a keyboard key to the process window."""
        lParam_down = (1 << 0) | (scan_code << 16)
        lParam_up = (1 << 0) | (scan_code << 16) | (1 << 30) | (1 << 31)
        self._windll.SendMessageW(self.hWnd, self._get_key("WM_KEYDOWN"), scan_code, lParam_down)
        time.sleep(0.15)
        self._windll.SendMessageW(self.hWnd, self._get_key("WM_KEYUP"), scan_code, lParam_up)

    def _save_mouse_position(self):
        """Save the current mouse position."""
        point = ctypes.wintypes.POINT()
        self._windll.GetCursorPos(ctypes.byref(point))
        return point.x, point.y

    def _restore_mouse_position(self, x, y):
        """Restore the mouse to a saved position."""
        self._windll.SetCursorPos(x, y)

    @staticmethod
    def _generate_lParam(x: int, y: int) -> int:
        """Generate lParam for mouse operations."""
        return int((y << 16) | x)

    def moveTo(self, x: int, y: int):
        """Move the mouse to the specified coordinates."""
        if self.medivia:
            self.original_x, self.original_y = self._save_mouse_position()
            self._windll.SetCursorPos(int(x), int(y+20))
            time.sleep(0.2)
        else:
            lParam = self._generate_lParam(x, y)
            self._windll.PostMessageW(self.hWnd, self._get_key("WM_MOUSEMOVE"), self._get_key("MK_LBUTTON"), lParam)
            time.sleep(0.015)

    def click(self, x: int, y: int, button="left"):
        """Simulate a mouse click at the given coordinates."""
        if self.medivia:
            # Create input structure for mouse click
            class MouseInput(ctypes.Structure):
                _fields_ = [("dx", ctypes.c_long),
                            ("dy", ctypes.c_long),
                            ("mouseData", ctypes.c_ulong),
                            ("dwFlags", ctypes.c_ulong),
                            ("time", ctypes.c_ulong),
                            ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]

            class Input(ctypes.Structure):
                class _InputUnion(ctypes.Union):
                    _fields_ = [("mi", MouseInput)]

                _anonymous_ = ("_input",)
                _fields_ = [("type", ctypes.c_ulong), ("_input", _InputUnion)]

            # Flags for mouse click
            if button == "left":
                down_flag = 0x0002  # MOUSEEVENTF_LEFTDOWN
                up_flag = 0x0004  # MOUSEEVENTF_LEFTUP
            else:
                down_flag = 0x0008  # MOUSEEVENTF_RIGHTDOWN
                up_flag = 0x0010  # MOUSEEVENTF_RIGHTUP

            # Create input events for the click
            inputs = (Input * 2)(
                Input(type=0, mi=MouseInput(dx=0, dy=0, mouseData=0, dwFlags=down_flag, time=0, dwExtraInfo=None)),
                Input(type=0, mi=MouseInput(dx=0, dy=0, mouseData=0, dwFlags=up_flag, time=0, dwExtraInfo=None))
            )

            # Send the input events
            ctypes.windll.user32.SendInput(len(inputs), ctypes.byref(inputs), ctypes.sizeof(Input))

            self._restore_mouse_position(self.original_x, self.original_y)
        else:
            # Use SendMessage for non-Medivia interactions
            lParam = self._generate_lParam(x, y)
            self.logger.log("debug", f"Attempting to click at ({x}, {y}) with lParam={lParam}")

            if button == "left":
                self._windll.SendMessageW(self.hWnd, self._get_key("WM_LBUTTONDOWN"), 1, lParam)
                time.sleep(0.015)
                self._windll.SendMessageW(self.hWnd, self._get_key("WM_LBUTTONUP"), 0, lParam)
            else:
                self._windll.SendMessageW(self.hWnd, self._get_key("WM_RBUTTONDOWN"), 0, lParam)
                time.sleep(0.015)
                self._windll.SendMessageW(self.hWnd, self._get_key("WM_RBUTTONUP"), 0, lParam)


    def perform_drag_and_drop(self, start_x: int, start_y: int, dest_x: int, dest_y: int, steps: int = 50, delay=0.01):
        """Simulate a drag-and-drop operation."""
        if not self.hWnd:
            raise ValueError("hWnd not defined. Use set_hwnd to set the window handle.")

        lParam_start = self._generate_lParam(start_x, start_y)
        self._windll.SendMessageW(self.hWnd, self._get_key("WM_LBUTTONDOWN"), self._get_key("MK_LBUTTON"), lParam_start)
        time.sleep(0.1)

        for i in range(steps):
            interp_x = int(start_x + (dest_x - start_x) * (i + 1) / steps)
            interp_y = int(start_y + (dest_y - start_y) * (i + 1) / steps)
            lParam_move = self._generate_lParam(interp_x, interp_y)
            self._windll.SendMessageW(self.hWnd, self._get_key("WM_MOUSEMOVE"), self._get_key("MK_LBUTTON"), lParam_move)
            time.sleep(delay)

        lParam_end = self._generate_lParam(dest_x, dest_y)
        self._windll.SendMessageW(self.hWnd, self._get_key("WM_LBUTTONUP"), 0, lParam_end)


class ScreenManager:
    # Singleton
    """A manager for interacting with screen process"""
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ScreenManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.hWnd = None
        self.lock = threading.Lock()
        self._initialize()

    def _initialize(self):
        """Define hwnd"""
        process = ProcessManager()
        self.hWnd = process.hWnd

    def set_window_handle(self, hwnd):
        """Set a handle of window"""
        self.hWnd = hwnd

    def capture_screenshot(self, region=None):
        """Capture a screenshot in window and return only the specified region without black background."""
        if not self.hWnd or not win32gui.IsWindow(self.hWnd):
            print("Error: Window invalid or handle not defined.")
            return None

        if win32gui.IsIconic(self.hWnd):
            print("Error: Window minimized.")
            return None

        hwnd_dc = None
        mfc_dc = None
        save_dc = None
        bitmap = None

        try:
            hwnd_dc = win32gui.GetWindowDC(self.hWnd)
            if hwnd_dc == 0:
                print("Error: Not possible to obtain DC of window.")
                return None

            left, top, right, bottom = win32gui.GetClientRect(self.hWnd)
            w = right - left
            h = bottom - top

            mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
            save_dc = mfc_dc.CreateCompatibleDC()
            bitmap = win32ui.CreateBitmap()
            bitmap.CreateCompatibleBitmap(mfc_dc, w, h)
            save_dc.SelectObject(bitmap)

            result = windll.user32.PrintWindow(self.hWnd, save_dc.GetSafeHdc(), 3)
            if result != 1:
                print("Error: PrintWindow failure.")
                return None

            bmpinfo = bitmap.GetInfo()
            bmpstr = bitmap.GetBitmapBits(True)

            img = np.frombuffer(bmpstr, dtype=np.uint8).reshape((bmpinfo["bmHeight"], bmpinfo["bmWidth"], 4))
            img = np.ascontiguousarray(img)[..., :-1]
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

            if region:
                # Extrai diretamente a região desejada
                x, y, width, height = region[0], region[1], region[2], region[3]
                cropped_img = img[y:y + height, x:x + width]
                return cropped_img

            return img
        finally:
            if mfc_dc:
                mfc_dc.DeleteDC()
            if save_dc:
                save_dc.DeleteDC()
            win32gui.ReleaseDC(self.hWnd, hwnd_dc)
            if bitmap:
                win32gui.DeleteObject(bitmap.GetHandle())

    @staticmethod
    def find_image(main_image, template, threshold=0.8, preprocess=False, binary_threshold_main=127, binary_threshold_template=127, all_matches=False,
                   variation=3):
        """
        Find a template image inside another image.

        :param variation:
        :param main_image: The main image where the search will be performed.
        :param template: Path to the template image to search for.
        :param threshold: Similarity threshold (default is 0.8).
        :param preprocess: If True, applies binary thresholding to both images before matching.
        :param binary_threshold_main: Threshold value for binary conversion of the main image (default is 127).
        :param binary_threshold_template: Threshold value for binary conversion of the template image (default is 127).
        :param all_matches: If True, returns all matches found. Otherwise, returns only the first match.
        :return: A list of (center_x, center_y) for all matches if all_matches=True, or a single (center_x, center_y) tuple if not.
                 Returns None if no matches are found.
        """
        # Load the template
        r_template = cv2.imread(template)
        if r_template is None:
            raise ValueError(f"Template image not found or unable to load: {template}")

        # Optional preprocessing: convert both images to grayscale and apply binary thresholding
        if preprocess:
            main_image_gray = cv2.cvtColor(main_image, cv2.COLOR_BGR2GRAY)
            template_gray = cv2.cvtColor(r_template, cv2.COLOR_BGR2GRAY)

            _, main_image_binary = cv2.threshold(main_image_gray, binary_threshold_main, 255, cv2.THRESH_BINARY)
            _, template_binary = cv2.threshold(template_gray, binary_threshold_template, 255, cv2.THRESH_BINARY)

            main_image = main_image_binary
            r_template = template_binary

        # Perform template matching
        res = cv2.matchTemplate(main_image, r_template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= threshold)

        # Get dimensions of the template
        w, h = r_template.shape[1], r_template.shape[0]

        # Collect all matches
        matches = []
        for pt in zip(*loc[::-1]):
            center_x = pt[0] + w // 2
            center_y = pt[1] + h // 2

            random_offset_x = random.randint(-variation, variation)
            random_offset_y = random.randint(-variation, variation)
            randomized_x = center_x + random_offset_x
            randomized_y = center_y + random_offset_y

            matches.append((randomized_x, randomized_y))
            if not all_matches:
                break

        return matches if all_matches else (matches[0] if matches else None)

    def select_regions(self, title="Select the region", multiple=True, save_img=None, default_path="./assets/templates", filename="img"):
        """
        Allows the user to select one or multiple regions from a screenshot and optionally save them as images.

        :param default_path: Directory to save the selected regions as images.
        :param filename: Name of file to save.
        :param title: Title of the selection window.
        :param multiple: Defines if multiple regions can be selected (True) or only a single region (False).
        :param save_img: Param to set if region want to save. If None, regions are not saved.
        :return: List of coordinates of the selected regions (a list with a single tuple if `multiple=False`).
        """
        if not self.hWnd:
            print("Error: Window handle not defined.")
            return []

        screenshot = self.capture_screenshot()
        if screenshot is None:
            print("Error: Failed to capture the screenshot.")
            return []

        regions = []
        count = 0  # To generate unique filenames if saving regions
        start_point = None
        end_point = None
        current_mouse_position = (0, 0)
        selecting = False

        def mouse_callback(event, x, y, flags, param):
            """Callback to handle mouse events and update the selection region."""
            nonlocal start_point, end_point, selecting, current_mouse_position
            current_mouse_position = (x, y)  # Update the current mouse position

            if event == cv2.EVENT_LBUTTONDOWN:
                # Start point of the ROI
                start_point = (x, y)
                selecting = True
                print(f"Start point: {start_point}")

            elif event == cv2.EVENT_MOUSEMOVE and selecting:
                # Update the current end point while dragging
                end_point = (x, y)

            elif event == cv2.EVENT_LBUTTONUP:
                # End point of the ROI
                end_point = (x, y)
                selecting = False
                print(f"End point: {end_point}")

        while True:
            temp_screenshot = screenshot.copy()
            cv2.namedWindow(title)
            cv2.setMouseCallback(title, mouse_callback)

            while True:
                temp_screenshot = screenshot.copy()

                # Draw the ROI rectangle while selecting
                if start_point and end_point:
                    cv2.rectangle(temp_screenshot, start_point, end_point, (255, 0, 0), 2)

                # Display the mouse coordinates near the cursor
                cv2.putText(temp_screenshot, f"{current_mouse_position}",
                            (current_mouse_position[0] + 10, current_mouse_position[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

                # Show the updated image
                cv2.imshow(title, temp_screenshot)
                key = cv2.waitKey(1)

                if key == 27:  # Escape key to cancel
                    print("Selection cancelled.")
                    cv2.destroyAllWindows()
                    return []

                if not selecting and start_point and end_point:
                    # Store the selected region
                    x, y, w, h = start_point[0], start_point[1], end_point[0] - start_point[0], end_point[1] - start_point[1]
                    regions.append((x, y, abs(w), abs(h)))
                    print(f"Region added: x={x}, y={y}, width={abs(w)}, height={abs(h)}")

                    if save_img:
                        # Save the selected region as an image
                        selected_region = screenshot[y:y + abs(h), x:x + abs(w)]
                        file_suffix = f"_{count}" if multiple else ""
                        output_path = f"{default_path}/{filename}{file_suffix}.png"
                        cv2.imwrite(output_path, selected_region)
                        print(f"Region saved as {output_path}")
                        count += 1

                    if not multiple:
                        cv2.destroyAllWindows()
                        return regions

                    # Reset points for the next selection
                    start_point = None
                    end_point = None
                    break

            # Exit the outer loop after completing all selections
            if not multiple:
                break

        cv2.destroyAllWindows()
        return regions


class MouseBlocker:
    def __init__(self):
        self.hook = None
        self.blocking = None
        self.thread = None

        self.logger = LogManager()
        self.pressed_keys = {}  # Para rastrear teclas pressionadas

        self._user32 = ctypes.windll.user32
        self._kernel32 = ctypes.windll.kernel32

    def _low_level_mouse_proc(self, nCode, wParam, lParam):
        """Callback to intercept mouse events."""
        if self.blocking and wParam in {
            keys.get("WM_MOUSEMOVE"),
            keys.get("WM_LBUTTONDOWN"),
            keys.get("WM_LBUTTONUP"),
            keys.get("WM_RBUTTONDOWN"),
            keys.get("WM_RBUTTONUP")
        }:
            return 1
        return self._user32.CallNextHookEx(self.hook, nCode, wParam, lParam)

    def _save_pressed_keys(self):
        """Captura o estado atual das teclas pressionadas."""
        for key_code in range(0x01, 0xFE):  # Range para todas as teclas
            if self._user32.GetAsyncKeyState(key_code) & 0x8000:  # Checa se a tecla está pressionada
                self.pressed_keys[key_code] = True

    def _restore_pressed_keys(self):
        """Restaura o estado das teclas que ainda estão pressionadas."""
        for key_code in self.pressed_keys.keys():
            if self._user32.GetAsyncKeyState(key_code) & 0x8000:  # Se ainda está pressionada
                self._user32.keybd_event(key_code, 0, 0, 0)  # Simula tecla pressionada novamente
            else:
                self._user32.keybd_event(key_code, 0, 0x0002, 0)  # Simula tecla liberada
        self.pressed_keys.clear()  # Limpa o estado rastreado

    def _hook_thread(self):
        """Thread to set the mouse hook."""
        CMPFUNC = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.wintypes.WPARAM, ctypes.wintypes.LPARAM)
        self.proc = CMPFUNC(self._low_level_mouse_proc)

        self.hook = self._user32.SetWindowsHookExW(keys.get("WH_MOUSE_LL"), self.proc, 0, 0)
        if not self.hook:
            raise RuntimeError("Failed to set mouse hook")

        msg = MSG()
        while self._user32.GetMessageW(ctypes.byref(msg), 0, 0, 0) > 0:
            self._user32.TranslateMessage(ctypes.byref(msg))
            self._user32.DispatchMessageW(ctypes.byref(msg))

    def start_blocking(self):
        """Start blocking mouse input."""
        if not self.blocking:
            self._save_pressed_keys()  # Salva o estado antes de bloquear
            self.blocking = True
            self.thread = threading.Thread(target=self._hook_thread, daemon=True)
            self.thread.start()
            self.logger.log("info", f"Mouse blocked.")

    def stop_blocking(self):
        """Stop blocking mouse input."""
        if self.blocking:
            self.blocking = False
            if self.hook:
                self._user32.UnhookWindowsHookEx(self.hook)
                self.hook = None
            self.thread = None
            self._restore_pressed_keys()  # Restaura o estado das teclas após desbloquear
        self.logger.log("info", f"Mouse unblocking.")


# screen_manager = ScreenManager()
# hwnd = win32gui.FindWindow(None, "Medivia")
# screen_manager.set_window_handle(hwnd)
#
# regions_to_show = screen_manager.select_regions("Blank Rune Image",
#                                                 multiple=False,
#                                                 save_img="../assets/templates",
#                                                 filename="blank_rune2")
# if regions_to_show:
#     print(regions_to_show, "regiao xdxd")
#     print("Selected regions:")
#     for idx, (x, y, w, h) in enumerate(regions_to_show, 1):
#         print(f"Region {idx}: x={x}, y={y}, width={w}, height={h}")
#
#
# mouse_blocker = MouseBlocker()
#
# mouse_blocker.start_blocking()
# time.sleep(5)
#
# mouse_blocker.stop_blocking()


