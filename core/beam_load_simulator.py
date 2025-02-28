import random
import time
from PySide6.QtCore import QThread, Signal

class BeamLoadSimulator(QThread):
    update_signal = Signal(list, list)  # Сигнал для передачи сил и моментов

    def __init__(self, beam_length, num_forces, num_moments):
        super().__init__()
        self.beam_length = beam_length
        self.num_forces = num_forces
        self.num_moments = num_moments
        self.forces = self._generate_initial_loads('point', num_forces)
        self.moments = self._generate_initial_loads('moment', num_moments)
        self.is_running = True

    def _generate_initial_loads(self, load_type, num_loads):
        """Генерирует начальные случайные нагрузки."""
        loads = []
        for _ in range(num_loads):
            value = random.uniform(-10000, 10000)  # Случайное значение силы или момента
            position = random.uniform(0, self.beam_length)  # Случайная позиция на балке
            loads.append({'type': load_type, 'value': value, 'position': position})
        return loads

    def run(self):
        """Основной цикл симуляции с плавным изменением нагрузок."""
        while self.is_running:
            self._update_loads(self.forces)
            self._update_loads(self.moments)
            self.update_signal.emit(self.forces, self.moments)  # Отправка данных
            time.sleep(0.5)  # Пауза для плавности (можно настроить)

    def _update_loads(self, loads):
        """Плавно изменяет значения и позиции нагрузок."""
        for load in loads:
            # Случайное приращение значения
            delta_value = random.uniform(-100, 100)
            load['value'] += delta_value
            # Случайное приращение позиции с ограничением в пределах балки
            delta_position = random.uniform(-0.1, 0.1)
            load['position'] = max(0, min(self.beam_length, load['position'] + delta_position))

    def stop(self):
        """Останавливает симуляцию."""
        self.is_running = False
        self.wait()