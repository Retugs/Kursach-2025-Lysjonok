import sympy


def solve_and_find_extrema(E, I, a, q):
    """
    1) Решает систему уравнений для A, B, C:
       y(2a) = 0, y(3a) = 0, 3B - A = 4*a*q
    2) Составляет выражение y(t), находит его локальные экстремумы
       (первая производная = 0) на [0, 3a], и выводит t и y(t).
    """

    # --- 1. Решаем систему для A, B, C --------------------------------------
    # Объявляем искомые переменные
    A, B, C = sympy.symbols('A B C', real=True)
    # Определяем символическую переменную t
    t = sympy.Symbol('t', real=True)

    # Записываем EI*y(t) = ... (как F(t), чтоб было удобнее)
    F = (
            E * I * C * t
            + 2 * q * a ** 2 * (1 / sympy.Integer(2)) * t ** 2
            - B * (1 / sympy.Integer(6)) * t ** 3
            + A * (1 / sympy.Integer(6)) * (t - 2 * a) ** 3
            - 2 * q * a * (1 / sympy.Integer(6)) * (t - sympy.Rational(5, 2) * a) ** 3
            + 2 * q * (1 / sympy.Integer(24)) * t ** 4
            - 2 * q * (1 / sympy.Integer(24)) * (t - a) ** 4
    )
    # Собственно y(t) = F(t)/(E*I), но для условий y(…)=0 достаточно F(…)=0

    # Уравнения:
    # 1) y(2a) = 0  -> F(2a) = 0
    eq1 = F.subs(t, 2 * a)
    # 2) y(3a) = 0  -> F(3a) = 0
    eq2 = F.subs(t, 3 * a)
    # 3) 3B - A = 6*a*q
    eq3 = 3 * B - A - 6 * a * q

    # Решаем систему
    solution = sympy.solve((eq1, eq2, eq3), (A, B, C), dict=True)
    if not solution:
        print("Система уравнений не имеет решений.")
        return

    # Единственное (или основное) решение
    sol = solution[0]
    A_sol = sol[A]
    B_sol = sol[B]
    C_sol = sol[C]

    print(f"Найденные коэффициенты:")
    print(f"  A = {A_sol}")
    print(f"  B = {B_sol}")
    print(f"  C = {C_sol}")

    # --- 2. Составляем выражение y(t) ---------------------------------------
    # Перепишем F(t) (EI*y(t)) теперь с учётом найденных A, B, C
    # Подставим решения обратно, чтобы получить конкретное выражение для F(t)
    F_sub = F.subs({A: A_sol, B: B_sol, C: C_sol})

    # Собственно y(t) = F_sub / (E*I)
    y_expr = F_sub / (E * I)

    # --- 3. Находим критические точки (где y'(t) = 0) ----------------------
    dy_dt = sympy.diff(y_expr, t)

    # Решаем уравнение dy_dt = 0
    critical_points = sympy.solve(sympy.Eq(dy_dt, 0), t, dict=True)

    # Извлечём значения t из списка словарей и отфильтруем их по условию 0 <= t <= 3a
    critical_t_values = []
    for cp in critical_points:
        t_val = cp[t]
        # Убедимся, что t_val это действительное число и попадает в [0, 3a]
        if t_val.is_real:
            # Иногда sympy может дать выражение, которое неупрощённо выглядит,
            # поэтому приведём к float, чтобы сравнить
            t_float = float(t_val)
            if 0 <= t_float <= 3 * a:
                critical_t_values.append(t_float)

    # Также часто рассматривают граничные точки 0 и 3a,
    # но пользователь просил найти лишь "локальные экстремумы".
    # Если же нужно учесть и границы, можно их добавить в общий список:
    # boundary_points = [0, 3*a]
    # for bp in boundary_points:
    #     if bp not in critical_t_values:
    #         critical_t_values.append(bp)

    # Сортируем найденные точки по возрастанию
    critical_t_values.sort()

    # --- 4. Выводим найденные экстремумы ------------------------------------
    print("\nЛокальные экстремумы (критические точки на [0, 3a]):")
    if not critical_t_values:
        print("  Нет критических точек на заданном промежутке.")
    else:
        for ct in critical_t_values:
            # Вычислим y(ct)
            y_val = y_expr.subs(t, ct)
            print(f"  t = {ct:.5g},  y(t) = {y_val.evalf():.5g}")


# ----------------------------------------------------------------------------
# Пример использования
if __name__ == "__main__":
    # Задаём числовые значения констант
    E_val = 1  # Модуль Юнга (Па)
    I_val = 1.0  # Момент инерции (м^4)
    a_val = 1.0  # Пример
    q_val = 1.0  # Пример

    solve_and_find_extrema(E_val, I_val, a_val, q_val)