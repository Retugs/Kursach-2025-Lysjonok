import numpy as np
from PySide6.QtWidgets import QWidget, QMainWindow
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QImage, QPainter, QColor
from numba import jit

"""
0 - Синие оттенки
1 - Радуга
2 - Пастель (по умолчанию)
3 - Огонь
4 - Лес
5 - Закат
6 - Океан
7 - Неон
8 - Чёрно-белый
"""


class FractalWidget(QWidget):
    def __init__(self, palette=8, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_OpaquePaintEvent)

        # Параметры анимации (НАСТРОЙКИ СКОРОСТИ ЗДЕСЬ)
        self.animation_speed = 0.1  # Множитель скорости (0.1-1.0)

        # Основные параметры
        self._width = 800
        self._height = 600
        self.max_iter = 120
        self.update_interval = 5  # Интервал обновления в ms

        # Параметры преобразований
        self.zoom = 10.0
        self.angle = 0.0
        self.hue_offset = 0.0
        self.palette = palette

        # Инициализация данных
        self.color_map = np.zeros((self.max_iter, 3), dtype=np.uint8)
        self.fractal = self._generate_julia(
            self._width,
            self._height,
            self.zoom,
            self.angle,
            self.max_iter
        )
        self.update_color_map()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_fractal)
        self.timer.start(self.update_interval)

    @staticmethod
    @jit(nopython=True)
    def _generate_julia(width, height, zoom, angle, max_iter):
        c = 0.7885 * np.exp(1j * angle)
        re = np.linspace(-1.5 / zoom, 1.5 / zoom, width)
        im = np.linspace(-1.0 / zoom, 1.0 / zoom, height)
        fractal = np.zeros((height, width), dtype=np.uint16)

        for y in range(height):
            for x in range(width):
                z = re[x] + 1j * im[y]
                for i in range(max_iter):
                    if abs(z) > 4.0:
                        break
                    z = z ** 2 + c
                    fractal[y, x] += 1
        return fractal

    def update_color_map(self):
        """Выбор палитры через номер (0-8) в self.palette"""
        for i in range(self.max_iter):
            t = i / self.max_iter
            if self.palette == 0:  # Синие оттенки
                self.color_map[i] = (10, 50 + 150 * t, 200 + 55 * t)
            elif self.palette == 1:  # Радуга
                h = (self.hue_offset + t) % 1.0
                color = QColor.fromHsvF(h, 0.8, 0.9)
                self.color_map[i] = (color.red(), color.green(), color.blue())
            elif self.palette == 2:  # Пастель (по умолчанию)
                h = (0.5 + 0.3 * np.sin(2 * np.pi * t)) % 1.0
                s = 0.3 + 0.2 * t
                v = 0.8 - 0.4 * t
                color = QColor.fromHsvF(h, s, v)
                self.color_map[i] = (color.red(), color.green(), color.blue())
            elif self.palette == 3:  # Огонь
                self.color_map[i] = (255, 80 + 100 * t, 30 * t)
            elif self.palette == 4:  # Лес
                self.color_map[i] = (20 * t, 100 + 80 * t, 40 * t)
            elif self.palette == 5:  # Закат
                r = 255 * (0.8 + 0.2 * np.sin(2 * np.pi * t))
                g = 100 * (1 - t)
                b = 150 * t
                self.color_map[i] = (int(r), int(g), int(b))
            elif self.palette == 6:  # Океан
                self.color_map[i] = (20 * t, 100 + 80 * t, 200 + 55 * t)
            elif self.palette == 7:  # Неон
                r = 255 * np.sin(2 * np.pi * t)
                g = 255 * np.sin(2 * np.pi * (t + 0.33))
                b = 255 * np.sin(2 * np.pi * (t + 0.66))
                self.color_map[i] = (int(r), int(g), int(b))
            elif self.palette == 8:  # Чёрно-белый
                intensity = int(255 * (1 - t))
                self.color_map[i] = (intensity, intensity, intensity)

    def update_fractal(self):
        # Плавные изменения параметров (основные настройки скорости)
        self.angle += 0.005 * self.animation_speed  # Было 0.01
        self.zoom = 1.0 + 0.1 * np.sin(self.angle / 5)  # Было 0.15 и /4
        self.hue_offset += 0.002 * self.animation_speed  # Было 0.005

        self.fractal = self._generate_julia(
            self._width,
            self._height,
            self.zoom,
            self.angle,
            self.max_iter
        )
        self.update_color_map()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        buffer = np.zeros((self._height, self._width, 3), dtype=np.uint8)
        np.take(self.color_map, np.clip(self.fractal, 0, self.max_iter - 1),
                out=buffer, axis=0)
        image = QImage(buffer.data, self._width, self._height,
                       QImage.Format_RGB888)
        painter.drawImage(self.rect(), image)

    def resizeEvent(self, event):
        self._width = self.width()
        self._height = self.height()
        self.fractal = self._generate_julia(
            self._width,
            self._height,
            self.zoom,
            self.angle,
            self.max_iter
        )
        self.update_color_map()
        self.update()


class ReverseModeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Обратный режим")

        # Для смены палитры измените число (0-8) ↓
        self.fractal_widget = FractalWidget(palette=8)  # 2 = пастель по умолчанию

        self.setCentralWidget(self.fractal_widget)
        self.showFullScreen()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    def set_palette(self, palette):
        """Явная установка палитры с принудительным обновлением"""
        self.palette = palette
        self.update_color_map()
        self.update()