import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

# Данные
years = np.array([2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024])
values = np.array([0.296327654, 0.299122714, 0.30203823, 0.305529126, 0.309354805,
                   0.313163482, 0.317697228, 0.323551543, 0.329432163, 0.334495533, 0.338575797])

# Интерполяция
interp_func = interp1d(years, values, kind='linear', fill_value="extrapolate")

# Создание точек для графика
years_extended = np.arange(2014, 2035, 1)
values_extended = interp_func(years_extended)

# Умножение интерполированных значений на 1000
values_extended *= 1000

# Установка темного стиля
plt.style.use("dark_background")

# Построение графика
plt.figure(figsize=(10, 5))
plt.plot(years_extended[:11], values_extended[:11], label="Фактические данные", color="cyan", linestyle="-")
plt.plot(years_extended[10:], values_extended[10:], label="Прогноз", color="orange", linestyle="--")

# Оформление графика
plt.xlabel("Год", color="white")
plt.ylabel("Количество автомобилей на 1000 человек", color="white")
plt.title("Прогноз", color="white")
plt.legend()
plt.grid(True, linestyle="--", alpha=0.5)

# Установка темно-серого фона
plt.gca().set_facecolor("#303030")

# Отображение графика
plt.show()