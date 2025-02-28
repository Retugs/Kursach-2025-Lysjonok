import numpy as np
import matplotlib.pyplot as plt


def calculate_stresses(length, loads, num_points=1000):
    """
    Рассчитывает поперечные силы Q(x) вдоль балки.

    :param length: Длина балки
    :param loads: Список нагрузок [{'type': 'point', 'value': Q, 'position': a}]
    :param num_points: Количество точек дискретизации
    :return: Кортеж (x, Q), где x - массив координат, Q - массив значений поперечной силы
    """

    # 1. Определяем реакции опор с учетом равномерного распределения
    sum_forces = sum(load['value'] for load in loads)  # Сумма всех сил с учетом знака
    R_A = -sum_forces / 2  # Реакция в левой опоре

    # 2. Вычисляем эпюру поперечных сил
    x_vals = np.linspace(0, length, num_points)
    Q_vals = np.zeros_like(x_vals)

    for i, x in enumerate(x_vals):
        Q = R_A  # Начинаем с реакции в A

        # Добавляем вклад каждой нагрузки
        for load in loads:
            if load['position'] <= x:
                Q += load['value']

        Q_vals[i] = Q

    return x_vals, Q_vals

