import numpy as np


def generate_random_displacements(n, L, N_modes=5, max_amplitude=1.0):
    """
    Генерирует случайные перемещения для балки с нулевыми перемещениями на концах,
    используя суперпозицию синусоидальных мод.

    :param n: количество внутренних точек (всего точек будет n+2, включая концы)
    :param L: длина балки
    :param N_modes: количество мод для суперпозиции (по умолчанию 5)
    :param max_amplitude: максимальная амплитуда для случайных коэффициентов (по умолчанию 1.0)
    :return: кортеж (z, w), где z — массив координат точек, w — массив перемещений
    """
    # Создаём массив координат точек от 0 до L
    z = np.linspace(0, L, n + 2)

    # Инициализируем массив перемещений нулями
    w = np.zeros_like(z)

    # Генерируем перемещения как суперпозицию синусоидальных мод
    for k in range(1, N_modes + 1):
        # Случайный коэффициент для каждой моды
        a_k = np.random.uniform(-max_amplitude, max_amplitude)
        # Добавляем вклад моды: a_k * sin(k * pi * z / L)
        w += a_k * np.sin(k * np.pi * z / L)

    return z, w


# Пример использования
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    # Параметры
    n = 100  # количество внутренних точек
    L = 10.0  # длина балки
    N_modes = 3  # количество мод
    max_amplitude = 0.1  # максимальная амплитуда

    # Генерируем перемещения
    z, w = generate_random_displacements(n, L, N_modes, max_amplitude)

    # Визуализация
    plt.plot(z, w)
    plt.xlabel('z (координата вдоль балки)')
    plt.ylabel('w(z) (перемещение)')
    plt.title('Случайные перемещения балки')
    plt.grid(True)
    plt.show()