import sys
from PySide6.QtWidgets import QApplication
from gui.main_menu import MainMenu

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainMenu()
    window.show()
    sys.exit(app.exec())