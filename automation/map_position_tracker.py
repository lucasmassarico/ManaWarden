import time
from process_manager import ProcessManager, ScreenManager


def track_map_position(window_title, template_path, update_interval=1):
    """
    Monitora continuamente a posição do mapa na aplicação.

    Args:
        window_title (str): Título da janela da aplicação.
        template_path (str): Caminho para o template da imagem do mapa.
        update_interval (float): Intervalo em segundos entre as atualizações.
    """
    # Inicializa os gerenciadores de processo e tela
    process_manager = ProcessManager()
    screen_manager = ScreenManager()

    # Localiza e define o hwnd da janela
    hwnd = process_manager.find_hWnd_by_name(window_title)
    if not hwnd:
        print(f"Janela com o título '{window_title}' não encontrada.")
        return

    process_manager.set_hwnd(hwnd)
    screen_manager.set_window_handle(hwnd)

    print(f"Monitorando a posição do mapa na janela '{window_title}'...\n")

    try:
        while True:
            # Captura a screenshot da janela
            screen = screen_manager.capture_screenshot()
            if screen is None:
                print("Erro ao capturar a tela. Verifique se a janela está acessível.")
                break

            # Encontra a posição do mapa
            position = screen_manager.find_image(main_image=screen, template=template_path)
            if position:
                print(f"Mapa encontrado na posição: {position}")
            else:
                print("Mapa não encontrado na tela.")

            # Aguarda pelo próximo ciclo
            time.sleep(update_interval)
    except KeyboardInterrupt:
        print("\nMonitoramento interrompido pelo usuário.")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")


if __name__ == "__main__":
    # Substitua pelo título da janela e pelo caminho do template do mapa
    window_title = "Título da Aplicação"
    template_path = "./assets/templates/map_template.png"

    # Intervalo de atualização (em segundos)
    update_interval = 1

    # Inicia o rastreamento
    track_map_position(window_title, template_path, update_interval)