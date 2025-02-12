import tkinter as tk
from automation.actions import FishAction, UseItemAction, MoveItemAction, CastSpellAction, CastIciclesMedivia
import keyboard
import threading
import time
import random
from process_manager import ScreenManager, ProcessManager

# Gerenciador de processos e tela
process = ProcessManager()
screen = ScreenManager()
handle = process.find_hWnd_by_name("Medivia")
process.set_hwnd(handle)
process.medivia = True
screen.set_window_handle(handle)

# Variáveis globais de controle
running = False
item_running = False
move_running = False
current_action = ""

# Criar a janela principal
root = tk.Tk()
root.overrideredirect(True)  # Remove bordas da janela
root.attributes("-topmost", True)  # Mantém a janela sempre no topo
root.attributes("-transparentcolor", "black")  # Define o preto como transparente

# Dimensões da bolinha
diameter = 20
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Definir posição no canto inferior direito
x_pos = 1550
y_pos = 35
root.geometry(f"{diameter+15}x{diameter}+{x_pos}+{y_pos}")

# Criar um canvas para desenhar a bolinha
canvas = tk.Canvas(root, width=diameter+15, height=diameter, bg="black", highlightthickness=0)
canvas.pack()

# Desenhar a bolinha
indicator = canvas.create_oval(2, 2, diameter - 2, diameter - 2, fill="green", outline="green")
text_label = canvas.create_text(diameter + 5, diameter // 2, text="", fill="white", font=("Arial", 12, "bold"))

# Atualiza a bolinha e a legenda
def update_indicator(status, label):
    color = "green" if not status else "red"
    canvas.itemconfig(indicator, fill=color, outline=color)
    canvas.itemconfig(text_label, text=label)

# Fechar a janela ao clicar na bolinha
def close(event):
    root.destroy()

canvas.bind("<Button-1>", close)


# Funções de loop das ações
def fish_action_loop():
    global running, current_action
    action_fish = UseItemAction(instance_n=15)
    while running:
        current_action = "F"
        update_indicator(True, "F")
        action_fish.execute()
        time.sleep(0.6)
    update_indicator(False, "")


def mana_action_loop():
    global running, current_action
    action_mana = UseItemAction(instance_n=20)
    while running:
        current_action = "M"
        update_indicator(True, "M")
        action_mana.execute()
        time.sleep(0.55)
    update_indicator(False, "")


def hmm_action_loop():
    global running, current_action
    action_hmm = UseItemAction(instance_n=25)
    while running:
        current_action = "H"
        update_indicator(True, "H")
        action_hmm.execute()
        time.sleep(1.50 + random.uniform(-0.01, 0.1))
    update_indicator(False, "")


def icicle_action_loop():
    global running, current_action
    action_icicle = CastIciclesMedivia(instance_n=1)
    while running:
        current_action = "I"
        update_indicator(True, "I")
        action_icicle.execute()
        time.sleep(1.50 + random.uniform(-0.05, 0.1))
    update_indicator(False, "")


# Funções para alternar as ações
def toggle_fishing():
    global running
    if running:
        running = False
    else:
        running = True
        threading.Thread(target=fish_action_loop, daemon=True).start()


def toggle_mana():
    global running
    if running:
        running = False
    else:
        running = True
        threading.Thread(target=mana_action_loop, daemon=True).start()


def toggle_hmm():
    global running
    if running:
        running = False
    else:
        running = True
        threading.Thread(target=hmm_action_loop, daemon=True).start()


def toggle_uh():
    action_uh = UseItemAction(instance_n=1)
    action_uh.execute()


def toggle_icicle():
    global running
    if running:
        running = False
    else:
        running = True
        threading.Thread(target=icicle_action_loop, daemon=True).start()


# Configurar atalhos do teclado
keyboard.add_hotkey("ctrl+f9", toggle_fishing)
keyboard.add_hotkey("ctrl+f10", toggle_mana)
keyboard.add_hotkey("f4", toggle_hmm)
# keyboard.add_hotkey("4", toggle_icicle)
# keyboard.add_hotkey("2", toggle_uh)

print("Press Ctrl+F9 to start/stop fishing.")
print("Press Ctrl+F10 to start/stop MANA.")
print("Press F4 to start/stop HMM.")
print("Press 4 to start/stop ICICLES.")

# Manter o Tkinter rodando
root.mainloop()
