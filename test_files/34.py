import sympy


def solve_system(E, I, a, q):
    # Определяем символы
    A, B, C = sympy.symbols('A B C', real=True)

    # Задаём уравнения в виде символьных выражений (левая часть = 0)
    eq1 = 2 * E * I * C - (4 / sympy.Integer(3)) * B * a ** 2 + (127 / sympy.Integer(24)) * q * a ** 3
    eq2 = 3 * E * I * C - (9 / sympy.Integer(2)) * B * a ** 2 + (1 / sympy.Integer(6)) * a ** 2 + (
                115 / sympy.Integer(8)) * q * a ** 3
    eq3 = A + 3 * B - 8 * a * q

    # Решаем систему
    sol = sympy.solve((eq1, eq2, eq3), (A, B, C), dict=True)

    if sol:
        # sol — это список решений (обычно одно решение для такой системы)
        # Возвращаем A, B, C как кортеж
        return sol[0][A], sol[0][B], sol[0][C]
    else:
        # Нет решений
        return None


if __name__ == "__main__":
    # Пример: задаём значения E, I, a, q
    E_val = 210e9  # Пример, модуль Юнга, Па
    I_val = 1.0e-6  # Пример, момент инерции, м^4
    a_val = 2.0  # Пример
    q_val = 5.0  # Пример

    A_sol, B_sol, C_sol = solve_system(E_val, I_val, a_val, q_val)

    print(f"A = {A_sol}")
    print(f"B = {B_sol}")
    print(f"C = {C_sol}")