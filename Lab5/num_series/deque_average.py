"""Скользящие средние на основе collections.deque (расширение 5.1).

Отдельный модуль, не заменяющий moving_average.py:
- сохраняет публичный контракт (Sequence[float] -> list[float]);
- реализует SMA, CMA, EMA и WMA (вариант 7) через deque(maxlen=...);
- удобен для потоковой обработки и сравнения с «индексной» версией.
"""

from __future__ import annotations

from collections import deque
from typing import Deque, List, Sequence


def _ensure_not_empty(data: Sequence[float]) -> None:
    """Валидатор: ряд не должен быть пустым (fail fast)."""
    if not data:
        raise ValueError("Ряд пуст: расчёт скользящей средней невозможен")


def _check_window(window: int, n: int) -> None:
    """Проверка окна: целое >= 1 и не больше длины ряда n."""
    if not isinstance(window, int) or isinstance(window, bool):
        raise ValueError(f"window должен быть целым, получено: {window!r}")
    if window < 1:
        raise ValueError(f"window должен быть >= 1, получено: {window}")
    if window > n:
        raise ValueError(
            f"window ({window}) больше длины ряда ({n}) — SMA невозможна"
        )


def _check_alpha(alpha: float) -> None:
    """Проверка коэффициента сглаживания alpha из (0, 1]."""
    if not (0 < alpha <= 1):
        raise ValueError(f"alpha должен быть в (0, 1], получено: {alpha}")


def simple_moving_average_deque(
    data: Sequence[float],
    window: int,
) -> List[float]:
    """SMA через deque(maxlen=window).

    Сложность: O(n) по времени, O(window) по памяти. deque автоматически
    «забывает» значение, вышедшее за окно, поэтому не нужно индексировать
    исходный ряд по i - window.

    Пример:
        >>> simple_moving_average_deque([1, 2, 3, 4, 5], 3)
        [2.0, 3.0, 4.0]
    """
    _ensure_not_empty(data)
    _check_window(window, len(data))
    buf: Deque[float] = deque(maxlen=window)
    running = 0.0
    result: List[float] = []
    for x in data:
        if len(buf) == window:
            running -= buf[0]
        buf.append(x)
        running += x
        if len(buf) == window:
            result.append(running / window)
    return result


def centered_moving_average_deque(
    data: Sequence[float],
    window: int,
) -> List[float]:
    """Центрированное МА через deque: окно нечётное, выровнено по центру.

    Для чётного window выбрасывается ValueError — как в moving_average.py.
    """
    _ensure_not_empty(data)
    _check_window(window, len(data))
    if window % 2 == 0:
        raise ValueError(
            f"Центрированное МА требует нечётного window, получено: {window}"
        )
    half = window // 2
    buf: Deque[float] = deque(maxlen=window)
    running = 0.0
    result: List[float] = []
    for x in data:
        if len(buf) == window:
            running -= buf[0]
        buf.append(x)
        running += x
        if len(buf) == window:
            result.append(running / window)
    return result


def exponential_moving_average_deque(
    data: Sequence[float],
    alpha: float,
) -> List[float]:
    """EMA через deque: EMA[0] = data[0]; EMA[i] = alpha*x[i] + (1-a)*EMA[i-1].

    deque(maxlen=1) используется как ring-buffer последнего значения —
    для симметрии с SMA и потокового характера обработки.
    """
    _ensure_not_empty(data)
    _check_alpha(alpha)
    buf: Deque[float] = deque(maxlen=1)
    prev = float(data[0])
    result: List[float] = [prev]
    for x in data[1:]:
        prev = alpha * x + (1.0 - alpha) * prev
        result.append(prev)
        buf.append(prev)
    return result


def weighted_moving_average_deque(
    data: Sequence[float],
    window: int,
) -> List[float]:
    """WMA с линейными весами через deque (вариант 7).

    В окне веса от старого к новому: 1, 2, ..., window. Скользящий
    пересчёт за O(1): при сдвиге окна из взвешенной суммы вычитается
    сумма значений окна (вес каждого элемента уменьшается на 1), а
    новый элемент входит с весом window.

    Пример:
        >>> weighted_moving_average_deque([1, 2, 3, 4, 5], 3)
        [2.333..., 3.333..., 4.333...]
    """
    _ensure_not_empty(data)
    _check_window(window, len(data))
    buf: Deque[float] = deque(maxlen=window)
    window_sum = 0.0      # сумма значений в окне
    running = 0.0         # взвешенная сумма: новейший элемент весит window
    denom = window * (window + 1) / 2.0
    result: List[float] = []
    for x in data:
        if len(buf) == window:
            running -= window_sum
            window_sum -= buf[0]
        buf.append(x)
        window_sum += x
        running += x * len(buf)
        if len(buf) == window:
            result.append(running / denom)
    return result


__all__ = [
    "simple_moving_average_deque",
    "centered_moving_average_deque",
    "exponential_moving_average_deque",
    "weighted_moving_average_deque",
]
