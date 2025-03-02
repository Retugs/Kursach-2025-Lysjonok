import sys
import numpy as np
from scipy.interpolate import UnivariateSpline  # Для сглаживания
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import FancyArrowPatch
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QPushButton)
from core.beam_solver import BeamSolver  # Импорт класса решателя
from core.reverce_solver import compute_forces_and_moments  # Правильный импорт
from data.random_deflections import generate_random_displacements


class BeamAnalysisGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Beam Forces Analyzer")
        self.setGeometry(100, 100, 1200, 800)

        # Параметры для инициализации BeamSolver
        self.length = 10.0  # Длина балки (м)
        self.E = 2.1e11  # Модуль упругости (Па)
        self.profile_params = {
            'I': 1e-6,  # Момент инерции (м^4)
            'h': 0.1  # Высота сечения (м)
        }

        # Инициализация решателя
        self.solver = BeamSolver(self.length, self.E, self.profile_params)

        # Инициализация данных
        self.displacement_data = None
        self.results = None
        self.calculated_deflections = None

        # Создание виджетов
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        # Основной layout
        main_layout = QVBoxLayout(self.main_widget)

        # Графики
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        main_layout.addWidget(self.canvas)

        # Кнопка Regenerate
        self.btn_regenerate = QPushButton("Regenerate")
        main_layout.addWidget(self.btn_regenerate)

        # Подключение сигналов
        self.btn_regenerate.clicked.connect(self.generate_data)

        # Генерация начальных данных
        self.generate_data()

    def generate_data(self):
        """Генерация случайных данных перемещений"""
        n = 50  # Количество точек
        L = self.length  # Длина балки
        self.displacement_data = generate_random_displacements(n, L)
        self.calculate_forces()
        self.update_plot()

    def calculate_forces(self):
        """Вычисление сил и моментов"""
        if self.displacement_data is None:
            return

        # Параметры расчета
        params = {
            'EI': self.E * self.profile_params['I'],
            'smoothing_factor': 0.01,
            'segment_length': 2.0,
            'force_threshold': 1e3,
            'moment_threshold': 5e3
        }

        # Вычисление сил и моментов
        self.results = compute_forces_and_moments(
            self.displacement_data,
            EI=params['EI'],
            smoothing_factor=params['smoothing_factor'],
            segment_length=params['segment_length'],
            force_threshold=params['force_threshold'],
            moment_threshold=params['moment_threshold']
        )

        # Конвертация нагрузок для beam_solver
        loads = []
        for z, F in self.results[4]:
            loads.append({'type': 'point', 'value': F, 'position': z})  # Формат для calculate_deflections
        for z, M in self.results[5]:
            # Моменты пока не учитываем, так как функция calculate_deflections их не поддерживает
            pass

        # Расчет перемещений по найденным нагрузкам
        self.calculated_deflections = self.solver.calculate_deflections(loads)

    def update_plot(self):
        """Обновление графика"""
        self.figure.clf()

        if self.displacement_data and self.results and self.calculated_deflections:
            z, w = self.displacement_data
            x_calc, w_calc = self.calculated_deflections
            z_beam, Q, M, q, forces, moments = self.results

            # Создаем два подграфика
            ax1 = self.figure.add_subplot(211)  # График перемещений
            ax2 = self.figure.add_subplot(212)  # Визуализация балки

            # Сглаживание calculated deflections
            spline = UnivariateSpline(x_calc, w_calc, s=0.1)  # Параметр s регулирует степень сглаживания
            x_smooth = np.linspace(min(x_calc), max(x_calc), 1000)
            w_smooth = spline(x_smooth)

            # График перемещений
            ax1.plot(z, w, 'b-', label='Original Deflections')
            ax1.plot(x_smooth, w_smooth, 'r--', label='Calculated Deflections (Smoothed)')
            ax1.set_title("Beam Deflections")
            ax1.set_xlabel("Position (m)")
            ax1.set_ylabel("Deflection (m)")
            ax1.grid(True)
            ax1.legend()

            # Визуализация балки
            ax2.plot(z_beam, np.zeros_like(z_beam), 'k-', linewidth=2, label='Beam')

            # Отрисовка сил
            for pos, F in forces:
                color = 'red' if F > 0 else 'blue'
                arrow = FancyArrowPatch(
                    (pos, 0), (pos, F / abs(F) * 0.5),
                    arrowstyle='->', color=color,
                    mutation_scale=20, linewidth=2
                )
                ax2.add_patch(arrow)
                ax2.text(pos, F / abs(F) * 0.6, f'{F:.1f} N',
                         ha='center', color=color)

            # Отрисовка моментов
            for pos, M_val in moments:
                if M_val > 0:
                    # Положительный момент (по часовой стрелке)
                    ax2.annotate('', xy=(pos, 0.3), xytext=(pos, -0.3),
                                 arrowprops=dict(
                                     arrowstyle='->',
                                     color='green',
                                     linewidth=2))
                    ax2.text(pos, 0.35, f'{M_val:.1f} N·m',
                             ha='center', color='green')
                else:
                    # Отрицательный момент (против часовой стрелки)
                    ax2.annotate('', xy=(pos, -0.3), xytext=(pos, 0.3),
                                 arrowprops=dict(
                                     arrowstyle='->',
                                     color='purple',
                                     linewidth=2))
                    ax2.text(pos, -0.35, f'{M_val:.1f} N·m',
                             ha='center', color='purple')

            # Настройки графика балки
            ax2.set_title("Beam Visualization")
            ax2.set_xlabel("Position (m)")
            ax2.set_ylim(-1, 1)
            ax2.grid(True)
            ax2.legend()

        self.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BeamAnalysisGUI()
    window.show()
    sys.exit(app.exec())