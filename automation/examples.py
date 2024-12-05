from automation.actions import FishAction, MoveItemAction
import keyboard
import threading
import time

running = False  # Variável de controle
item_running = False


def fish_action_loop():
    global running
    action_fish = FishAction()
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
    action_item = MoveItemAction()
    while item_running:
        print("\n")
        action_item.execute()
        item_running = False


def toggle_item_action():
    global item_running
    if item_running:
        print("Stopping item action...")
        item_running = False
    else:
        print("Start item action")
        item_running = True
        threading.Thread(target=item_action_loop, daemon=True).start()


def on_key_press(event):
    if event.name == "f7":
        toggle_item_action()


keyboard.on_press(on_key_press)
keyboard.add_hotkey("ctrl+f9", toggle_fishing)
keyboard.add_hotkey("f7", toggle_item_action)

print("Press Ctrl+F9 to start/stop fishing.")
print("Press F7 to start/stop item action.")
keyboard.wait("esc")  # O programa continuará executando até você pressionar ESC
