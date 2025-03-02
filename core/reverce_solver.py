import numpy as np
from scipy.interpolate import UnivariateSpline
import matplotlib.pyplot as plt
from data.random_deflections import generate_random_displacements


def compute_forces_and_moments(displacement_tuple, EI=1.0, smoothing_factor=0.01, segment_length=2.0,
                               force_threshold=10, moment_threshold=50):
    """
    Вычисляет сосредоточенные силы и моменты с учетом их точного положения через центр "масс".

    Аргументы:
        displacement_tuple -- кортеж (z, w) с координатами и перемещениями
        EI                -- жесткость балки (Н·м²)
        smoothing_factor  -- коэффициент сглаживания сплайна
        segment_length    -- длина сегмента для вычисления сосредоточенных сил и моментов (м)
        force_threshold   -- порог для обнаружения сосредоточенных сил (Н)
        moment_threshold  -- порог для обнаружения сосредоточенных моментов (Н·м)

    Возвращает:
        z, Q, M, q, forces, moments -- координаты, силы, моменты, нагрузка и списки сосредоточенных сил и моментов
    """
    z, w = displacement_tuple

    # Сплайн-интерполяция с минимальным сглаживанием
    spline = UnivariateSpline(z, w, s=smoothing_factor, k=5)

    # Вычисление производных
    w_pp = spline.derivative(n=2)  # Вторая производная
    w_ppp = spline.derivative(n=3)  # Третья производная
    w_pppp = spline.derivative(n=4)  # Четвертая производная

    # Вычисление функций
    M = -EI * w_pp(z)  # Изгибающий момент
    Q = -EI * w_ppp(z)  # Поперечная сила
    q = EI * w_pppp(z)  # Распределенная нагрузка

    # Увеличение плотности точек для точного интегрирования
    fine_z = np.linspace(z[0], z[-1], 10 * len(z))
    fine_q = EI * w_pppp(fine_z)
    fine_M = -EI * w_pp(fine_z)

    # Замена q(z) на сосредоточенные силы с учетом центра "масс"
    forces = []
    moments = []
    n_segments = int(np.ceil((z[-1] - z[0]) / segment_length))

    for i in range(n_segments):
        z_start = i * segment_length
        z_end = min((i + 1) * segment_length, z[-1])

        # Для сил
        mask = (fine_z >= z_start) & (fine_z <= z_end)
        segment_z = fine_z[mask]
        segment_q = fine_q[mask]

        if len(segment_z) > 1:
            F = np.trapezoid(segment_q, segment_z)
            if abs(F) > force_threshold:
                z_F = np.trapezoid(segment_z * segment_q, segment_z) / F
                forces.append((z_F, F))

        # Для моментов: максимальный скачок в M(z) на сегменте
        segment_M = fine_M[mask]
        if len(segment_M) > 1:
            delta_M = np.max(segment_M) - np.min(segment_M)
            if abs(delta_M) > moment_threshold:
                z_M = (z_start + z_end) / 2  # Пока используем середину сегмента
                moments.append((z_M, delta_M))

    return z, Q, M, q, forces, moments


# Пример использования
if __name__ == "__main__":
    # Параметры
    n = 200  # Увеличиваем количество точек для большей детализации
    L = 10.0  # Длина балки (м)
    N_modes = 5  # Количество мод
    max_amplitude = 0.1  # Максимальная амплитуда (м)
    EI = 1e6  # Жесткость балки (Н·м²)
    smoothing_factor = 0.01  # Уменьшаем сглаживание
    segment_length = 2.0  # Длина сегмента (м)
    force_threshold = 1e3  # Порог для сил (Н)
    moment_threshold = 5e3  # Порог для моментов (Н·м)

    # Генерация перемещений
    displacement_tuple = generate_random_displacements(n, L, N_modes, max_amplitude)
    z, w = displacement_tuple

    # Вычисление усилий
    z, Q, M, q, forces, moments = compute_forces_and_moments(
        displacement_tuple, EI, smoothing_factor, segment_length, force_threshold, moment_threshold
    )

    # Визуализация
    plt.figure(figsize=(12, 8))

    plt.subplot(4, 1, 1)
    plt.plot(z, w, label='w(z)')
    plt.title('Перемещения w(z)')
    plt.xlabel('z (м)')
    plt.ylabel('w (м)')
    plt.grid(True)
    plt.legend()

    plt.subplot(4, 1, 2)
    plt.plot(z, M, label='M(z)')
    for z_m, M_conc in moments:
        plt.axvline(z_m, color='b', linestyle='--', label=f'Момент {M_conc:.2f} Н·м' if z_m == moments[0][0] else "")
    plt.title('Изгибающий момент M(z) и сосредоточенные моменты')
    plt.xlabel('z (м)')
    plt.ylabel('M (Н·м)')
    plt.grid(True)
    plt.legend()

    plt.subplot(4, 1, 3)
    plt.plot(z, Q, label='Q(z)')
    plt.title('Поперечная сила Q(z)')
    plt.xlabel('z (м)')
    plt.ylabel('Q (Н)')
    plt.grid(True)
    plt.legend()

    plt.subplot(4, 1, 4)
    plt.plot(z, q, label='q(z)')
    for z_f, F in forces:
        plt.axvline(z_f, color='r', linestyle='--', label=f'Сила {F:.2f} Н' if z_f == forces[0][0] else "")
    plt.title('Распределенная нагрузка q(z) и сосредоточенные силы')
    plt.xlabel('z (м)')
    plt.ylabel('q (Н/м)')
    plt.grid(True)
    plt.legend()

    plt.tight_layout()
    plt.show()

    # Вывод сосредоточенных сил и моментов
    print("Сосредоточенные силы:")
    for z_f, F in forces:
        print(f"Сила {F:.2f} Н в точке z = {z_f:.2f} м")

    print("Сосредоточенные моменты:")
    for z_m, M_conc in moments:
        print(f"Момент {M_conc:.2f} Н·м в точке z = {z_m:.2f} м")