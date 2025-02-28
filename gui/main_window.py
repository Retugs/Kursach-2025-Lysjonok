from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QSplitter
from PySide6.QtCore import Qt
from gui.controls import ControlPanel
from gui.plot_widget import PlotWidget
from test_files.important_file import W1djet
from gui.beam_visualization_widget import BeamVisualizationWidget
from PySide6.QtCore import QLocale

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Beam Simulator")
        self.setGeometry(1000, 500, 1200, 800)

        QLocale.setDefault(QLocale(QLocale.Russian, QLocale.Russia))

        # Создаем центральный виджет и главный layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Главный горизонтальный разделитель (левая и правая части)
        main_splitter = QSplitter(Qt.Horizontal)

        # Левая часть - вертикальный layout
        left_layout_widget = QWidget()
        left_layout = QVBoxLayout(left_layout_widget)

        # Добавляем новый виджет W1djet внизу слева (изначально скрытый)
        self.w1djet = W1djet()
        self.w1djet.setVisible(False)  # Скрываем виджет при старте

        # Панель управления, передаём W1djet внутрь
        self.control_panel = ControlPanel(self.w1djet)
        left_layout.addWidget(self.control_panel)
        left_layout.addWidget(self.w1djet)

        # Правая часть - вертикальный разделитель (балка + графики)
        right_splitter = QSplitter(Qt.Vertical)
        self.beam_vis_widget = BeamVisualizationWidget()
        self.plot_widget = PlotWidget()

        # Добавляем виджеты в правый вертикальный разделитель
        right_splitter.addWidget(self.beam_vis_widget)
        right_splitter.addWidget(self.plot_widget)

        # Настройка пропорций для правого разделителя
        right_splitter.setSizes([250, 350])

        # Собираем главный разделитель
        main_splitter.addWidget(left_layout_widget)
        main_splitter.addWidget(right_splitter)

        # Настройка пропорций главного разделителя
        main_splitter.setSizes([300, 900])  # 300px - левая часть, остальное - правая

        main_layout.addWidget(main_splitter)

        # Подключение сигналов
        self.control_panel.update_signal.connect(self.update_visualizations)

    def update_visualizations(self, data):
        self.plot_widget.update_plots(data)  # Графики без напряжений
        if 'stresses' in data and 'critical_stress' in data and 'forces' in data:
            x, stresses = data['stresses']
            critical_stress = data['critical_stress']
            forces = data['forces']
            moments = data['applied_moments']
            self.beam_vis_widget.update_visualization(x, stresses, critical_stress, forces, moments)
        else:
            print("Ошибка: данные о напряжениях, критическом напряжении или нагрузках отсутствуют.")

    def closeEvent(self, event):
        event.accept()