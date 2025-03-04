from PySide6.QtWidgets import QWidget, QPushButton, QSlider, QLabel, QComboBox, QHBoxLayout, QFormLayout, QSpacerItem, QSizePolicy
from PySide6.QtCore import Signal, Qt
from core.beam_loader import BeamLoader
from core.beam_solver import BeamSolver

class ControlPanel(QWidget):
    update_signal = Signal(dict)

    def __init__(self, w1djet, parent=None):
        super(ControlPanel, self).__init__(parent)
        self.w1djet = w1djet

        layout = QFormLayout(self)

        self.loader = BeamLoader('data/profiles.json')
        self.profile_combo = QComboBox()
        self.profile_combo.addItems(self.loader.profiles.keys())
        layout.addRow("Профиль:", self.profile_combo)

        self.force_value_slider = QSlider(Qt.Horizontal)
        self.force_value_slider.setRange(-10000, 10000)
        self.force_value_slider.setValue(0)
        self.force_label = QLabel("0 Н")

        self.force_position_slider = QSlider(Qt.Horizontal)
        self.force_position_slider.setRange(0, 100)
        self.force_position_slider.setValue(50)
        self.position_label = QLabel("50%")

        force_layout = QHBoxLayout()
        force_layout.addWidget(self.force_value_slider)
        force_layout.addWidget(self.force_label)
        layout.addRow("Величина нагрузки:", force_layout)

        position_layout = QHBoxLayout()
        position_layout.addWidget(self.force_position_slider)
        position_layout.addWidget(self.position_label)
        layout.addRow("Положение нагрузки:", position_layout)

        load_buttons_layout = QHBoxLayout()
        self.add_load_button = QPushButton("Добавить нагрузку")
        self.remove_load_button = QPushButton("Удалить нагрузку")
        load_buttons_layout.addWidget(self.add_load_button)
        load_buttons_layout.addWidget(self.remove_load_button)
        layout.addRow(load_buttons_layout)

        self.moment_value_slider = QSlider(Qt.Horizontal)
        self.moment_value_slider.setRange(-10000, 10000)
        self.moment_value_slider.setValue(0)
        self.moment_value_label = QLabel("0 Н·м")

        self.moment_position_slider = QSlider(Qt.Horizontal)
        self.moment_position_slider.setRange(0, 100)
        self.moment_position_slider.setValue(50)
        self.moment_position_label = QLabel("50%")

        moment_value_layout = QHBoxLayout()
        moment_value_layout.addWidget(self.moment_value_slider)
        moment_value_layout.addWidget(self.moment_value_label)
        layout.addRow("Величина момента:", moment_value_layout)

        moment_position_layout = QHBoxLayout()
        moment_position_layout.addWidget(self.moment_position_slider)
        moment_position_layout.addWidget(self.moment_position_label)
        layout.addRow("Положение момента:", moment_position_layout)

        moment_buttons_layout = QHBoxLayout()
        self.add_moment_button = QPushButton("Добавить момент")
        self.remove_moment_button = QPushButton("Удалить момент")
        moment_buttons_layout.addWidget(self.add_moment_button)
        moment_buttons_layout.addWidget(self.remove_moment_button)
        layout.addRow(moment_buttons_layout)

        layout.addItem(QSpacerItem(0, 15, QSizePolicy.Minimum, QSizePolicy.Fixed))

        self.create_w1djet = QPushButton("-------------")
        layout.addRow(self.create_w1djet)

        self.forces = []
        self.moments = []
        self.length = 5.0
        self.E = 2e11

        self.add_load_button.clicked.connect(self.add_load)
        self.remove_load_button.clicked.connect(self.remove_load)
        self.force_value_slider.valueChanged.connect(self.update_force_label)
        self.force_position_slider.valueChanged.connect(self.update_position_label)
        self.profile_combo.currentIndexChanged.connect(self.update_data)
        self.add_moment_button.clicked.connect(self.add_moment)
        self.moment_value_slider.valueChanged.connect(self.update_moment_value_label)
        self.moment_position_slider.valueChanged.connect(self.update_moment_position_label)
        self.remove_moment_button.clicked.connect(self.remove_moment)
        self.create_w1djet.clicked.connect(self.game)

    def game(self):
        self.w1djet.setVisible(not self.w1djet.isVisible())


    def add_load(self):
        F = self.force_value_slider.value()
        a = (self.force_position_slider.value() / 100.0) * self.length
        self.forces.append({'type': 'point', 'value': F, 'position': a})
        self.update_data()

    def add_moment(self):
        M = self.moment_value_slider.value()
        a = (self.moment_position_slider.value() / 100.0) * self.length
        self.moments.append({'type': 'moment', 'value': M, 'position': a})
        self.update_data()

    def remove_load(self):
        if self.forces:
            self.forces.pop()
            self.update_data()

    def remove_moment(self):
        if self.moments:
            self.moments.pop()
            self.update_data()

    def update_force_label(self, value):
        self.force_label.setText(f"{value} Н")

    def update_position_label(self, value):
        self.position_label.setText(f"{value}%")

    def update_moment_value_label(self, value):
        self.moment_value_label.setText(f"{value} Н·м")

    def update_moment_position_label(self, value):
        self.moment_position_label.setText(f"{value}%")

    def update_data(self):
        try:
            profile_name = self.profile_combo.currentText()
            profile_params = self.loader.get_profile(profile_name)

            solver = BeamSolver(self.length, self.E, profile_params)

            combined_loads = self.forces + self.moments
            x_moment, moments = solver.calculate_moments(combined_loads, num_points=1000)
            stresses = solver.calculate_stresses(moments)
            x_defl, deflections = solver.calculate_deflections_test(combined_loads)
            x_transverse, transverse_forces = solver.calculate_transverse_forces(self.forces)

            data = {
                'moment_diagram': (x_moment, moments),  # Эпюра моментов
                'deflections': (x_defl, deflections),
                'stresses': (x_moment, stresses),
                'transverse_forces': (x_transverse, transverse_forces),
                'critical_stress': profile_params['critical_stress'],
                'forces': self.forces,
                'applied_moments': self.moments  # Список приложенных моментов
            }
            self.update_signal.emit(data)
        except Exception as e:
            print(f"Ошибка при обновлении данных: {e}")