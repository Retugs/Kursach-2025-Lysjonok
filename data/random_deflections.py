import numpy as np

def generate_random_displacements(n, L, N_modes=5, max_amplitude=1.0):
    z = np.linspace(0, L, n + 2)
    w = np.zeros_like(z)

    for k in range(1, N_modes + 1):
        a_k = np.random.uniform(-max_amplitude, max_amplitude)
        w += a_k * np.sin(k * np.pi * z / L)
    return z, w

if __name__ == "__main__":
    import matplotlib.pyplot as plt

    n = 100
    L = 10.0
    N_modes = 3
    max_amplitude = 0.1

    z, w = generate_random_displacements(n, L, N_modes, max_amplitude)

    plt.plot(z, w)
    plt.xlabel('z (координата вдоль балки)')
    plt.ylabel('w(z) (перемещение)')
    plt.title('Случайные перемещения балки')
    plt.grid(True)
    plt.show()