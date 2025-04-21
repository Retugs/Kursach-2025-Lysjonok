import sys
import json
import os
import time
import datetime
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton,
    QLabel, QSpinBox, QDoubleSpinBox, QTextEdit, QProgressBar, QGroupBox
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

# Импорт необходимых функций/классов из calc_module и beam_solver
from core.beam_solver import BeamSolver
from core.calc_module import (
    L_GLOBAL, E_GLOBAL, I_GLOBAL, GLOBAL_MAX_ITER,
    generate_random_displacements, run_multistart_optimization
)


class MainGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Обратная задача — улучшенный интерфейс")

        self.n_points = 200
        self.N_modes = 3
        self.max_amplitude = 0.05
        self.n_starts = 1

        self.solver = BeamSolver(L_GLOBAL, E_GLOBAL, {'I': I_GLOBAL, 'h': 0.1})

        # Основной вертикальный layout
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # 1. Верхняя панель управления
        self._create_top_controls()

        # 2. Прогресс-бар
        self._create_progress_bar()

        # 3. Поле вывода текста
        self.textOutput = QTextEdit()
        self.textOutput.setReadOnly(True)
        self.main_layout.addWidget(self.textOutput)

        # 4. Графики Matplotlib
        self.fig, self.axs = plt.subplots(1, 2, figsize=(10, 4))
        self.canvas = FigureCanvas(self.fig)
        self.main_layout.addWidget(self.canvas)

        # Инициализация
        self.x_target = None
        self.w_target = None

        self.on_regenerate_clicked()

    def _create_top_controls(self):
        """
        Создаём панель управления вверху окна:
        - Блок выбора сил, моментов, числа мод, амплитуды, числа стартов.
        - Кнопка Regenerate.
        """
        top_box = QGroupBox("Настройки модели")
        top_layout = QGridLayout()
        top_box.setLayout(top_layout)

        # Силы
        self.labelForces = QLabel("Силы:")
        self.spinForces = QSpinBox()
        self.spinForces.setRange(0, 1000)
        self.spinForces.setValue(2)

        # Моменты
        self.labelMoments = QLabel("Моменты:")
        self.spinMoments = QSpinBox()
        self.spinMoments.setRange(0, 10)
        self.spinMoments.setValue(1)

        # Число мод
        self.labelModes = QLabel("Число мод:")
        self.spinModes = QSpinBox()
        self.spinModes.setRange(1, 20)
        self.spinModes.setValue(self.N_modes)

        # Макс. амплитуда
        self.labelAmplitude = QLabel("Макс. амплитуда:")
        self.spinAmplitude = QDoubleSpinBox()
        self.spinAmplitude.setRange(0.0, 10.0)
        self.spinAmplitude.setSingleStep(0.01)
        self.spinAmplitude.setValue(self.max_amplitude)

        # Число стартов
        self.labelMulti = QLabel("Число стартов:")
        self.spinMulti = QSpinBox()
        self.spinMulti.setRange(1, 50)
        self.spinMulti.setValue(self.n_starts)

        # Кнопка Regenerate
        self.btnRegenerate = QPushButton("Regenerate")
        self.btnRegenerate.clicked.connect(self.on_regenerate_clicked)

        # Размещаем в сетке
        top_layout.addWidget(self.labelForces,    0, 0)
        top_layout.addWidget(self.spinForces,     0, 1)
        top_layout.addWidget(self.labelMoments,   0, 2)
        top_layout.addWidget(self.spinMoments,    0, 3)

        top_layout.addWidget(self.labelModes,     1, 0)
        top_layout.addWidget(self.spinModes,      1, 1)
        top_layout.addWidget(self.labelAmplitude, 1, 2)
        top_layout.addWidget(self.spinAmplitude,  1, 3)

        top_layout.addWidget(self.labelMulti,     2, 0)
        top_layout.addWidget(self.spinMulti,      2, 1)
        top_layout.addWidget(self.btnRegenerate,  2, 3)

        self.main_layout.addWidget(top_box)

    def _create_progress_bar(self):
        """
        Создаём progress bar и метки для отображения текущего процента итераций и числа запусков.
        """
        progress_layout = QHBoxLayout()

        self.progressBar = QProgressBar()
        # Скрываем внутренний текст, оставляем только саму полосу
        self.progressBar.setTextVisible(False)
        self.progressBar.setRange(0, 100)

        self.progressLabel = QLabel("Итерация: 0%")
        self.launchLabel = QLabel("Запусков: 0/0")

        progress_layout.addWidget(self.progressBar)
        progress_layout.addWidget(self.progressLabel)
        progress_layout.addWidget(self.launchLabel)

        self.main_layout.addLayout(progress_layout)

    def on_regenerate_clicked(self):
        """
        Генерирует новую "целевую" кривую перемещений, запускает многостартовую оптимизацию,
        обновляет графики, выводит результаты и сохраняет итоговые данные в файл data/data.json.
        """
        import time, os, json, datetime

        # 1. Считываем параметры из управляющих элементов
        N_F = self.spinForces.value()
        N_M = self.spinMoments.value()
        self.N_modes = self.spinModes.value()
        self.max_amplitude = self.spinAmplitude.value()
        self.n_starts = self.spinMulti.value()

        # 2. Генерируем "целевые" перемещения (n_points фиксировано)
        self.x_target, self.w_target = generate_random_displacements(
            n=self.n_points,
            L=L_GLOBAL,
            N_modes=self.N_modes,
            max_amplitude=self.max_amplitude
        )

        # 3. Запускаем многостартовую оптимизацию с измерением времени
        start_time = time.time()
        best_params, best_loads, best_error, best_nit = run_multistart_optimization(
            solver=self.solver,
            x_target=self.x_target,
            w_target=self.w_target,
            N_F=N_F,
            N_M=N_M,
            n_starts=self.n_starts,
            iteration_callback=self._iteration_callback,
            start_callback=self._start_callback
        )
        elapsed_time = time.time() - start_time

        # 4. Вычисляем восстановленные перемещения
        x_calc, w_calc = self.solver.calculate_deflections_test(best_loads, num_points=len(self.x_target))

        # 5. Обновляем графики
        for ax in self.axs:
            ax.clear()
        self.axs[0].plot(self.x_target, self.w_target, color="blue", label="Исходные")
        self.axs[0].set_title("Исходные перемещения")
        self.axs[0].grid(True)
        self.axs[1].plot(x_calc, w_calc, color="red", label="Восстановленные")
        self.axs[1].set_title("Восстановленные перемещения")
        self.axs[1].grid(True)
        self.canvas.draw()

        # 6. Формируем HTML-таблицу с итоговыми данными для вывода в текстовое поле
        forces_list = []
        moments_list = []
        for ld in best_loads:
            if ld['type'] == 'point':
                forces_list.append(f"P = {ld['value']:.3f} Н, a = {ld['position']:.3f} м")
            else:
                moments_list.append(f"M = {ld['value']:.3f} Нм, b = {ld['position']:.3f} м")

        colA = f"""
        <b>Число мод:</b> {self.N_modes}, <b>  Амплитуда:</b> {self.max_amplitude:.3f}<br>
        <b>Сил:</b> {N_F}, <b>  Моментов:</b> {N_M}<br>
        <b>Запусков:</b> {self.n_starts}<br>
        <b>Ошибка:</b> {best_error * 100:.4f}%<br>
        <b>Количество итераций:</b> {best_nit}<br>
        <b>Время (с):</b> {elapsed_time:.2f}
        """
        colB = "<b>Найденные силы:</b><br>" + "<br>".join(
            forces_list) if forces_list else "<b>Найденные силы:</b><br>(нет)"
        colC = "<b>Найденные моменты:</b><br>" + "<br>".join(
            moments_list) if moments_list else "<b>Найденные моменты:</b><br>(нет)"

        html_output = f"""
        <table width="100%" cellpadding="5" cellspacing="0">
          <tr valign="top">
            <td width="33%" style="border-right:1px solid #777;">{colA}</td>
            <td width="33%" style="border-right:1px solid #777;">{colB}</td>
            <td width="34%">{colC}</td>
          </tr>
        </table>
        """
        self.textOutput.setHtml(html_output)

        # 7. Сохраняем итоговые данные в файл data/data.json
        os.makedirs("data", exist_ok=True)
        filepath = os.path.join("data", "data.json")

        # Считываем существующие данные, если файл уже есть
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    logs = json.load(f)
                print(f"DEBUG: Файл {filepath} найден, данные будут дописаны.")
            except Exception as e:
                print(f"WARNING: Не удалось прочитать {filepath}: {e}")
                logs = []
        else:
            print(f"DEBUG: Файл {filepath} не найден, будет создан новый.")
            logs = []

        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_record = {
            "timestamp": now_str,
            "N_F": N_F,
            "N_M": N_M,
            "N_modes": self.N_modes,
            "n_starts": self.n_starts,
            "error": f"{best_error:.6e}",
            "iterations": best_nit,
            "time_s": f"{elapsed_time:.2f}"
        }
        logs.append(new_record)

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)
            print(f"DEBUG: Данные успешно записаны в {filepath}.")
        except Exception as e:
            print(f"ERROR: Не удалось записать данные в {filepath}: {e}")

    def _write_log_to_json(self, best_error, elapsed_time, N_F, N_M, N_modes, n_starts):
        """
        Сохраняет информацию об одном запуске в файл data/data.json в формате JSON.
        Если файл не существует — создаётся. Если существует — данные из него читаются,
        затем добавляется новая запись, и всё перезаписывается.
        """
        os.makedirs("data", exist_ok=True)
        filepath = os.path.join("data", "data.json")

        # Пробуем считать уже существующий список
        logs = []
        if os.path.exists(filepath):
            print(f"DEBUG: Найден файл {filepath}, читаем содержимое.")
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    logs = json.load(f)
            except Exception as e:
                print(f"WARNING: Не удалось считать JSON из {filepath}. Ошибка: {e}")
                logs = []
        else:
            print(f"DEBUG: Файл {filepath} не найден, будет создан заново.")

        # Формируем запись для добавления
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_record = {
            "timestamp": now_str,
            "N_F": N_F,
            "N_M": N_M,
            "N_modes": N_modes,
            "n_starts": n_starts,
            "error": f"{best_error:.6e}",
            "time_s": f"{elapsed_time:.2f}"
        }

        # Добавляем в список
        logs.append(new_record)

        # Пишем обратно
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)
            print(f"DEBUG: Запись новой записи в {filepath} успешно выполнена.")
        except Exception as e:
            print(f"ERROR: Не удалось записать JSON в {filepath}. Исключение: {e}")

    def _write_log_to_file(self, best_error, elapsed_time, N_F, N_M, N_modes, n_starts):
        """
        Запись итоговых данных в файл data/data.txt
        с дополнительным дебагом.
        """
        import os
        import datetime

        # Убедимся, что директория data/ существует, при необходимости создадим
        os.makedirs("data", exist_ok=True)

        filepath = os.path.join("data", "data.txt")

        # Проверим, существует ли файл
        if os.path.exists(filepath):
            print(f"DEBUG: Файл {filepath} уже существует, будем дописывать в конец.")
        else:
            print(f"DEBUG: Файл {filepath} не найден, будет создан заново.")

        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        log_text = (
            f"time: {now_str}\n"
            f"N_F={N_F}, N_M={N_M}, N_modes={N_modes}, n_starts={n_starts}\n"
            f"error={best_error:.6e}, time={elapsed_time:.2f} s\n"
            "----------------------------------\n"
        )

        try:
            with open(filepath, "a", encoding="utf-8") as f:
                f.write(log_text)
            print(f"DEBUG: Запись данных в файл {filepath} успешно выполнена.")
        except Exception as e:
            print(f"ERROR: Не удалось записать в файл {filepath}. Исключение:")
            print(e)

    # ------------------- Колбэки для многостарта и итераций -------------------
    def _iteration_callback(self, iter_num):
        """
        На каждой итерации trust-constr. iter_num / GLOBAL_MAX_ITER -> %.
        """
        percent = min(int(iter_num / GLOBAL_MAX_ITER * 100), 100)
        self.progressBar.setValue(percent)
        self.progressLabel.setText(f"Итерация: {percent}%")
        QApplication.processEvents()

    def _start_callback(self, start_i, total_starts):
        """
        Перед каждым запуском. Сбрасываем прогресс, пишем 'Запусков: i / total'.
        """
        self.progressBar.setValue(0)
        self.progressLabel.setText("Итерация: 0%")
        self.launchLabel.setText(f"Запусков: {start_i}/{total_starts}")
        QApplication.processEvents()


def main():


    app = QApplication(sys.argv)
    # qdarktheme.enable()  # при желании включить тёмную тему
    window = MainGUI()
    window.show()
    sys.exit(app.exec())




if __name__ == "__main__":
    main()
