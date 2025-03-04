import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtWidgets import QWidget, QVBoxLayout

class PlotWidget(QWidget):
    def __init__(self, parent=None):
        super(PlotWidget, self).__init__(parent)

        self.figure, self.axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
        self.canvas = FigureCanvas(self.figure)
        self.axes[0].set_title("")
        self.axes[1].set_title("")
        self.axes[2].set_title("")
        for ax in self.axes:
            ax.grid(True)

        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)

    def update_plots(self, data):
        for ax in self.axes:
            ax.clear()

        if 'moment_diagram' in data:
            x_moment, moments = data['moment_diagram']
            ax_moment = self.axes[0]
            ax_moment.plot(x_moment, moments, 'b-', label='Моменты', linewidth=1.5)  # Линия графика
            ax_moment.fill_between(x_moment, moments, color='blue', alpha=0.15)  # Заливка с прозрачностью
            ax_moment.set_title("Моменты", fontsize=14, fontweight='bold')  # Заголовок
            ax_moment.set_ylabel("Момент (Н·м)", fontsize=12)
            ax_moment.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)  # Плотная сетка
            ax_moment.axhline(0, color='black', linewidth=2.5, alpha=0.9)  # Жирная ось y=0
            ax_moment.legend(fontsize=10, loc='best')  # Легенда

        if 'deflections' in data:
            x_defl, deflections = data['deflections']
            ax_defl = self.axes[1]
            ax_defl.plot(x_defl, deflections, 'g-', label='Прогибы', linewidth=1.5)
            ax_defl.fill_between(x_defl, deflections, color='green', alpha=0.15)
            ax_defl.set_title("Прогибы", fontsize=14, fontweight='bold')
            ax_defl.set_ylabel("Прогиб (м)", fontsize=12)
            ax_defl.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)
            ax_defl.axhline(0, color='black', linewidth=2.5, alpha=0.9)
            ax_defl.legend(fontsize=10, loc='best')

        if 'transverse_forces' in data:
            x_trans, transverse = data['transverse_forces']
            ax_trans = self.axes[2]
            ax_trans.plot(x_trans, transverse, 'm-', label='Поперечные силы', linewidth=1.5)
            ax_trans.fill_between(x_trans, transverse, color='magenta', alpha=0.15)
            ax_trans.set_title("Поперечные силы", fontsize=14, fontweight='bold')
            ax_trans.set_xlabel("Позиция (м)", fontsize=12)
            ax_trans.set_ylabel("Сила (Н)", fontsize=12)
            ax_trans.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)
            ax_trans.axhline(0, color='black', linewidth=2.5, alpha=0.9)
            ax_trans.legend(fontsize=10, loc='best')

        self.canvas.draw()