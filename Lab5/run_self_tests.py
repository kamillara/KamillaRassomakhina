"""Автономная самопроверка проекта без pytest.

python run_self_tests.py
Выводит [ OK ]/[ FAIL ] по каждой проверке, в конце — итог
и код возврата 0 (успех) или 1 (есть падения).
"""

from __future__ import annotations

import functools
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from num_series import (  # noqa: E402
    discrete_series,
    exponential_moving_average,
    exponential_moving_average_deque,
    iqr,
    load_series_json,
    load_series_txt,
    mean,
    median,
    q1,
    q3,
    quantile,
    save_series_json,
    simple_moving_average,
    simple_moving_average_deque,
    spread,
    weighted_moving_average,
    weighted_moving_average_deque,
)

FAILURES: list[str] = []


def check(name: str):
    """Декоратор: запускает проверку и печатает [ OK ]/[ FAIL ]."""

    def deco(fn):
        @functools.wraps(fn)
        def wrapper() -> None:
            try:
                fn()
                print(f"[ OK ] {name}")
            except AssertionError as err:
                print(f"[FAIL] {name}: {err}")
                FAILURES.append(name)
            except Exception as err:  # noqa: BLE001
                print(f"[FAIL] {name}: {type(err).__name__}: {err}")
                FAILURES.append(name)
        return wrapper
    return deco


# ---------------------------------------------------------------------------
# Статистика
# ---------------------------------------------------------------------------
@check("mean: среднее арифметическое")
def _mean():
    assert mean([1, 2, 3, 4]) == 2.5


@check("mean: пустой ряд -> ValueError")
def _mean_empty():
    try:
        mean([])
    except ValueError:
        return
    raise AssertionError("ValueError не выброшен")


@check("median: нечётное n")
def _median_odd():
    assert median([3, 1, 2]) == 2.0


@check("median: чётное n")
def _median_even():
    assert median([4, 1, 3, 2]) == 2.5


@check("spread: размах")
def _spread():
    assert spread([1, 5, 3]) == 4.0


@check("quantile: границы q=0 и q=1")
def _quantile_bounds():
    data = [1, 2, 3, 4, 5]
    assert quantile(data, 0.0) == 1.0 and quantile(data, 1.0) == 5.0


@check("квартили: Q1/Q3/IQR при нечётном n")
def _quartiles_odd():
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert q1(data) == 3.0 and q3(data) == 7.0 and iqr(data) == 4.0


@check("квартили: Q1/Q3/IQR при чётном n (краевой кейс)")
def _quartiles_even():
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    assert q1(data) == 3.25 and q3(data) == 7.75 and iqr(data) == 4.5


# ---------------------------------------------------------------------------
# Генератор варианта 7
# ---------------------------------------------------------------------------
@check("discrete_series: длины, множество значений, seed")
def _discrete():
    a = discrete_series(200, seed=42)
    b = discrete_series(200, seed=42)
    assert a == b
    assert len(a) == 200
    assert set(a).issubset({1.0, 2.0, 3.0, 4.0, 5.0})


@check("discrete_series: нулевой вес скрывает значение")
def _discrete_zero_weight():
    data = discrete_series(100, values=[1, 2, 3], weights=[5, 0, 0], seed=1)
    assert set(data).issubset({1.0})


@check("discrete_series: длины values/weights не совпали -> ValueError")
def _discrete_mismatch():
    try:
        discrete_series(10, values=[1, 2, 3], weights=[1, 2])
    except ValueError:
        return
    raise AssertionError("ValueError не выброшен")


# ---------------------------------------------------------------------------
# Скользящие средние
# ---------------------------------------------------------------------------
@check("SMA: пример из задания")
def _sma():
    assert simple_moving_average([1, 2, 3, 4, 5], 3) == [2.0, 3.0, 4.0]


@check("SMA: окно больше ряда -> ValueError")
def _sma_too_wide():
    try:
        simple_moving_average([1, 2], 3)
    except ValueError:
        return
    raise AssertionError("ValueError не выброшен")


