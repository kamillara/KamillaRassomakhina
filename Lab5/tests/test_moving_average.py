"""Тесты скользящих средних (list-версии): SMA, CMA, EMA, WMA, бенчмарк."""

import pytest

from num_series.generator import discrete_series
from num_series.moving_average import (
    benchmark_moving_average,
    centered_moving_average,
    exponential_moving_average,
    simple_moving_average,
    weighted_moving_average,
)


# ---------------------------------------------------------------------------
# SMA
# ---------------------------------------------------------------------------
def test_sma_example():
    assert simple_moving_average([1, 2, 3, 4, 5], 3) == [2.0, 3.0, 4.0]


def test_sma_window_equals_n():
    # Краевой кейс: k = n -> одно значение
    assert simple_moving_average([1, 2, 3], 3) == [2.0]


def test_sma_window_one():
    # Краевой кейс: k = 1 -> исходный ряд
    assert simple_moving_average([1.5, 2.5], 1) == [1.5, 2.5]


@pytest.mark.parametrize(
    "data, window, match",
    [
        ([1, 2], 3, "больше длины ряда"),
        ([], 1, "пуст"),
        ([1, 2], 0, ">= 1"),
        ([1, 2], 1.5, "целым"),
        ([1, 2], True, "целым"),
    ],
)
def test_sma_errors(data, window, match):
    with pytest.raises(ValueError, match=match):
        simple_moving_average(data, window)


def test_sma_matches_naive():
    """Дифференциальный тест: бегущая сумма O(n) против наивной O(n*w)."""
    data = discrete_series(150, seed=21)
    window = 5
    fast = simple_moving_average(data, window)
    naive = [
        sum(data[i : i + window]) / window
        for i in range(len(data) - window + 1)
    ]
    assert fast == pytest.approx(naive)


# ---------------------------------------------------------------------------
# CMA (центрированное МА)
# ---------------------------------------------------------------------------
def test_cma_example():
    assert centered_moving_average([1, 2, 3, 4, 5], 3) == [2.0, 3.0, 4.0]


@pytest.mark.parametrize("window", [2, 4, 6])
def test_cma_even_window(window):
    with pytest.raises(ValueError, match="нечётного"):
        centered_moving_average(list(range(1, 10)), window)


# ---------------------------------------------------------------------------
# EMA
# ---------------------------------------------------------------------------
def test_ema_example():
    assert exponential_moving_average([1, 2, 3], 0.5) == [1.0, 1.5, 2.25]


@pytest.mark.parametrize("alpha", [0.0, -0.1, 1.5])
def test_ema_invalid_alpha(alpha):
    with pytest.raises(ValueError, match="alpha"):
        exponential_moving_average([1, 2, 3], alpha)


def test_ema_empty():
    with pytest.raises(ValueError, match="пуст"):
        exponential_moving_average([], 0.5)


# ---------------------------------------------------------------------------
# WMA (вариант 7)
# ---------------------------------------------------------------------------
def test_wma_example():
    # Веса от старого к новому: 1, 2, 3; знаменатель 6
    result = weighted_moving_average([1, 2, 3, 4, 5], 3)
    assert result == pytest.approx([14 / 6, 20 / 6, 26 / 6])


def test_wma_matches_naive():
    """Дифференциальный тест WMA против прямой формулы с весами."""
    data = discrete_series(120, seed=22)
    window = 4
    fast = weighted_moving_average(data, window)
    weights = list(range(1, window + 1))
    denom = sum(weights)
    naive = [
        sum(w * x for w, x in zip(weights, data[i : i + window])) / denom
        for i in range(len(data) - window + 1)
    ]
    assert fast == pytest.approx(naive)


@pytest.mark.parametrize(
    "data, window, match",
    [
        ([1, 2], 3, "больше длины ряда"),
        ([], 2, "пуст"),
        ([1, 2], 0, ">= 1"),
    ],
)
def test_wma_errors(data, window, match):
    with pytest.raises(ValueError, match=match):
        weighted_moving_average(data, window)


# ---------------------------------------------------------------------------
# Бенчмарк (5.1)
# ---------------------------------------------------------------------------
def test_benchmark_keys_and_positive():
    data = discrete_series(200, seed=23)
    timings = benchmark_moving_average(data, 5, repeats=10)
    assert set(timings) == {"list", "deque"}
    assert timings["list"] > 0
    assert timings["deque"] > 0
