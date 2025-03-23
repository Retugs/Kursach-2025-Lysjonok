import matplotlib.pyplot as plt
import numpy as np


def calculate_break_even_months(initial_investment, monthly_revenue, monthly_expenses):
    """
    Рассчитывает срок окупаемости проекта в месяцах.

    Накопленная прибыль рассчитывается как:
      (monthly_revenue - monthly_expenses) * x - initial_investment = 0

    :param initial_investment: Первоначальные вложения (USD)
    :param monthly_revenue: Ежемесячный доход (USD)
    :param monthly_expenses: Ежемесячные эксплуатационные расходы (USD)
    :return: Срок окупаемости (в месяцах)
    :raises ValueError: Если чистая прибыль за месяц (monthly_revenue - monthly_expenses) <= 0.
    """
    net_monthly_profit = monthly_revenue - monthly_expenses
    if net_monthly_profit <= 0:
        raise ValueError("Ежемесячный доход не покрывает расходы. Окупаемость невозможна.")
    return initial_investment / net_monthly_profit


def main():
    # Исходные данные
    initial_investment = 18150  # USD - первоначальные вложения
    monthly_revenue = 1366.67  # USD - ежемесячный доход (от бронирований, абонементов, рекламы и аналитики)
    monthly_expenses = 391.67  # USD - ежемесячные эксплуатационные расходы (~4700 USD/год)

    net_monthly_profit = monthly_revenue - monthly_expenses

    try:
        break_even_months = calculate_break_even_months(initial_investment, monthly_revenue, monthly_expenses)
        print(f"Срок окупаемости проекта: {break_even_months:.1f} месяцев")
    except ValueError as e:
        print("Ошибка:", e)
        return

    # Настройка темного стиля для графика
    plt.style.use('dark_background')

    # Подготовка данных: создаем массив месяцев и рассчитываем накопленную чистую прибыль,
    # где начальное значение = -initial_investment (т.е. расходы)
    x_max = int(np.ceil(break_even_months * 1.5))
    x = np.linspace(0, x_max, num=500)
    y = net_monthly_profit * x - initial_investment

    # Построение графика
    plt.figure(figsize=(10, 6))
    plt.plot(x, y, label='Накопленная чистая прибыль', color='cyan', linewidth=2)

    # Отмечаем точку окупаемости (когда накопленная прибыль = 0)
    plt.scatter(break_even_months, 0, color='yellow', s=100, zorder=5, label='Точка окупаемости')
    plt.axvline(x=break_even_months, color='yellow', linestyle='--', linewidth=1)

    # Добавляем четкую горизонтальную линию для нулевой прибыли
    plt.axhline(y=0, color='white', linestyle='-', linewidth=2, label='Нулевая прибыль')

    plt.title("График окупаемости проекта", fontsize=16)
    plt.xlabel("Время (месяцы)", fontsize=14)
    plt.ylabel("Накопленная чистая прибыль (USD)", fontsize=14)
    plt.legend()
    plt.grid(True, color='gray', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    main()