@check("дифференциальный: SMA(list) == SMA(deque)")
def _sma_differential():
    data = discrete_series(150, seed=11)
    assert simple_moving_average(data, 5) == simple_moving_average_deque(data, 5)


@check("WMA: линейные веса")
def _wma():
    result = weighted_moving_average([1, 2, 3, 4, 5], 3)
    expected = [14 / 6, 20 / 6, 26 / 6]
    assert all(abs(r - e) < 1e-9 for r, e in zip(result, expected))


@check("дифференциальный: WMA(list) == WMA(deque)")
def _wma_differential():
    data = discrete_series(150, seed=12)
    a = weighted_moving_average(data, 4)
    b = weighted_moving_average_deque(data, 4)
    assert all(abs(x - y) < 1e-9 for x, y in zip(a, b))


@check("EMA: пример")
def _ema():
    assert exponential_moving_average([1, 2, 3], 0.5) == [1.0, 1.5, 2.25]


@check("дифференциальный: EMA(list) == EMA(deque)")
def _ema_differential():
    data = discrete_series(100, seed=13)
    a = exponential_moving_average(data, 0.3)
    b = exponential_moving_average_deque(data, 0.3)
    assert a == b


# ---------------------------------------------------------------------------
# Ввод-вывод
# ---------------------------------------------------------------------------
@check("io_json: сохранение и чтение в tmp-каталоге")
def _io_json():
    data = discrete_series(50, seed=21)
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "series.json"
        save_series_json(data, path, meta={"kind": "discrete", "variant": 7})
        assert load_series_json(path) == data
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["meta"]["variant"] == 7


@check("io_file: чтение txt, запятая как десятичный разделитель")
def _io_txt():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "series.txt"
        path.write_text("1,5\n2\n-3\n", encoding="utf-8")
        assert load_series_txt(path) == [1.5, 2.0, -3.0]


# ---------------------------------------------------------------------------
# CLI (интеграционный уровень)
# ---------------------------------------------------------------------------
@check("CLI: обычный запуск (код 0, статистика и МА в выводе)")
def _cli_basic():
    result = subprocess.run(
        [sys.executable, str(ROOT / "main.py"), "--n", "50", "--window", "5"],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert result.returncode == 0, f"код {result.returncode}: {result.stderr}"
    for phrase in ("Квартиль Q1", "IQR", "SMA", "WMA"):
        assert phrase in result.stdout, f"нет фразы: {phrase}"


@check("CLI: --json возвращает корректный JSON")
def _cli_json():
    result = subprocess.run(
        [sys.executable, str(ROOT / "main.py"), "--n", "20", "--window", "4", "--json"],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert set(payload) == {"data", "stats", "sma", "wma"}


@check("CLI: окно больше ряда -> код 1 и 'Ошибка' в stderr")
def _cli_error():
    result = subprocess.run(
        [sys.executable, str(ROOT / "main.py"), "--n", "5", "--window", "10"],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert result.returncode == 1
    assert "Ошибка" in result.stderr


def main() -> int:
    # Порядок прогонов фиксирован
    ordered = [
        _mean, _mean_empty, _median_odd, _median_even, _spread,
        _quantile_bounds, _quartiles_odd, _quartiles_even,
        _discrete, _discrete_zero_weight, _discrete_mismatch,
        _sma, _sma_too_wide, _sma_differential,
        _wma, _wma_differential, _ema, _ema_differential,
        _io_json, _io_txt, _cli_basic, _cli_json, _cli_error,
    ]
    print(f"Проверок в наборе: {len(ordered)}\n")
    for fn in ordered:
        fn()
    passed = len(ordered) - len(FAILURES)
    print(f"\nИтог: {passed}/{len(ordered)} проверок пройдено")
    if FAILURES:
        print("Падения:", ", ".join(FAILURES))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
