"""Тесты deque-версий скользящих средних и дифференциальные сравнения с list."""

import pytest

from num_series.deque_average import (
    centered_moving_average_deque,
    exponential_moving_average_deque,
    simple_moving_average_deque,
    weighted_moving_average_deque,
)
from num_series.generator import discrete_series
from num_series.moving_average import (
    centered_moving_average,
    exponential_moving_average,
    simple_moving_average,
    weighted_moving_average,
)


# ---------------------------------------------------------------------------
# SMA через deque
# ---------------------------------------------------------------------------
def test_sma_deque_example():
    assert simple_moving_average_deque([1, 2, 3, 4, 5], 3) == [2.0, 3.0, 4.0]


def test_sma_deque_window_equals_n():
    assert simple_moving_average_deque([1, 2, 3], 3) == [2.0]


def test_sma_deque_matches_list_version():
    """Дифференциальный тест: deque-версия == list-версия на реальном ряде."""
    data = discrete_series(300, seed=31)
    for window in (3, 7):
        assert simple_moving_average_deque(data, window) == simple_moving_average(
            data, window
        )


@pytest.mark.parametrize(
    "data, window, match",
    [
        ([1, 2], 3, "больше длины ряда"),
        ([], 1, "пуст"),
        ([1, 2], 1.5, "целым"),
    ],
)
def test_sma_deque_errors(data, window, match):
    with pytest.raises(ValueError, match=match):
        simple_moving_average_deque(data, window)


# ---------------------------------------------------------------------------
# CMA через deque
# ---------------------------------------------------------------------------
def test_cma_deque_matches_list_version():
    data = discrete_series(200, seed=32)
    assert centered_moving_average_deque(data, 5) == centered_moving_average(data, 5)


@pytest.mark.parametrize("window", [2, 4])
def test_cma_deque_even_window(window):
    with pytest.raises(ValueError, match="нечётного"):
        centered_moving_average_deque([1, 2, 3, 4, 5], window)


# ---------------------------------------------------------------------------
# EMA через deque
# ---------------------------------------------------------------------------
def test_ema_deque_matches_list_version():
    data = discrete_series(150, seed=33)
    assert exponential_moving_average_deque(data, 0.3) == exponential_moving_average(
        data, 0.3
    )


def test_ema_deque_invalid_alpha():
    with pytest.raises(ValueError, match="alpha"):
        exponential_moving_average_deque([1, 2, 3], 0.0)


# ---------------------------------------------------------------------------
# WMA через deque (вариант 7)
# ---------------------------------------------------------------------------
def test_wma_deque_example():
    result = weighted_moving_average_deque([1, 2, 3, 4, 5], 3)
    assert result == pytest.approx([14 / 6, 20 / 6, 26 / 6])


def test_wma_deque_matches_list_version():
    """Дифференциальный тест: deque-WMA == list-WMA на реальном ряде."""
    data = discrete_series(300, seed=34)
    for window in (3, 6):
        assert weighted_moving_average_deque(data, window) == weighted_moving_average(
            data, window
        )


@pytest.mark.parametrize(
    "data, window, match",
    [
        ([1, 2], 3, "больше длины ряда"),
        ([], 2, "пуст"),
        ([1, 2], 0, ">= 1"),
    ],
)
def test_wma_deque_errors(data, window, match):
    with pytest.raises(ValueError, match=match):
        weighted_moving_average_deque(data, window)
