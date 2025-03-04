import numpy as np
import matplotlib.pyplot as plt
from PySide6.QtWidgets import  QMainWindow, QPushButton, QVBoxLayout, QWidget
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from core.reverce_solver import generate_random_displacements, compute_forces_and_moments


class BeamApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Визуализация балки")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.button = QPushButton("Regenerate")
        self.button.clicked.connect(self.update_plot)
        self.layout.addWidget(self.button)

        self.figure, self.axs = plt.subplots(2, 1, figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        self.n = 200
        self.L = 10.0
        self.N_modes = 5
        self.max_amplitude = 0.1
        self.EI = 1e6
        self.smoothing_factor = 0.01
        self.segment_length = 2.0
        self.force_threshold = 1e3
        self.moment_threshold = 5e3

        self.update_plot()

    def update_plot(self):
        # Очистка графиков
        for ax in self.axs:
            ax.clear()

        z, w = generate_random_displacements(self.n, self.L, self.N_modes, self.max_amplitude)

        _, Q, M, q, forces, moments = compute_forces_and_moments(
            (z, w), self.EI, self.smoothing_factor, self.segment_length, self.force_threshold, self.moment_threshold
        )

        print("\nНайденные сосредоточенные силы:")
        if forces:
            for z_F, F in forces:
                print(f"  Сила {F:.2f} Н в точке z = {z_F:.2f} м")
        else:
            print("  Нет найденных сил.")

        self.axs[0].plot(z, w, label="Перемещения w(z)", color="blue")
        self.axs[0].set_xlabel("z (м)")
        self.axs[0].set_ylabel("w (м)")
        self.axs[0].legend()
        self.axs[0].grid()

        self.axs[1].axhline(0, color="black", linewidth=2)
        for z_F, F in forces:
            color = "red" if F > 0 else "blue"
            self.axs[1].arrow(z_F, 0, 0, 0.5 * np.sign(F), head_width=0.2, head_length=0.2, fc=color, ec=color)
            self.axs[1].text(z_F, 0.6 * np.sign(F), f"{F:.1f} Н", ha="center", color=color)

        self.axs[1].set_xlabel("Длина балки (м)")
        self.axs[1].set_ylabel("Силы")
        self.axs[1].grid()

        self.canvas.draw()