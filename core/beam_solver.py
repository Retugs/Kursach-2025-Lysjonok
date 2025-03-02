import numpy as np
from scipy.integrate import cumtrapz
from scipy.interpolate import interp1d


class BeamSolver:
    def __init__(self, length, E, profile_params):
        self.length = length
        self.E = E
        self.I = profile_params['I']
        self.h = profile_params['h']

    def calculate_moments(self, loads, num_points=10000):

        point_forces = [load for load in loads if load['type'] == 'point']
        moments = [load for load in loads if load['type'] == 'moment']

        sum_F = sum(force['value'] for force in point_forces)
        sum_M = sum(moment['value'] for moment in moments)
        sum_M_F = sum(force['value'] * force['position'] for force in point_forces)

        R_B = -(sum_M_F + sum_M) / self.length
        R_A = -sum_F - R_B

        all_forces = [
                         {'type': 'point', 'value': R_A, 'position': 0},
                         {'type': 'point', 'value': R_B, 'position': self.length}
                     ] + point_forces

        x = np.linspace(0, self.length, num_points)
        M = np.zeros_like(x)

        for force in all_forces:
            F = force['value']
            a = force['position']
            M += np.where(x > a, F * (x - a), 0)

        for moment in moments:
            M_val = moment['value']
            a = moment['position']
            M += np.where(x >= a, -M_val, 0)

        return x, M

    def calculate_stresses(self, moments):
        y = self.h / 2
        stresses = moments * y / self.I
        return stresses

    def calculate_deflections(self, loads):
        x = np.linspace(0, self.length, 10000)
        w = np.zeros_like(x)
        for load in loads:
            if load['type'] == 'point':
                F = load['value']
                a = load['position']
                w += (F * a * (self.length - a) * (self.length ** 2 - a ** 2 - (self.length - a) ** 2)) / (
                        6 * self.E * self.I * self.length
                ) * (
                         np.where(x < a, x * (self.length - a), a * (self.length - x))
                     )
        return x, w

    def calculate_deflections_test(self, loads, num_points=10000):
        x, M = self.calculate_moments(loads, num_points=num_points)

        M_interp = interp1d(x, M, kind='cubic', fill_value="extrapolate")

        EI = self.E * self.I

        f_vals = -M_interp(x) / EI

        dw_dx = cumtrapz(f_vals, x, initial=0)

        w = cumtrapz(dw_dx, x, initial=0)

        w_L = w[-1]
        correction = np.linspace(0, w_L, num_points)
        w_corrected = w - correction

        return x, w_corrected

    def calculate_transverse_forces(self, forces, num_points=10000):
        sum_forces = sum(force['value'] for force in forces)
        R_A = -sum_forces / 2

        x_vals = np.linspace(0, self.length, num_points)
        Q_vals = np.zeros_like(x_vals)

        for i, x in enumerate(x_vals):
            Q = R_A
            for force in forces:
                if force['position'] <= x:
                    Q += force['value']
            Q_vals[i] = Q
        return x_vals, Q_vals