"""Тесты статистики, включая квартили и IQR (вариант 7)."""

import unittest

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


class TestMean(unittest.TestCase):
    def test_simple(self):
        self.assertAlmostEqual(mean([1, 2, 3, 4]), 2.5)

    def test_empty(self):
        with self.assertRaises(ValueError):
            mean([])


class TestMedian(unittest.TestCase):
    def test_odd_n(self):
        # Нечётное n: средний элемент
        self.assertEqual(median([3, 1, 2]), 2.0)

    def test_even_n(self):
        # Чётное n: среднее двух средних
        self.assertEqual(median([4, 1, 3, 2]), 2.5)

    def test_single(self):
        self.assertEqual(median([7]), 7.0)

    def test_empty(self):
        with self.assertRaises(ValueError):
            median([])


class TestSpread(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(spread([1, 5, 3]), 4.0)

    def test_empty(self):
        with self.assertRaises(ValueError):
            spread([])


class TestQuantile(unittest.TestCase):
    """Квантиль линейной интерполяцией — ядро варианта 7."""

    def test_q0_q1(self):
        data = [1, 2, 3, 4, 5]
        self.assertEqual(quantile(data, 0.0), 1.0)
        self.assertEqual(quantile(data, 1.0), 5.0)

    def test_median_matches_quantile_half(self):
        data = [4, 1, 3, 2, 5]
        self.assertAlmostEqual(quantile(data, 0.5), median(data))

    def test_invalid_q(self):
        with self.assertRaises(ValueError):
            quantile([1, 2, 3], 1.5)
        with self.assertRaises(ValueError):
            quantile([1, 2, 3], -0.1)

    def test_single(self):
        self.assertEqual(quantile([42], 0.25), 42.0)


class TestQuartilesIQR(unittest.TestCase):
    """Квартили Q1, Q3 и IQR; краевой кейс — чётное и нечётное n."""

    def test_odd_n(self):
        # n = 9 (нечётное): 1..9
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        # pos(Q1) = 0.25 * 8 = 2.0 -> s[2] = 3
        # pos(Q3) = 0.75 * 8 = 6.0 -> s[6] = 7
        self.assertAlmostEqual(q1(data), 3.0)
        self.assertAlmostEqual(q3(data), 7.0)
        self.assertAlmostEqual(iqr(data), 4.0)

    def test_even_n(self):
        # n = 10 (чётное): 1..10
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        # pos(Q1) = 0.25 * 9 = 2.25 -> 3 + 0.25 = 3.25
        # pos(Q3) = 0.75 * 9 = 6.75 -> 7 + 0.75 = 7.75
        self.assertAlmostEqual(q1(data), 3.25)
        self.assertAlmostEqual(q3(data), 7.75)
        self.assertAlmostEqual(iqr(data), 4.5)

    def test_median_consistency_even_odd(self):
        # Медиана и quantile(0.5) совпадают и для чётного, и для нечётного n
        odd = [1, 2, 3, 4, 5]
        even = [1, 2, 3, 4]
        self.assertAlmostEqual(quantile(odd, 0.5), median(odd))
        self.assertAlmostEqual(quantile(even, 0.5), median(even))

    def test_empty(self):
        with self.assertRaises(ValueError):
            q1([])
        with self.assertRaises(ValueError):
            q3([])
        with self.assertRaises(ValueError):
            iqr([])


class TestSummarize(unittest.TestCase):
    def test_keys_and_values(self):
        stats = summarize([1, 2, 3, 4, 5])
        for key in ("count", "mean", "median", "spread", "min", "max", "q1", "q3", "iqr"):
            self.assertIn(key, stats)
        self.assertEqual(stats["count"], 5)
        self.assertEqual(stats["min"], 1.0)
        self.assertEqual(stats["max"], 5.0)

    def test_empty(self):
        with self.assertRaises(ValueError):
            summarize([])


if __name__ == "__main__":
    unittest.main()
