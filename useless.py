from process_manager import ProcessManager
import time
import keyboard


def main():
    manager = ProcessManager()

    # Defina o `hWnd` para a janela que deseja controlar.
    hwnd = manager.find_hWnd_by_name("The Sandbox")  # Substitua "Nome da Janela" pelo título da janela.
    if not hwnd:
        print("Janela não encontrada!")
        return

    manager.set_hwnd(hwnd)

    print("Pressione F5 para realizar 10 cliques rápidos na janela.")
    print("Pressione ESC para sair do programa.")

    while True:
        if keyboard.is_pressed("f5"):
            print("Executando 10 cliques rápidos...")
            for _ in range(60):
                # Ajuste as coordenadas (x, y) conforme necessário.
                manager.click(x=100, y=100, button="left")
                manager.click(x=100, y=100, button="right")
        if keyboard.is_pressed("esc"):
            print("Programa encerrado.")
            break


if __name__ == "__main__":
    main()
