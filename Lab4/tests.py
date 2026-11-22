"""Юнит-тесты модулей validators и operations.

Запуск: python -m unittest tests -v
"""

import unittest
from unittest.mock import patch

import logger
import validators
import operations


class TestValidateRange(unittest.TestCase):
    """Тесты функции validate_range: границы диапазона."""

    def test_inside(self):
        """Значение внутри диапазона — True, без сообщения."""
        self.assertEqual(validators.validate_range(50, 1, 500), (True, ""))

    def test_on_lower(self):
        """Значение на нижней границе — True."""
        self.assertEqual(validators.validate_range(1, 1, 500), (True, ""))

    def test_on_upper(self):
        """Значение на верхней границе — True."""
        self.assertEqual(validators.validate_range(500, 1, 500), (True, ""))

    def test_below(self):
        """Значение ниже диапазона — False, есть сообщение."""
        ok, msg = validators.validate_range(0, 1, 500)
        self.assertFalse(ok)
        self.assertTrue(msg)

    def test_above(self):
        """Значение выше диапазона — False, есть сообщение."""
        ok, msg = validators.validate_range(501, 1, 500)
        self.assertFalse(ok)
        self.assertTrue(msg)


class TestInputDiameter(unittest.TestCase):
    """Тесты циклического ввода диаметра (границы 1 и 500)."""

    def setUp(self):
        """Очистка журнала перед каждым тестом."""
        logger.clear()

    def test_invalid_then_valid(self):
        """Ввод «abc», затем 600, затем 50 — результат 50.0, две ошибки в журнале."""
        with patch("validators.input", side_effect=["abc", "600", "50"]):
            self.assertEqual(validators.input_diameter(), 50.0)
        self.assertEqual(len(logger.get_entries()), 2)

    def test_lower_boundary(self):
        """Ввод 1 — минимальная граница принимается."""
        with patch("validators.input", side_effect=["1"]):
            self.assertEqual(validators.input_diameter(), 1.0)

    def test_upper_boundary(self):
        """Ввод 500 — максимальная граница принимается."""
        with patch("validators.input", side_effect=["500"]):
            self.assertEqual(validators.input_diameter(), 500.0)


class TestInputFrequency(unittest.TestCase):
    """Тесты циклического ввода частоты вращения (границы 50 и 3000)."""

    def setUp(self):
        """Очистка журнала перед каждым тестом."""
        logger.clear()

    def test_invalid_then_valid(self):
        """Ввод 10, затем 5000, затем 1000 — результат 1000.0, две ошибки в журнале."""
        with patch("validators.input", side_effect=["10", "5000", "1000"]):
            self.assertEqual(validators.input_frequency(), 1000.0)
        self.assertEqual(len(logger.get_entries()), 2)

    def test_lower_boundary(self):
        """Ввод 50 — минимальная граница принимается."""
        with patch("validators.input", side_effect=["50"]):
            self.assertEqual(validators.input_frequency(), 50.0)

    def test_upper_boundary(self):
        """Ввод 3000 — максимальная граница принимается."""
        with patch("validators.input", side_effect=["3000"]):
            self.assertEqual(validators.input_frequency(), 3000.0)


class TestOperations(unittest.TestCase):
    """Тесты расчётов скорости резания и классификации диаметра."""

    def test_cutting_speed(self):
        """cutting_speed(100, 1000) ≈ 314.1593."""
        self.assertAlmostEqual(
            operations.cutting_speed(100, 1000), 314.1593, places=4
        )

    def test_adjusted_speed_coarse(self):
        """Коэффициент 1.0 не меняет скорость."""
        self.assertEqual(operations.adjusted_speed(100.0, 1.0), 100.0)

    def test_adjusted_speed_semi(self):
        """Коэффициент 0.85 уменьшает скорость."""
        self.assertEqual(operations.adjusted_speed(100.0, 0.85), 85.0)

    def test_adjusted_speed_finish(self):
        """Коэффициент 0.7 уменьшает скорость."""
        self.assertEqual(operations.adjusted_speed(100.0, 0.7), 70.0)

    def test_class_small(self):
        """Диаметр 5 — «малый диаметр»."""
        self.assertEqual(operations.diameter_class(5), "малый диаметр")

    def test_class_small_limit(self):
        """Диаметр 10 — «нормальный диаметр» (граница)."""
        self.assertEqual(operations.diameter_class(10), "нормальный диаметр")

    def test_class_normal(self):
        """Диаметр 50 — «нормальный диаметр»."""
        self.assertEqual(operations.diameter_class(50), "нормальный диаметр")

    def test_class_large_limit(self):
        """Диаметр 100 — «нормальный диаметр» (граница)."""
        self.assertEqual(operations.diameter_class(100), "нормальный диаметр")

    def test_class_large(self):
        """Диаметр 150 — «крупный диаметр»."""
        self.assertEqual(operations.diameter_class(150), "крупный диаметр")


if __name__ == "__main__":
    unittest.main()
