import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
from PySide6.QtWidgets import QWidget, QVBoxLayout, QCheckBox
from scipy.ndimage import gaussian_filter1d

class BeamVisualizationWidget(QWidget):
    def __init__(self, parent=None):
        super(BeamVisualizationWidget, self).__init__(parent)

        self.figure, self.ax = plt.subplots(figsize=(10, 1))
        self.canvas = FigureCanvas(self.figure)

        self.ax.set_title("Визуализация балки")
        self.ax.set_axis_off()

        colors_1 = ["#4B0082", "#007BFF", "#00C896", "#FFC300", "#C70039", "#550000"]
        colors_2 = ["#2E1A47", "#0047AB", "#008F66", "#E3A400", "#B80028", "#400000"]
        colors_3 = ["#00274D", "#0056B3", "#009688", "#FFD700", "#FF5733", "#7D0000"]
        colors_4 = ["#B59FCC", "#92B4E3", "#A3DAC2", "#F9E79F", "#E6A4B4", "#8B5E5E"]
        colors_5 = ["#8561A8", "#5D92C4", "#63BFA1", "#EFC94C", "#E57373", "#9C6B6B"]
        colors_6 = ["#FFFFFF", "#FFE8A3", "#FFB878", "#FF6B6B", "#A52A2A", "#191919"]
        self.cmap = LinearSegmentedColormap.from_list("stress_cmap", colors_1)

        self.smooth_checkbox = QCheckBox("Сглаженная визуализация", self)

        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)
        layout.addWidget(self.smooth_checkbox)

        self.max_load_reference = 10000  # Опорное значение для сил (Н)
        self.max_moment_reference = 1000  # Опорное значение для моментов (Нм)

        self.last_x = None
        self.last_stresses = None
        self.last_critical_stress = None
        self.last_loads = None
        self.last_moments = None  # Новый атрибут для хранения моментов

        self.smooth_checkbox.stateChanged.connect(self.on_smooth_changed)

    def on_smooth_changed(self, state):
        if self.last_x is not None:
            self.update_visualization(
                self.last_x,
                self.last_stresses,
                self.last_critical_stress,
                self.last_loads,
                self.last_moments  # Добавляем моменты в вызов
            )

    def update_visualization(self, x, stresses, critical_stress, loads, moments):
        # Сохраняем все параметры включая моменты
        self.last_x = x
        self.last_stresses = stresses
        self.last_critical_stress = critical_stress
        self.last_loads = loads
        self.last_moments = moments

        self.ax.clear()
        self.ax.set_axis_off()

        vmin = 0
        vmax = critical_stress

        # Обработка сглаживания
        smooth = self.smooth_checkbox.isChecked()
        stresses_smooth = gaussian_filter1d(stresses, 10) if smooth else stresses

        # Визуализация напряжений
        img = np.abs(stresses_smooth)[np.newaxis, :]
        self.ax.imshow(img, aspect='auto', cmap=self.cmap,
                      extent=[x[0], x[-1], 0, 1], vmin=vmin, vmax=vmax, interpolation="bilinear")

        # Отрисовка сил
        for load in loads:
            if isinstance(load, dict) and 'position' in load and 'value' in load:
                position = load['position']
                value = load['value']
                marker_height = abs(value) / self.max_load_reference
                self.ax.vlines(position, 0, marker_height,
                             colors='black', linestyles='solid', linewidths=1)
                self.ax.text(position, -0.15, f"{value:.1f} N",
                            ha='center', va='top', color='black', fontsize=8)

        # Отрисовка моментов (новый блок)
        for moment in moments:
            if isinstance(moment, dict) and 'position' in moment and 'value' in moment:
                position = moment['position']
                value = moment['value']
                marker_height = abs(value) / self.max_moment_reference
                self.ax.vlines(position, 0, marker_height,
                             colors='red', linestyles='solid', linewidths=1)
                self.ax.text(position, -0.25, f"{value:.1f} Nm",
                            ha='center', va='top', color='red', fontsize=8)

        # Настройка области отображения
        self.ax.set_ylim(-0.4, 1)
        self.ax.set_xlim(x[0], x[-1])

        # Обновление цветовой шкалы
        if not hasattr(self, 'cbar'):
            self.cbar = self.figure.colorbar(self.ax.images[0], ax=self.ax,
                                           orientation='horizontal', pad=0.25)
            self.cbar.set_label('Напряжение (Па)')
        else:
            self.cbar.update_normal(self.ax.images[0])

        self.canvas.draw()