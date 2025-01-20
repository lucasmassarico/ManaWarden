import ctypes
import time

# Define constants
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010

# Get screen dimensions
SCREEN_WIDTH = ctypes.windll.user32.GetSystemMetrics(0)
SCREEN_HEIGHT = ctypes.windll.user32.GetSystemMetrics(1)


def send_right_click(x, y):
    """Simulate a right-click at the given screen coordinates."""
    # Convert coordinates to absolute values
    abs_x = int(x * 65535 / SCREEN_WIDTH)
    abs_y = int(y * 65535 / SCREEN_HEIGHT)

    # Structure for mouse input
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

    # Create input events for right-click
    inputs = (Input * 2)(
        Input(type=0, mi=MouseInput(dx=abs_x, dy=abs_y, mouseData=0,
                                    dwFlags=MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE, time=0, dwExtraInfo=None)),
        Input(type=0, mi=MouseInput(dx=0, dy=0, mouseData=0,
                                    dwFlags=MOUSEEVENTF_RIGHTDOWN | MOUSEEVENTF_RIGHTUP, time=0, dwExtraInfo=None))
    )

    # Send inputs
    ctypes.windll.user32.SendInput(len(inputs), ctypes.byref(inputs), ctypes.sizeof(Input))


if __name__ == "__main__":
    # Coordinates for the click (absolute screen coordinates)
    x, y = 1584, 400  # Adjust as needed
    print(f"Simulating right-click at ({x}, {y})...")
    send_right_click(x, y)
    print("Right-click simulation completed.")
