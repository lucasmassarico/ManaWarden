from automation.actions import FishAction, UseItemAction, MoveItemAction, CastSpellAction
import keyboard
import threading
import time
from process_manager import ScreenManager, ProcessManager


process = ProcessManager()
screen = ScreenManager()
handle = process.find_hWnd_by_name("Medivia")
process.set_hwnd(handle)
process.medivia = True
screen.set_window_handle(handle)

running = False  # Variável de controle
item_running = False
move_running = False


def fish_action_loop():
    global running
    # action_fish = FishAction()
    action_fish = UseItemAction(instance_n=15)
    while running:
        print("\n")  # Substitua por `action_fish.execute()`
        action_fish.execute()
        time.sleep(0.6)  # Ajuste o intervalo de execução, se necessário


def toggle_fishing():
    global running
    if running:
        print("Stopping fishing...")
        running = False
    else:
        print("Starting fishing...")
        running = True
        threading.Thread(target=fish_action_loop, daemon=True).start()


def item_action_loop():
    global item_running
    action_item = UseItemAction()
    while item_running:
        print("\n")
        action_item.execute()
        item_running = False


def move_action_loop():
    global move_running
    action_move = MoveItemAction()
    while move_running:
        print("\n")
        action_move.execute()
        move_running = False


def toggle_item_action():
    global item_running
    if item_running:
        print("Stopping item action...")
        item_running = False
    else:
        print("Start item action")
        item_running = True
        threading.Thread(target=item_action_loop, daemon=True).start()


def toggle_move_action():
    global move_running
    if move_running:
        print("stopping move action...")
        move_running = False
    else:
        print("start move action")
        move_running = True
        threading.Thread(target=move_action_loop, daemon=True).start()


# def on_key_press(event):
#     if event.name == "f7":
#         toggle_item_action()

# keyboard.on_press(on_key_press)
keyboard.add_hotkey("ctrl+f9", toggle_fishing)
keyboard.add_hotkey("f7", toggle_item_action)
keyboard.add_hotkey("f8", toggle_move_action)

print("Press Ctrl+F9 to start/stop fishing.")
print("Press F7 to start/stop item action.")
print("Press F8 to start/stop move action.")
keyboard.wait("esc")  # O programa continuará executando até você pressionar ESC
