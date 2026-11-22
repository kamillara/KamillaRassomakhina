"""Формирование числовых рядов (вариант 7 и базовые генераторы).

Вариант 7: дискретный ряд через random.choices со значениями
[1, 2, 3, 4, 5] и весами [1, 2, 4, 2, 1].
Остальные генераторы — из базовой части методички.

Каждый генератор создаёт локальный random.Random(seed):
глобальный random.seed(...) влиял бы на все модули программы,
локальный — изолирован.
"""

from __future__ import annotations

import math
import random
from typing import List, Optional, Sequence


def _validate_n(n: int) -> None:
    """Проверка, что n — положительное целое число."""
    try:
        is_positive_int = (n > 0) and (int(n) == n)
    except (TypeError, ValueError) as err:
        raise ValueError(
            f"n должно быть положительным целым числом "
            f"(получено: {n!r}; причина: {err.args[0]})"
        ) from err
    if not is_positive_int:
        raise ValueError(
            f"n должно быть положительным целым числом (получено: {n!r})"
        )


def discrete_series(
    n: int,
    values: Sequence[float] = (1, 2, 3, 4, 5),
    weights: Optional[Sequence[float]] = None,
    seed: Optional[int] = None,
) -> List[float]:
    """Ряд из n чисел дискретного распределения (вариант 7).

    Args:
        n: количество точек (положительное целое).
        values: возможные значения (по умолчанию [1, 2, 3, 4, 5]).
        weights: веса значений (по умолчанию [1, 2, 4, 2, 1] — как в
            задании варианта; None означает равномерные веса).
        seed: зерно ГПСЧ для воспроизводимости.

    Returns:
        Список float длины n.

    Raises:
        ValueError: если n некорректно, values пуст, длины values и
            weights не совпадают или все веса нулевые.
    """
    _validate_n(n)
    if not values:
        raise ValueError("values не должно быть пустым")
    if weights is None:
        weights = tuple(1.0 for _ in values)
    if len(weights) != len(values):
        raise ValueError(
            f"длины values ({len(values)}) и weights ({len(weights)}) "
            f"не совпадают"
        )
    if any(float(w) < 0 for w in weights):
        raise ValueError("веса должны быть неотрицательными")
    if all(float(w) == 0 for w in weights):
        raise ValueError("хотя бы один вес должен быть положительным")
    rng = random.Random(seed)
    return [
        float(x)
        for x in rng.choices(list(values), weights=list(weights), k=n)
    ]


def random_series(
    n: int,
    low: float = -100.0,
    high: float = 100.0,
    seed: Optional[int] = None,
) -> List[float]:
    """Ряд из n равномерно распределённых случайных чисел на [low, high]."""
    _validate_n(n)
    if low >= high:
        raise ValueError(f"low должно быть меньше high (получено: {low} >= {high})")
    rng = random.Random(seed)
    return [rng.uniform(low, high) for _ in range(n)]


def sine_series(
    n: int,
    amplitude: float = 1.0,
    frequency: float = 1.0,
    noise: float = 0.0,
    seed: Optional[int] = None,
) -> List[float]:
    """Синусоидальный ряд с аддитивным шумом (для наглядной проверки MA)."""
    _validate_n(n)
    rng = random.Random(seed)
    return [
        amplitude * math.sin(2 * math.pi * frequency * i / n)
        + (rng.uniform(-noise, noise) if noise else 0.0)
        for i in range(n)
    ]


def trend_series(
    n: int,
    start: float = 0.0,
    step: float = 1.0,
    noise: float = 0.0,
    seed: Optional[int] = None,
) -> List[float]:
    """Линейный тренд (полезно, чтобы увидеть, что MA смещается)."""
    _validate_n(n)
    rng = random.Random(seed)
    return [
        start + step * i + (rng.uniform(-noise, noise) if noise else 0.0)
        for i in range(n)
    ]
