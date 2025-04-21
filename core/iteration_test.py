# parameter_study_parallel.py

import os
import json
import time
import datetime
import numpy as np
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm

import core.calc_module as cm  # ваш модуль расчётов
from core.beam_solver import BeamSolver

# ---------------------- Параметры исследования -----------------------------
N_POINTS      = 200
MAX_AMPLITUDE = 0.05
N_REPEATS     = 10
MODES_RANGE   = range(1, 5)    # 1…5
FORCE_RANGE   = range(1, 21)   # 1…30
MOMENT_RANGE  = range(1, 21)   # 1…30

JSON_PATH = os.path.join("data", "parameter_study.json")

# ---------------------- Подготовка каталога/файла --------------------------
os.makedirs("data", exist_ok=True)
if os.path.exists(JSON_PATH):
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            results = json.load(f)
    except json.JSONDecodeError:
        print(f"WARNING: {JSON_PATH} повреждён, перезаписываем.")
        results = []
else:
    results = []


def run_one(task):
    """
    Выполнить одно задание parameter study:
    task = (N_modes, N_F, N_M, rep)
    """
    N_modes, N_F, N_M, rep = task

    # 1) Генерация целевых перемещений
    x_t, w_t = cm.generate_random_displacements(
        n=N_POINTS,
        L=cm.L_GLOBAL,
        N_modes=N_modes,
        max_amplitude=MAX_AMPLITUDE
    )

    # 2) Оптимизация (берём fresh BeamSolver внутри процесса)
    solver = BeamSolver(cm.L_GLOBAL, cm.E_GLOBAL, {"I": cm.I_GLOBAL, "h": 0.1})
    t0 = time.time()
    _, _, best_err, best_nit = cm.run_multistart_optimization(
        solver=solver,
        x_target=x_t,
        w_target=w_t,
        N_F=N_F,
        N_M=N_M,
        n_starts=1,
        iteration_callback=None,
        start_callback=None
    )
    elapsed = time.time() - t0

    # 3) Формируем словарь-результат
    return {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "N_modes": N_modes,
        "N_F": N_F,
        "N_M": N_M,
        "repeat": rep + 1,
        "error": float(f"{best_err:.6e}"),
        "iterations": int(best_nit),
        "time_s": float(f"{elapsed:.3f}")
    }


if __name__ == "__main__":
    # 4) Собираем все задания
    tasks = [
        (nm, nf, nmom, rep)
        for nm in MODES_RANGE
        for nf in FORCE_RANGE
        for nmom in MOMENT_RANGE
        for rep in range(N_REPEATS)
    ]

    total = len(tasks)
    workers = os.cpu_count() or 4

    # 5) Запуск в пуле процессов
    with ProcessPoolExecutor(max_workers=workers) as exe:
        futures = {exe.submit(run_one, t): t for t in tasks}

        # tqdm для визуализации прогресса и ETA
        for fut in tqdm(as_completed(futures),
                        total=total,
                        ncols=80,
                        desc="Parameter study"):
            task = futures[fut]
            try:
                rec = fut.result()
            except Exception as e:
                print(f"ERROR in task {task}: {e}")
                continue

            results.append(rec)
            # сохраняем сразу, чтобы не потерять данные при краше
            with open(JSON_PATH, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nГотово! Результаты в {JSON_PATH}")
