import numpy as np
import random
from scipy.optimize import minimize


# -------------------------------------------------------------
# 1. Генерация "целевых" перемещений (суперпозиция синусоид)
# -------------------------------------------------------------
def generate_random_displacements(n, L, N_modes=5, max_amplitude=1.0):
    """
    Генерирует массив координат z и соответствующие перемещения w(z).
    """
    z = np.linspace(0, L, n + 2)
    w = np.zeros_like(z)
    for k in range(1, N_modes + 1):
        a_k = np.random.uniform(-max_amplitude, max_amplitude)
        w += a_k * np.sin(k * np.pi * z / L)
    return z, w


# -------------------------------------------------------------
# 2. Формулы для прогиба шарнирно-опёртой балки
#    при сосредоточенной силе F или сосредоточенном моменте M
# -------------------------------------------------------------
def deflection_single_force(x, F, a, E, I, L):
    """
    Прогиб от сосредоточенной силы F, приложенной в точке a,
    для шарнирно-опертой балки на промежутке [0, L].
    Формулы классические сопромата.
    """
    # Удобно рассматривать отдельно области 0 <= x <= a и a <= x <= L.
    # Для x < a и x >= a используем стандартные выражения.
    # Ниже представлены обобщенные формулы (единичный пример).
    # Реально в сопроме есть несколько разных форм, в зависимости от расположения x и a.
    # Здесь — простой пример "собранный" из известных таблиц влияния.

    if x < 0 or x > L:
        return 0.0

    if x <= a:
        # Формула для 0 <= x <= a
        return F * x * (L ** 2 - x ** 2 - 2 * a * L + a ** 2 + 2 * a * x) / (6 * E * I * L)
    else:
        # Формула для a <= x <= L
        return F * a * (L - x) * (L ** 2 - (L - x) ** 2 - 2 * (L - a) * L + (L - a) ** 2 + 2 * (L - a) * (L - x)) / (
                    6 * E * I * L * a)
        # В учебниках эта часть обычно приводится в более компактном виде, но общая суть такова.


def deflection_single_moment(x, M, b, E, I, L):
    """
    Прогиб от сосредоточенного момента M, приложенного в точке b,
    для шарнирно-опертой балки на промежутке [0, L].
    """
    # Аналогично для момента. Для x < b и x >= b формулы разные.

    if x < 0 or x > L:
        return 0.0

    if x <= b:
        # 0 <= x <= b
        # Примерная формула (может отличаться в зависимости от соглашений о знаках)
        return M * x * (L ** 2 - x ** 2) / (6 * E * I * L)
    else:
        # b <= x <= L
        return M * b * (L - x) * (L ** 2 - (L - x) ** 2) / (6 * E * I * L * b)


def compute_deflection_from_loads(z_array, params, E, I, L, N_F, N_M):
    """
    Суммарный прогиб балки от заданного набора сил и моментов.
    params = [F1, a1, F2, a2, ..., FN_F, aN_F, M1, b1, M2, b2, ..., MN_M, bN_M]

    N_F - количество сил
    N_M - количество моментов

    Возвращает массив того же размера, что и z_array, со значениями прогибов.
    """
    w_calc = np.zeros_like(z_array)

    # Извлекаем F_k, a_k из params
    # Первая часть params: F1, a1, F2, a2, ...
    # Вторая часть: M1, b1, M2, b2, ...

    # Индекс в params, где начинаются моменты:
    moment_index = 2 * N_F  # т.к. на каждую силу 2 параметра (F, a)

    # Силы
    for i in range(N_F):
        F_i = params[2 * i]
        a_i = params[2 * i + 1]

        # Добавляем вклад в прогиб
        for j, x in enumerate(z_array):
            w_calc[j] += deflection_single_force(x, F_i, a_i, E, I, L)

    # Моменты
    for i in range(N_M):
        idx = moment_index + 2 * i
        M_i = params[idx]
        b_i = params[idx + 1]

        for j, x in enumerate(z_array):
            w_calc[j] += deflection_single_moment(x, M_i, b_i, E, I, L)

    return w_calc


# -------------------------------------------------------------
# 3. Целевая функция для оптимизации
# -------------------------------------------------------------
def objective_function(params, z_array, w_target, E, I, L, N_F, N_M):
    """
    Вычисляет сумму квадратов отклонений между w_calc и w_target.
    params - вектор оптимизируемых параметров.
    """
    w_calc = compute_deflection_from_loads(z_array, params, E, I, L, N_F, N_M)
    return np.sum((w_calc - w_target) ** 2)


