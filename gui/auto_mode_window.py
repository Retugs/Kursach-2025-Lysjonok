from PySide6.QtWidgets import QWidget, QVBoxLayout, QSplitter, QComboBox, QSlider, QLabel
from PySide6.QtCore import Qt
from gui.beam_visualization_widget import BeamVisualizationWidget
from gui.plot_widget import PlotWidget
from core.beam_solver import BeamSolver
from core.beam_load_simulator import BeamLoadSimulator
from core.beam_loader import BeamLoader

class AutoModeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Beam Simulator")
        self.setGeometry(1000, 500, 1200, 800)

        self.beam_length = 10

        self.loader = BeamLoader('data/profiles.json')
        self.profiles = self.loader.profiles
        self.profile_params = self.profiles.get(list(self.profiles.keys())[0], {
            "critical_stress": 250e6,
            "I": 12.3e-6,
            "h": 0.180
        })
        # BeamSolver
        self.solver = BeamSolver(self.beam_length, E=2e11, profile_params=self.profile_params)

        self.num_forces = 1
        self.num_moments = 1
        self.load_simulator = BeamLoadSimulator(beam_length=self.beam_length, num_forces=self.num_forces, num_moments=self.num_moments)
        self.load_simulator.update_signal.connect(self.update_calculations)
        self.load_simulator.start()

        self.beam_vis_widget = BeamVisualizationWidget()
        self.plot_widget = PlotWidget()

        main_splitter = QSplitter(Qt.Horizontal)

        control_panel = QWidget()
        control_layout = QVBoxLayout()

        self.profile_combo = QComboBox()
        self.profile_combo.addItems(self.profiles.keys())
        self.profile_combo.currentIndexChanged.connect(self.update_profile)
        control_layout.addWidget(QLabel("Профиль двутавра:"))
        control_layout.addWidget(self.profile_combo)

        self.force_slider = QSlider(Qt.Horizontal)
        self.force_slider.setRange(0, 10)
        self.force_slider.setValue(self.num_forces)
        self.force_slider.valueChanged.connect(self.update_num_forces)
        control_layout.addWidget(QLabel("Количество сил:"))
        control_layout.addWidget(self.force_slider)

        self.moment_slider = QSlider(Qt.Horizontal)
        self.moment_slider.setRange(0, 10)
        self.moment_slider.setValue(self.num_moments)
        self.moment_slider.valueChanged.connect(self.update_num_moments)
        control_layout.addWidget(QLabel("Количество моментов:"))
        control_layout.addWidget(self.moment_slider)

        control_panel.setLayout(control_layout)

        right_splitter = QSplitter(Qt.Vertical)
        right_splitter.setSizes([500, 700])
        right_splitter.addWidget(self.beam_vis_widget)
        right_splitter.addWidget(self.plot_widget)

        main_splitter.addWidget(control_panel)
        main_splitter.addWidget(right_splitter)
        main_splitter.setSizes([200, 1000])

        layout = QVBoxLayout()
        layout.addWidget(main_splitter)
        self.setLayout(layout)

    def update_profile(self):
        profile_name = self.profile_combo.currentText()
        self.profile_params = self.loader.get_profile(profile_name)
        self.solver = BeamSolver(self.beam_length, E=2e11, profile_params=self.profile_params)
        self.update_calculations(self.load_simulator.forces, self.load_simulator.moments)

    def update_num_forces(self, value):
        self.num_forces = value
        self.load_simulator.num_forces = value
        self.load_simulator.forces = self.load_simulator._generate_initial_loads('point', value)

    def update_num_moments(self, value):
        self.num_moments = value
        self.load_simulator.num_moments = value
        self.load_simulator.moments = self.load_simulator._generate_initial_loads('moment', value)

    def update_calculations(self, forces, moments):
        forces_dict = [{"type": "point", "value": f['value'], "position": f['position']} for f in forces]
        moments_dict = [{"type": "moment", "value": m['value'], "position": m['position']} for m in moments]
        loads = forces_dict + moments_dict

        x_moment, moments_data = self.solver.calculate_moments(loads)
        stresses = self.solver.calculate_stresses(moments_data)
        x_defl, deflections = self.solver.calculate_deflections_test(loads)
        x_transverse, transverse_forces = self.solver.calculate_transverse_forces(forces_dict)

        data = {
            'moment_diagram': (x_moment, moments_data),
            'deflections': (x_defl, deflections),
            'stresses': (x_moment, stresses),
            'transverse_forces': (x_transverse, transverse_forces),
            'critical_stress': self.profile_params['critical_stress'],
            'forces': forces_dict,
            'applied_moments': moments_dict
        }

        self.plot_widget.update_plots(data)
        self.beam_vis_widget.update_visualization(
            data['stresses'][0], data['stresses'][1],
            data['critical_stress'], data['forces'], data['applied_moments']
        )

    def update_calculations(self, forces, moments):
        """Обновляет расчёты и передаёт их в виджеты."""
        forces_dict = [{"type": "point", "value": f['value'], "position": f['position']} for f in forces]
        moments_dict = [{"type": "moment", "value": m['value'], "position": m['position']} for m in moments]

        loads = forces_dict + moments_dict

        x_moment, moments_data = self.solver.calculate_moments(loads)
        stresses = self.solver.calculate_stresses(moments_data)
        x_defl, deflections = self.solver.calculate_deflections_test(loads)
        x_transverse, transverse_forces = self.solver.calculate_transverse_forces(forces_dict)

        data = {
            'moment_diagram': (x_moment, moments_data),
            'deflections': (x_defl, deflections),
            'stresses': (x_moment, stresses),
            'transverse_forces': (x_transverse, transverse_forces),
            'critical_stress': self.profile_params['critical_stress'],
            'forces': forces_dict,
            'applied_moments': moments_dict
        }

        self.plot_widget.update_plots(data)
        self.beam_vis_widget.update_visualization(
            data['stresses'][0], data['stresses'][1],
            data['critical_stress'], data['forces'], data['applied_moments']
        )

    def closeEvent(self, event):
        """Останавливает симулятор при закрытии окна."""
        self.load_simulator.stop()
        event.accept()