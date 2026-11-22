"""Скользящие средние: SMA, CMA, EMA, WMA.

Вариант 7 требует SMA и WMA (взвешенная с линейными весами);
CMA и EMA входят в базовый API методички. Здесь же — SMA через
deque и бенчмарк time (расширение 5.1).
"""

from __future__ import annotations

import time
from collections import deque
from typing import Dict, List, Sequence


def _ensure_not_empty(data: Sequence[float]) -> None:
    """Валидатор: ряд не должен быть пустым (fail fast)."""
    if not data:
        raise ValueError("Ряд пуст: расчёт скользящей средней невозможен")


def check_window(window: int, n: int) -> None:
    """Проверка окна: целое >= 1 и не больше длины ряда n."""
    if not isinstance(window, int) or isinstance(window, bool):
        raise ValueError(f"window должен быть целым, получено: {window!r}")
    if window < 1:
        raise ValueError(f"window должен быть >= 1, получено: {window}")
    if window > n:
        raise ValueError(
            f"window ({window}) больше длины ряда ({n}) — SMA невозможна"
        )


def simple_moving_average(data: Sequence[float], window: int) -> List[float]:
    """SMA через бегущую сумму: O(n) по времени, O(1) по памяти.

    SMA[i] = (x[i] + ... + x[i + window - 1]) / window.
    Длина результата: n - window + 1.

    Пример:
        >>> simple_moving_average([1, 2, 3, 4, 5], 3)
        [2.0, 3.0, 4.0]
    """
    _ensure_not_empty(data)
    check_window(window, len(data))
    running = sum(data[:window])
    result = [running / window]
    for i in range(window, len(data)):
        running += data[i] - data[i - window]
        result.append(running / window)
    return result


def simple_moving_average_deque(
    data: Sequence[float],
    window: int,
) -> List[float]:
    """SMA с использованием collections.deque (двусторонней очереди)."""
    _ensure_not_empty(data)
    check_window(window, len(data))
    result = []
    d: deque = deque()
    running_sum = 0.0
    for x in data:
        d.append(x)
        running_sum += x
        if len(d) > window:
            running_sum -= d.popleft()
        if len(d) == window:
            result.append(running_sum / window)
    return result


def centered_moving_average(
    data: Sequence[float],
    window: int,
) -> List[float]:
    """Центрированное МА: окно нечётное, результат выровнен по центру.

    Для чётного window выбрасывается ValueError.
    """
    _ensure_not_empty(data)
    check_window(window, len(data))
    if window % 2 == 0:
        raise ValueError(
            f"Центрированное МА требует нечётного window, получено: {window}"
        )
    half = window // 2
    return [
        sum(data[i - half : i + half + 1]) / window
        for i in range(half, len(data) - half)
    ]


def exponential_moving_average(
    data: Sequence[float],
    alpha: float,
) -> List[float]:
    """EMA: EMA[0] = data[0]; EMA[i] = alpha*x[i] + (1-alpha)*EMA[i-1]."""
    _ensure_not_empty(data)
    if not (0 < alpha <= 1):
        raise ValueError(f"alpha должен быть в (0, 1], получено: {alpha}")
    prev = float(data[0])
    result = [prev]
    for x in data[1:]:
        prev = alpha * x + (1.0 - alpha) * prev
        result.append(prev)
    return result


def weighted_moving_average(
    data: Sequence[float],
    window: int,
) -> List[float]:
    """WMA с линейными весами (вариант 7).

    В окне веса от старого к новому: 1, 2, ..., window; знаменатель —
    сумма весов window*(window+1)/2. Длина результата: n - window + 1.

    Пример:
        >>> weighted_moving_average([1, 2, 3, 4, 5], 3)
        [2.333..., 3.333..., 4.333...]
    """
    _ensure_not_empty(data)
    check_window(window, len(data))
    denom = window * (window + 1) / 2.0
    weights = [float(j) for j in range(1, window + 1)]
    result = []
    for i in range(len(data) - window + 1):
        num = sum(w * x for w, x in zip(weights, data[i : i + window]))
        result.append(num / denom)
    return result


def benchmark_moving_average(
    data: Sequence[float],
    window: int,
    repeats: int = 1000,
) -> Dict[str, float]:
    """Замеряет среднее время выполнения SMA для list и deque.

    Args:
        data: числовой ряд.
        window: размер окна.
        repeats: количество повторов замера.

    Returns:
        Словарь с ключами "list" и "deque" (среднее время в секундах).
    """
    _ensure_not_empty(data)
    check_window(window, len(data))
    t0 = time.perf_counter()
    for _ in range(repeats):
        simple_moving_average(data, window)
    t_list = (time.perf_counter() - t0) / repeats
    t0 = time.perf_counter()
    for _ in range(repeats):
        simple_moving_average_deque(data, window)
    t_deque = (time.perf_counter() - t0) / repeats
    return {"list": t_list, "deque": t_deque}
