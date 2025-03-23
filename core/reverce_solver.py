import numpy as np
from scipy.interpolate import UnivariateSpline

def generate_random_displacements(n, L, N_modes=5, max_amplitude=1.0):
    z = np.linspace(0, L, n + 2)
    w = np.zeros_like(z)
    for k in range(1, N_modes + 1):
        a_k = np.random.uniform(-max_amplitude, max_amplitude)
        w += a_k * np.sin(k * np.pi * z / L)
    return z, w


def compute_forces_and_moments(displacement_tuple, EI=1.0, smoothing_factor=0.01, segment_length=2.0,
                               force_threshold=10, moment_threshold=50):
    z, w = displacement_tuple
    spline = UnivariateSpline(z, w, s=smoothing_factor, k=5)

    w_pp = spline.derivative(n=2)
    w_ppp = spline.derivative(n=3)
    w_pppp = spline.derivative(n=4)

    M = -EI * w_pp(z)
    Q = -EI * w_ppp(z)
    q = EI * w_pppp(z)
    fine_z = np.linspace(z[0], z[-1], 10 * len(z))
    fine_q = EI * w_pppp(fine_z)
    fine_M = -EI * w_pp(fine_z)

    forces = []
    moments = []
    n_segments = int(np.ceil((z[-1] - z[0]) / segment_length))

    for i in range(n_segments):
        z_start = i * segment_length
        z_end = min((i + 1) * segment_length, z[-1])

        mask = (fine_z >= z_start) & (fine_z <= z_end)
        segment_z = fine_z[mask]
        segment_q = fine_q[mask]

        if len(segment_z) > 1:
            F = np.trapezoid(segment_q, segment_z)
            if abs(F) > force_threshold:
                z_F = np.trapezoid(segment_z * segment_q, segment_z) / F
                forces.append((z_F, F))

        segment_M = fine_M[mask]
        if len(segment_M) > 1:
            delta_M = np.max(segment_M) - np.min(segment_M)
            if abs(delta_M) > moment_threshold:
                z_M = (z_start + z_end) / 2
                moments.append((z_M, delta_M))

    return z, Q, M, q, forces, moments


