"""Тесты скользящих средних: SMA, WMA, CMA, EMA, deque-версии и бенчмарк."""

import unittest

from num_series.generator import discrete_series
from num_series.moving_average import (
    benchmark_moving_average,
    centered_moving_average,
    exponential_moving_average,
    simple_moving_average,
    simple_moving_average_deque,
    weighted_moving_average,
)
from num_series.deque_average import (
    weighted_moving_average_deque,
    simple_moving_average_deque as deque_module_sma,
)


class TestSMA(unittest.TestCase):
    def test_example(self):
        self.assertEqual(simple_moving_average([1, 2, 3, 4, 5], 3), [2.0, 3.0, 4.0])

    def test_window_equals_n(self):
        # Краевой кейс: k = n -> одно значение
        self.assertEqual(simple_moving_average([1, 2, 3], 3), [2.0])

    def test_window_one(self):
        # Краевой кейс: k = 1 -> исходный ряд
        self.assertEqual(simple_moving_average([1.5, 2.5], 1), [1.5, 2.5])

    def test_window_greater_than_n(self):
        with self.assertRaises(ValueError):
            simple_moving_average([1, 2], 3)

    def test_empty(self):
        with self.assertRaises(ValueError):
            simple_moving_average([], 1)

    def test_window_zero(self):
        with self.assertRaises(ValueError):
            simple_moving_average([1, 2], 0)

    def test_window_not_int(self):
        with self.assertRaises(ValueError):
            simple_moving_average([1, 2], 1.5)
        with self.assertRaises(ValueError):
            simple_moving_average([1, 2], True)


class TestSMADeque(unittest.TestCase):
    def test_example(self):
        self.assertEqual(
            simple_moving_average_deque([1, 2, 3, 4, 5], 3), [2.0, 3.0, 4.0]
        )

    def test_matches_list_implementation(self):
        data = discrete_series(300, seed=11)
        self.assertEqual(
            simple_moving_average(data, 7),
            simple_moving_average_deque(data, 7),
        )

    def test_deque_module_matches_moving_average(self):
        data = discrete_series(200, seed=12)
        self.assertEqual(
            deque_module_sma(data, 5),
            simple_moving_average(data, 5),
        )

    def test_window_greater_than_n(self):
        with self.assertRaises(ValueError):
            simple_moving_average_deque([1, 2], 3)


class TestWMA(unittest.TestCase):
    """WMA с линейными весами — требование варианта 7."""

    def test_example(self):
        wma = weighted_moving_average([1, 2, 3, 4, 5], 3)
        self.assertAlmostEqual(wma[0], 14 / 6)
        self.assertAlmostEqual(wma[1], 20 / 6)
        self.assertAlmostEqual(wma[2], 26 / 6)

    def test_length(self):
        data = discrete_series(100, seed=13)
        self.assertEqual(len(weighted_moving_average(data, 10)), 91)

    def test_window_greater_than_n(self):
        with self.assertRaises(ValueError):
            weighted_moving_average([1, 2], 5)

    def test_window_one_is_source(self):
        self.assertEqual(weighted_moving_average([2.0, 4.0], 1), [2.0, 4.0])

    def test_deque_version_matches_list_version(self):
        data = discrete_series(300, seed=14)
        self.assertEqual(
            weighted_moving_average(data, 6),
            weighted_moving_average_deque(data, 6),
        )


class TestCMA(unittest.TestCase):
    def test_example(self):
        self.assertEqual(
            centered_moving_average([1, 2, 3, 4, 5], 3), [2.0, 3.0, 4.0]
        )

    def test_even_window_raises(self):
        with self.assertRaises(ValueError):
            centered_moving_average([1, 2, 3, 4], 2)


class TestEMA(unittest.TestCase):
    def test_constant_series(self):
        # Константный ряд EMA не меняет
        self.assertEqual(exponential_moving_average([5, 5, 5], 0.3), [5.0, 5.0, 5.0])

    def test_first_point_is_source(self):
        result = exponential_moving_average([10, 1, 1], 0.5)
        self.assertEqual(result[0], 10.0)

    def test_invalid_alpha(self):
        with self.assertRaises(ValueError):
            exponential_moving_average([1, 2], 0.0)
        with self.assertRaises(ValueError):
            exponential_moving_average([1, 2], 1.5)


class TestBenchmark(unittest.TestCase):
    def test_keys_and_positive(self):
        data = discrete_series(200, seed=15)
        timings = benchmark_moving_average(data, 10, repeats=5)
        self.assertEqual(set(timings), {"list", "deque"})
        self.assertGreater(timings["list"], 0.0)
        self.assertGreater(timings["deque"], 0.0)

    def test_invalid_window(self):
        with self.assertRaises(ValueError):
            benchmark_moving_average([1, 2], 5)


if __name__ == "__main__":
    unittest.main()