# -------------------------------------------------------------
# 4. Основная функция,
#    демонстрирующая процесс оптимизации
# -------------------------------------------------------------
def main_optimization_example():
    # ПАРАМЕТРЫ БАЛКИ И МАТЕРИАЛА
    L = 10.0  # длина балки
    E = 2.0e8  # модуль Юнга (к примеру)
    I = 1.0e-4  # момент инерции

    # ПАРАМЕТРЫ ГЕНЕРАЦИИ СЛУЧАЙНЫХ ПЕРЕМЕЩЕНИЙ
    n = 200
    N_modes = 3
    max_amplitude = 0.05

    # Сгенерируем "целевые" перемещения
    z_array, w_target = generate_random_displacements(n, L, N_modes, max_amplitude)

    # ПАРАМЕТРЫ ДЛЯ ОПТИМИЗАЦИИ
    N_F = 3  # Количество сил (можно варьировать)
    N_M = 2  # Количество моментов (можно варьировать)

    # Общая длина вектора параметров: 2*N_F + 2*N_M
    # (каждая сила: (F, a), каждый момент: (M, b))
    num_params = 2 * (N_F + N_M)

    # Начальное приближение для params:
    # Допустим, все силы и моменты = 0, а координаты = равномерное распределение
    # (просто как пример)
    init_params = []

    # Силы
    for i in range(N_F):
        init_params.append(0.0)  # F_i
        init_params.append((i + 1) / (N_F + 1) * L)  # a_i (равномерно по длине)

    # Моменты
    for i in range(N_M):
        init_params.append(0.0)  # M_i
        init_params.append((i + 1) / (N_M + 1) * L)  # b_i

    init_params = np.array(init_params, dtype=float)

    # Зададим bounds для параметров:
    # - Силы (F) пусть будут в диапазоне [-10000, 10000] (пример)
    # - Координаты (a) в диапазоне [0, L]
    # - Моменты (M) в диапазоне [-10000, 10000]
    # - Координаты (b) в диапазоне [0, L]

    bounds = []
    for i in range(N_F):
        # F_i
        bounds.append((-1e4, 1e4))
        # a_i
        bounds.append((0.0, L))
    for i in range(N_M):
        bounds.append((-1e4, 1e4))
        bounds.append((0.0, L))

    # Запустим оптимизацию методом 'trust-constr' или 'SLSQP'
    # (можно экспериментировать)

    result = minimize(
        objective_function,
        init_params,
        args=(z_array, w_target, E, I, L, N_F, N_M),
        method='trust-constr',  # или 'SLSQP'
        bounds=bounds,
        options={'maxiter': 1000, 'verbose': 1}
    )

    opt_params = result.x
    final_error = result.fun

    print("\n--- РЕЗУЛЬТАТ ОПТИМИЗАЦИИ ---")
    print(f"Статус: {result.message}")
    print(f"Число итераций: {result.niter}")
    print(f"Итоговая невязка (сумма квадратов): {final_error:.6f}")

    # Разберёмся, что именно получилось:
    # opt_params = [F1, a1, F2, a2, ..., FN_F, aN_F, M1, b1, M2, b2, ..., MN_M, bN_M]
    # Сформируем удобный вывод
    forces_str = []
    moments_str = []

    idx = 0
    for i in range(N_F):
        F_i = opt_params[idx]
        a_i = opt_params[idx + 1]
        forces_str.append(f"P{i + 1} = {F_i:.3f} Н, a = {a_i:.3f} м")
        idx += 2

    for i in range(N_M):
        M_i = opt_params[idx]
        b_i = opt_params[idx + 1]
        moments_str.append(f"M{i + 1} = {M_i:.3f} Нм, b = {b_i:.3f} м")
        idx += 2

    print("\nНайденные силы:")
    for fs in forces_str:
        print("  " + fs)

    print("\nНайденные моменты:")
    for ms in moments_str:
        print("  " + ms)

    # При желании можем построить график (если нужно)
    # Сравним w_target и w_calc:
    w_calc_opt = compute_deflection_from_loads(z_array, opt_params, E, I, L, N_F, N_M)

    # Печать, например, разности:
    diff = w_calc_opt - w_target
    print(f"\nСреднеквадратичная ошибка: {np.sqrt(np.mean(diff ** 2)):.6e}")

    # Если нужно – вернём результат
    return (z_array, w_target, w_calc_opt, opt_params, result)


# -------------------------------------------------------------
# 5. Запуск примера
# -------------------------------------------------------------
if __name__ == "__main__":
    main_optimization_example()
