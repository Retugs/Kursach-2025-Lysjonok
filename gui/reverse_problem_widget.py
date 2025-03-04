import numpy as np
import matplotlib.pyplot as plt
from PySide6.QtWidgets import  QMainWindow, QPushButton, QVBoxLayout, QWidget
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from core.reverce_solver import generate_random_displacements, compute_forces_and_moments
from core.beam_solver import BeamSolver
from scipy.interpolate import UnivariateSpline



class BeamApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Визуализация балки")
        self.setGeometry(100, 100, 800, 900)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.button = QPushButton("Regenerate")
        self.button.clicked.connect(self.update_plot)
        self.layout.addWidget(self.button)

        self.figure, self.axs = plt.subplots(3, 1, figsize=(8, 10))
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        self.n = 500
        self.L = 10.0
        self.N_modes = 5
        self.max_amplitude = 0.1
        self.E = 1e8
        self.I = 1e-4
        self.smoothing_factor = 0.01
        self.segment_length = 1.0
        self.force_threshold = 100
        self.moment_threshold = 50

        self.update_plot()

    def update_plot(self):
        # Очистка графиков
        for ax in self.axs:
            ax.clear()

        z, w = generate_random_displacements(self.n, self.L, self.N_modes, self.max_amplitude)

        _, Q, M, q, forces, moments = compute_forces_and_moments(
            (z, w), self.E * self.I, self.smoothing_factor, self.segment_length, self.force_threshold,
            self.moment_threshold
        )

        print("\nНайденные сосредоточенные силы:")
        if forces:
            for z_F, F in forces:
                print(f"  Сила {F:.2f} Н в точке z = {z_F:.2f} м")
        else:
            print("  Нет найденных сил.")
        print(f"\nМаксимальные и минимальные значения:")
        print(f"  max(q) = {max(q):.2f}, min(q) = {min(q):.2f}")
        print(f"  max(M) = {max(M):.2f}, min(M) = {min(M):.2f}")

        if forces:
            beam_solver = BeamSolver(self.L, self.E, {'I': self.I, 'h': 0.1})
            loads = [{'type': 'point', 'value': F, 'position': z_F} for z_F, F in forces]
            z_restored, w_restored = beam_solver.calculate_deflections(loads)
            print(f"\nВосстановленные перемещения: max = {max(w_restored):.5f}, min = {min(w_restored):.5f}")
            smoothing_spline = UnivariateSpline(z_restored, w_restored, s=50)  # s - степень сглаживания
            w_smoothed = smoothing_spline(z_restored)

        else:
            z_restored, w_restored, w_smoothed = np.array([]), np.array([]), np.array([])

        self.axs[0].plot(z, w, label="Исходные перемещения w(z)", color="blue")
        self.axs[0].set_xlabel("z (м)")
        self.axs[0].set_ylabel("w (м)")
        self.axs[0].legend()
        self.axs[0].grid()

        if len(z_restored) > 0:
            self.axs[1].plot(z_restored, w_smoothed, '--', label="Восстановленные перемещения",
                             color="red")
        else:
            self.axs[1].text(0.5, 0.5, "Нет восстановленных данных", ha='center', va='center',
                             transform=self.axs[1].transAxes)

        self.axs[1].set_xlabel("z (м)")
        self.axs[1].set_ylabel("w (м)")
        self.axs[1].legend()
        self.axs[1].grid()

        self.axs[2].axhline(0, color="black", linewidth=2)
        for z_F, F in forces:
            color = "red" if F > 0 else "blue"
            self.axs[2].arrow(z_F, 0, 0, 0.5 * np.sign(F), head_width=0.2, head_length=0.2, fc=color, ec=color)
            self.axs[2].text(z_F, 0.6 * np.sign(F), f"{F:.1f} Н", ha="center", color=color)

        self.axs[2].set_xlabel("Длина балки (м)")
        self.axs[2].set_ylabel("Силы")
        self.axs[2].grid()

        self.canvas.draw()