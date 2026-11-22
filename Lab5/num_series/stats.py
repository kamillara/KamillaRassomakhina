"""Базовая статистика и квартили (вариант 7).

Реализовано вручную, без statistics, numpy и pandas:
среднее, медиана, размах, квантиль линейной интерполяцией,
квартили Q1/Q3 и межквартильный размах IQR = Q3 - Q1.
Метод интерполяции даёт согласованные значения квартилей
как для чётного, так и для нечётного n (краевой кейс варианта).
"""

from __future__ import annotations

import math
from typing import Dict, Sequence


def _ensure_not_empty(data: Sequence[float]) -> None:
    """Валидатор: ряд не должен быть пустым (fail fast)."""
    if not data:
        raise ValueError("Ряд пуст: расчёт статистики невозможен")


def mean(data: Sequence[float]) -> float:
    """Среднее арифметическое."""
    _ensure_not_empty(data)
    return sum(data) / len(data)


def median(data: Sequence[float]) -> float:
    """Медиана (устойчива к выбросам)."""
    _ensure_not_empty(data)
    s = sorted(data)
    k = len(s) // 2
    if len(s) % 2:
        return float(s[k])
    return (s[k - 1] + s[k]) / 2.0


def spread(data: Sequence[float]) -> float:
    """Размах ряда: max - min."""
    _ensure_not_empty(data)
    return float(max(data) - min(data))


def quantile(data: Sequence[float], q: float) -> float:
    """Квантиль уровня q (0 <= q <= 1) линейной интерполяцией.

    Позиция pos = q * (n - 1); если pos дробный — интерполяция между
    соседними элементами отсортированного ряда. Работает одинаково
    корректно для чётного и нечётного n.

    Args:
        data: числовой ряд.
        q: уровень квантиля в [0, 1].

    Returns:
        Значение квантиля.
    """
    _ensure_not_empty(data)
    if not (0.0 <= q <= 1.0):
        raise ValueError(f"q должен быть в [0, 1], получено: {q}")
    s = sorted(data)
    n = len(s)
    if n == 1:
        return float(s[0])
    pos = q * (n - 1)
    lower = int(math.floor(pos))
    frac = pos - lower
    if frac == 0.0:
        return float(s[lower])
    return float(s[lower] + frac * (s[lower + 1] - s[lower]))


def q1(data: Sequence[float]) -> float:
    """Первый квартиль Q1 (уровень 0.25)."""
    return quantile(data, 0.25)


def q3(data: Sequence[float]) -> float:
    """Третий квартиль Q3 (уровень 0.75)."""
    return quantile(data, 0.75)


def iqr(data: Sequence[float]) -> float:
    """Межквартильный размах IQR = Q3 - Q1."""
    _ensure_not_empty(data)
    return q3(data) - q1(data)


def summarize(data: Sequence[float]) -> Dict[str, float]:
    """Сводный отчёт: count, mean, median, spread, min, max, q1, q3, iqr."""
    _ensure_not_empty(data)
    return {
        "count": len(data),
        "mean": mean(data),
        "median": median(data),
        "spread": spread(data),
        "min": float(min(data)),
        "max": float(max(data)),
        "q1": q1(data),
        "q3": q3(data),
        "iqr": iqr(data),
    }
