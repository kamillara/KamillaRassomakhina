"""Тесты генераторов (вариант 7: дискретный ряд)."""

import unittest

from num_series.generator import (
    _validate_n,
    discrete_series,
    random_series,
    sine_series,
    trend_series,
)


class TestValidateN(unittest.TestCase):
    """Валидация n: fail fast на некорректных входах."""

    def test_zero(self):
        with self.assertRaises(ValueError):
            _validate_n(0)

    def test_negative(self):
        with self.assertRaises(ValueError):
            _validate_n(-5)

    def test_float(self):
        with self.assertRaises(ValueError):
            _validate_n(10.5)

    def test_string(self):
        with self.assertRaises(ValueError):
            _validate_n("10")


class TestDiscreteSeries(unittest.TestCase):
    """Дискретный ряд — генератор варианта 7."""

    def test_length(self):
        self.assertEqual(len(discrete_series(1000, seed=1)), 1000)

    def test_values_in_set(self):
        data = discrete_series(500, seed=2)
        self.assertTrue(set(data).issubset({1.0, 2.0, 3.0, 4.0, 5.0}))

    def test_reproducible(self):
        a = discrete_series(100, seed=42)
        b = discrete_series(100, seed=42)
        self.assertEqual(a, b)

    def test_custom_weights(self):
        # Вес 0 у части значений — они не должны встречаться
        data = discrete_series(
            300, values=[1, 2, 3], weights=[10, 0, 0], seed=3
        )
        self.assertTrue(set(data).issubset({1.0}))

    def test_weights_length_mismatch(self):
        with self.assertRaises(ValueError):
            discrete_series(10, values=[1, 2, 3], weights=[1, 2])

    def test_empty_values(self):
        with self.assertRaises(ValueError):
            discrete_series(10, values=[])

    def test_all_zero_weights(self):
        with self.assertRaises(ValueError):
            discrete_series(10, values=[1, 2], weights=[0, 0])

    def test_negative_weight(self):
        with self.assertRaises(ValueError):
            discrete_series(10, values=[1, 2], weights=[1, -1])


class TestBaseGenerators(unittest.TestCase):
    """Базовые генераторы методички."""

    def test_random_reproducible(self):
        self.assertEqual(random_series(50, seed=5), random_series(50, seed=5))

    def test_random_bounds(self):
        data = random_series(200, low=-10, high=10, seed=6)
        self.assertTrue(all(-10 <= x <= 10 for x in data))

    def test_sine_reproducible(self):
        self.assertEqual(sine_series(30, seed=7), sine_series(30, seed=7))

    def test_trend_values(self):
        data = trend_series(5, start=1, step=2, noise=0)
        self.assertEqual(data, [1.0, 3.0, 5.0, 7.0, 9.0])


if __name__ == "__main__":
    unittest.main()
