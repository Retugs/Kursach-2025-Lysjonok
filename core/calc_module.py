import numpy as np
from scipy.optimize import minimize

# Глобальные настройки балки
L_GLOBAL = 10.0
E_GLOBAL = 2e8
I_GLOBAL = 1e-4

# Параметры для высокой точности
GLOBAL_MAX_ITER = 2000
GLOBAL_XTOL = 1e-12
GLOBAL_GTOL = 1e-12
GLOBAL_BARRIER_TOL = 1e-12


def generate_random_displacements(n, L, N_modes=5, max_amplitude=1.0):
    z = np.linspace(0, L, n + 2)
    w = np.zeros_like(z)
    for k in range(1, N_modes + 1):
        a_k = np.random.uniform(-max_amplitude, max_amplitude)
        w += a_k * np.sin(k * np.pi * z / L)
    return z, w


def objective_function(params, solver, x_target, w_target, N_F, N_M, iter_callback=None):
    """
    Целевая функция. Для удобства передачи 'iter_callback' при trust-constr,
    но на самом деле callback придётся обрабатывать отдельно.
    """
    w_calc = _compute_w(params, solver, x_target, N_F, N_M)
    return np.sum((w_calc - w_target) ** 2)


def _compute_w(params, solver, x_target, N_F, N_M):
    loads = []
    idx = 0
    for i in range(N_F):
        F_i = params[idx]
        a_i = params[idx + 1]
        loads.append({'type': 'point', 'value': F_i, 'position': a_i})
        idx += 2
    for i in range(N_M):
        M_i = params[idx]
        b_i = params[idx + 1]
        loads.append({'type': 'moment', 'value': M_i, 'position': b_i})
        idx += 2

    x_calc, w_calc = solver.calculate_deflections_test(loads, num_points=len(x_target))
    return w_calc


###############################################################################
# Методы для однократной оптимизации с callback'ом (progress bar)
###############################################################################
global_iteration_count = 0


def _trust_constr_callback(xk, *args, **kwargs):
    """
    Вызывается на каждой итерации 'trust-constr'.
    Обновляем global_iteration_count и вызываем пользовательский колбэк, если есть.
    """
    # args может содержать res.fun, res.jac, ... но trust-constr
    # официально в callback передаёт только xk, args и kwds
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.OptimizeResult.html

    # Мы воспользуемся глобальной переменной (не самое красивое решение),
    # но для демонстрации сгодится
    global global_iteration_count
    global_iteration_count += 1

    user_callback = kwargs.get('user_callback', None)
    if user_callback is not None:
        user_callback(global_iteration_count)


def run_single_optimization_with_callback(
        solver, x_target, w_target,
        N_F, N_M,
        init_params,
        iteration_callback=None
):
    """
    Запускает оптимизацию 'trust-constr' из init_params,
    обновляя итерации через global_iteration_count и iteration_callback.
    """
    import functools

    bounds = []
    for i in range(N_F):
        bounds.append((-1e4, 1e4))
        bounds.append((0.0, L_GLOBAL))
    for i in range(N_M):
        bounds.append((-1e4, 1e4))
        bounds.append((0.0, L_GLOBAL))

    def obj(params_):
        return objective_function(params_, solver, x_target, w_target, N_F, N_M)

    options = {
        'maxiter': GLOBAL_MAX_ITER,
        'verbose': 0,
        'xtol': GLOBAL_XTOL,
        'gtol': GLOBAL_GTOL,
        'barrier_tol': GLOBAL_BARRIER_TOL
    }

    # Сбрасываем счётчик итераций
    global global_iteration_count
    global_iteration_count = 0

    # Callback-обёртка
    # метод minimize позволяет callback=lambda xk, *arg: ...
    # но trust-constr не всегда даёт много инфы
    wrapped_callback = functools.partial(_trust_constr_callback, user_callback=iteration_callback)

    res = minimize(
        obj,
        init_params,
        method='trust-constr',
        bounds=bounds,
        callback=wrapped_callback,
        options=options
    )

    opt_params = res.x
    final_error = res.fun
    # Формируем loads
    loads = []
    idx = 0
    for i in range(N_F):
        F_i = opt_params[idx]
        a_i = opt_params[idx + 1]
        loads.append({'type': 'point', 'value': F_i, 'position': a_i})
        idx += 2
    for i in range(N_M):
        M_i = opt_params[idx]
        b_i = opt_params[idx + 1]
        loads.append({'type': 'moment', 'value': M_i, 'position': b_i})
        idx += 2

    return opt_params, loads, final_error, res


###############################################################################
# Многостартовая оптимизация
###############################################################################
def run_multistart_optimization(
        solver, x_target, w_target,
        N_F, N_M,
        n_starts=5,
        iteration_callback=None,
        start_callback=None
):
    """
    Внешний цикл по числу запусков.
    iteration_callback(iter_num) - вызывается при каждой итерации trust-constr;
    start_callback(start_i, n_starts) - вызывается при начале очередного запуска.
    """
    best_error = np.inf
    best_params = None
    best_loads = None
    best_res = None

    for attempt_i in range(n_starts):
        if start_callback:
            start_callback(attempt_i + 1, n_starts)

        # Генерируем случайное нач. приближение
        init_p = []
        for i in range(N_F):
            Fi = np.random.uniform(-1000, 1000)
            ai = np.random.uniform(0, L_GLOBAL)
            init_p.append(Fi)
            init_p.append(ai)
        for i in range(N_M):
            Mi = np.random.uniform(-1000, 1000)
            bi = np.random.uniform(0, L_GLOBAL)
            init_p.append(Mi)
            init_p.append(bi)
        init_p = np.array(init_p, dtype=float)

        # Запуск одиночной оптимизации
        params, loads, err, res = run_single_optimization_with_callback(
            solver, x_target, w_target,
            N_F, N_M,
            init_p,
            iteration_callback=iteration_callback
        )
        if err < best_error:
            best_error = err
            best_params = params
            best_loads = loads
            best_res = res

    return best_params, best_loads, best_error, (best_res.nit if best_res else 0)
