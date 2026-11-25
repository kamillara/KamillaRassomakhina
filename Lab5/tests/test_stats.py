"""Тесты статистики, включая квартили и IQR (вариант 7)."""

import pytest

from num_series.stats import (
    iqr,
    mean,
    median,
    q1,
    q3,
    quantile,
    spread,
    summarize,
)


# ---------------------------------------------------------------------------
# Среднее
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "data, expected",
    [
        ([1, 2, 3, 4], 2.5),
        ([5], 5.0),
        ([-1, 1], 0.0),
        ([0.1, 0.2, 0.3], 0.2),
    ],
)
def test_mean(data, expected):
    assert mean(data) == pytest.approx(expected)


def test_mean_empty():
    with pytest.raises(ValueError, match="пуст"):
        mean([])


# ---------------------------------------------------------------------------
# Медиана (краевой кейс варианта 7: чётное и нечётное n)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "data, expected",
    [
        ([3, 1, 2], 2.0),           # нечётное n: средний элемент
        ([4, 1, 3, 2], 2.5),        # чётное n: среднее двух средних
        ([7], 7.0),                 # единственный элемент
        ([2, 2, 2], 2.0),           # все равны
    ],
)
def test_median(data, expected):
    assert median(data) == pytest.approx(expected)


def test_median_empty():
    with pytest.raises(ValueError, match="пуст"):
        median([])


# ---------------------------------------------------------------------------
# Размах
# ---------------------------------------------------------------------------
def test_spread():
    assert spread([1, 5, 3]) == 4.0


def test_spread_empty():
    with pytest.raises(ValueError, match="пуст"):
        spread([])


# ---------------------------------------------------------------------------
# Квантиль линейной интерполяцией — ядро варианта 7
# ---------------------------------------------------------------------------
def test_quantile_bounds():
    data = [1, 2, 3, 4, 5]
    assert quantile(data, 0.0) == 1.0
    assert quantile(data, 1.0) == 5.0


def test_quantile_median_agreement():
    data = [4, 1, 3, 2, 5]
    assert quantile(data, 0.5) == pytest.approx(median(data))


@pytest.mark.parametrize("bad_q", [1.5, -0.1])
def test_quantile_invalid_q(bad_q):
    with pytest.raises(ValueError, match="q должен быть"):
        quantile([1, 2, 3], bad_q)


def test_quantile_single_element():
    assert quantile([42], 0.25) == 42.0


# ---------------------------------------------------------------------------
# Квартили Q1/Q3 и IQR; краевой кейс — чётное и нечётное n
# ---------------------------------------------------------------------------
def test_quartiles_odd_n():
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    # pos(Q1) = 0.25 * 8 = 2.0 -> s[2] = 3; pos(Q3) = 0.75 * 8 = 6.0 -> s[6] = 7
    assert q1(data) == pytest.approx(3.0)
    assert q3(data) == pytest.approx(7.0)
    assert iqr(data) == pytest.approx(4.0)


def test_quartiles_even_n():
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    # pos(Q1) = 2.25 -> 3.25; pos(Q3) = 6.75 -> 7.75; IQR = 4.5
    assert q1(data) == pytest.approx(3.25)
    assert q3(data) == pytest.approx(7.75)
    assert iqr(data) == pytest.approx(4.5)


def test_quartiles_single():
    assert q1([5]) == 5.0
    assert q3([5]) == 5.0
    assert iqr([5]) == 0.0


# ---------------------------------------------------------------------------
# Сводка
# ---------------------------------------------------------------------------
def test_summarize_keys_and_values():
    stats = summarize([1, 2, 3, 4, 5])
    assert set(stats) == {
        "count", "mean", "median", "spread", "min", "max", "q1", "q3", "iqr",
    }
    assert stats["count"] == 5
    assert stats["mean"] == pytest.approx(3.0)
    assert stats["median"] == pytest.approx(3.0)
    assert stats["spread"] == pytest.approx(4.0)
    assert stats["q1"] == pytest.approx(2.0)
    assert stats["q3"] == pytest.approx(4.0)
    assert stats["iqr"] == pytest.approx(2.0)


def test_summarize_empty():
    with pytest.raises(ValueError, match="пуст"):
        summarize([])
