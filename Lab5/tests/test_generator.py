"""Тесты генераторов рядов (вариант 7: дискретный ряд)."""

import pytest

from num_series.generator import (
    _validate_n,
    discrete_series,
    random_series,
    sine_series,
    trend_series,
)


# ---------------------------------------------------------------------------
# _validate_n: fail fast на некорректных входах
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("bad_n", [0, -5, 10.5, "10", None])
def test_validate_n_rejects(bad_n):
    with pytest.raises(ValueError, match="положительным целым"):
        _validate_n(bad_n)


@pytest.mark.parametrize("good_n", [1, 2, 100])
def test_validate_n_accepts(good_n):
    _validate_n(good_n)  # не должно выбрасывать исключений


# ---------------------------------------------------------------------------
# Дискретный ряд (вариант 7)
# ---------------------------------------------------------------------------
def test_discrete_length():
    assert len(discrete_series(1000, seed=1)) == 1000


def test_discrete_values_in_set():
    data = discrete_series(500, seed=2)
    assert set(data).issubset({1.0, 2.0, 3.0, 4.0, 5.0})


def test_discrete_reproducible():
    assert discrete_series(100, seed=42) == discrete_series(100, seed=42)


def test_discrete_zero_weight_hides_value():
    # Вес 0 у части значений — они не должны встречаться
    data = discrete_series(300, values=[1, 2, 3], weights=[10, 0, 0], seed=3)
    assert set(data).issubset({1.0})


@pytest.mark.parametrize(
    "values, weights, match",
    [
        ([1, 2, 3], [1, 2], "не совпадают"),
        ([], None, "не должно быть пустым"),
        ([1, 2], [0, 0], "хотя бы один вес"),
        ([1, 2], [1, -1], "неотрицательными"),
    ],
)
def test_discrete_errors(values, weights, match):
    with pytest.raises(ValueError, match=match):
        discrete_series(10, values=values, weights=weights)


# ---------------------------------------------------------------------------
# Базовые генераторы методички
# ---------------------------------------------------------------------------
def test_random_reproducible():
    assert random_series(50, seed=5) == random_series(50, seed=5)


def test_random_bounds():
    data = random_series(200, low=-10, high=10, seed=6)
    assert all(-10 <= x <= 10 for x in data)


def test_sine_reproducible_and_bounded():
    a = sine_series(100, seed=7)
    b = sine_series(100, seed=7)
    assert a == b
    assert all(abs(x) <= 11.5 + 1e-9 for x in a)  # амплитуда 10 + шум 1.5


def test_trend_bounds():
    n = 20
    data = trend_series(n, start=0, step=1.0, noise=0.5, seed=8)
    assert len(data) == n
    assert data[0] == pytest.approx(0.0, abs=0.5)
    assert data[-1] == pytest.approx(n - 1, abs=0.5)
