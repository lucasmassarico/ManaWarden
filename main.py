import sys
from PySide6.QtWidgets import QApplication
from ui.process_dialog import ProcessSelectionDialog
from process_manager import ProcessManager
from ui.MainWindow import MainWindow

sys.argv += ["-platform", "windows:darkmode=2"]

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    select_process = ProcessSelectionDialog()
    result = select_process.exec()

    process_manager = ProcessManager()

    if result == ProcessSelectionDialog.Accepted:
        select_process.select_process()

        if not process_manager.hWnd:
            sys.exit(99)
        main_window = MainWindow()
        main_window.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)
