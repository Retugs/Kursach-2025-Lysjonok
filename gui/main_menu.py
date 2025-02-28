from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMainWindow
from PySide6.QtGui import QFont
from gui.auto_mode_window import AutoModeWindow
from PySide6.QtCore import Qt
from gui.main_window import MainWindow
from data.visualisation import FractalWidget

class ReverseModeWindow(QMainWindow):
    """Окно для отображения фрактала в полноэкранном режиме"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Обратный режим")
        self.fractal = FractalWidget()
        self.setCentralWidget(self.fractal)
        self.showFullScreen()


class MainMenu(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Главное Меню")
        self.setGeometry(1000, 500, 400, 300)
        self.setStyleSheet("background-color: #2b2b2b; color: #ffffff;")

        layout = QVBoxLayout()
        layout.setSpacing(15)

        title = QLabel("Главное Меню")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        self.manual_button = self.create_button("Ручной режим", self.load_manual_mode)
        self.auto_button = self.create_button("Автоматический режим", self.load_auto_mode)
        self.reverse_button = self.create_button("Обратный режим", self.load_reverse_mode)

        layout.addWidget(title)
        layout.addWidget(self.manual_button)
        layout.addWidget(self.auto_button)
        layout.addWidget(self.reverse_button)
        layout.addStretch()

        self.setLayout(layout)

    def create_button(self, text, callback):
        button = QPushButton(text)
        button.setFont(QFont("Arial", 14))
        button.setFixedHeight(40)
        button.setCursor(Qt.PointingHandCursor)
        button.setStyleSheet("""
            QPushButton {
                background-color: #444;
                color: white;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #666;
            }
            QPushButton:pressed {
                background-color: #222;
            }
        """)
        button.clicked.connect(callback)
        return button

    def load_manual_mode(self):
        self.window = MainWindow()
        self.window.show()
        self.close()

    def load_auto_mode(self):
        self.window = AutoModeWindow()
        self.window.show()
        self.close()

    def load_reverse_mode(self):
        self.reverse_window = ReverseModeWindow()
        self.reverse_window.show()
        self.hide()


