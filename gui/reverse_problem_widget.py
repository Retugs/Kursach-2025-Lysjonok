import sys
import numpy as np
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

# Импорты с учетом файловой структуры
from data.random_deflections import generate_random_displacements
from core.beam_solver import BeamSolver
from core.reverce_solver import compute_forces_and_moments


class BeamGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Анализ балки")
        self.setGeometry(100, 100, 1000, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.canvas = FigureCanvas(plt.figure(figsize=(8, 6)))
        self.layout.addWidget(self.canvas)

        self.btn_update = QPushButton("Обновить данные")
        self.btn_update.clicked.connect(self.update_plot)
        self.layout.addWidget(self.btn_update)

        self.update_plot()

    def update_plot(self):
        self.canvas.figure.clear()
        ax1 = self.canvas.figure.add_subplot(311)
        ax2 = self.canvas.figure.add_subplot(312)
        ax3 = self.canvas.figure.add_subplot(313)

        # Генерация случайных перемещений (передаем аргументы n и L)
        n, L = 100, 10.0  # n - количество точек, L - длина балки
        z, w_rand = generate_random_displacements(n, L)

        # Расчет сил и моментов
        z, Q, M, q, forces, moments = compute_forces_and_moments((z, w_rand))

        # Задаем параметры балки
        length = L  # Длина балки совпадает с L
        E = 2e11  # Модуль Юнга (можешь изменить)
        profile_params = {"I": 1e-6, "h": 0.2}  # Добавляем h
        # Создание объекта BeamSolver и расчет восстановленных перемещений
        beam_solver = BeamSolver(length, E, profile_params)
        x_rec, w_rec = beam_solver.calculate_deflections(forces)

        # График исходных перемещений
        ax1.plot(z, w_rand, label="Исходные перемещения", color="blue")
        ax1.set_ylabel("w (м)")
        ax1.legend()
        ax1.grid()

        # Визуализация балки с силами и моментами
        ax2.plot(z, np.zeros_like(z), 'k-', linewidth=2)
        for zF, F in forces:
            ax2.arrow(zF, 0, 0, -np.sign(F) * 0.1, head_width=0.2, head_length=0.05, fc='red', ec='red')
            ax2.text(zF, -np.sign(F) * 0.15, f"{F:.1f} Н", ha="center", fontsize=10, color='red')

        for zM, M_val in moments:
            ax2.text(zM, 0.1, f"{M_val:.1f} Н·м", ha="center", fontsize=10, color='blue')

        ax2.set_ylim(-0.5, 0.5)  # Сделаем больше места для стрелок
        ax2.set_title("Визуализация балки")
        ax2.grid()

        # График восстановленных перемещений
        ax3.plot(x_rec, w_rec, label="Восстановленные перемещения", color="green")
        ax3.set_ylabel("w (м)")
        ax3.legend()
        ax3.grid()

        print("Найденные силы:", forces)
        print("Найденные моменты:", moments)
        print("Восстановленные перемещения:", w_rec)

        self.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BeamGUI()
    window.show()
    sys.exit(app.exec())