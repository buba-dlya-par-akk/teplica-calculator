"""
Unit-тесты для модуля calculator.py
"""

import sys
import os
import unittest

# Добавление src в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from calculator import calculate_watering, load_coefficients, compare_cultures


class TestCalculator(unittest.TestCase):
    """Тесты для функций калькулятора"""

    @classmethod
    def setUpClass(cls):
        """Загрузка коэффициентов перед всеми тестами"""
        cls.coefficients = load_coefficients()

    def test_normal_calculation(self):
        """Тест нормального расчёта"""
        volume, formula = calculate_watering(
            "помидоры", 100, 25, 70, self.coefficients
        )
        self.assertGreater(volume, 0)
        self.assertIn("помидоры", formula.lower())
        self.assertIn("100", formula)

    def test_high_temperature_increases_watering(self):
        """Тест: высокая температура увеличивает полив"""
        vol_normal, _ = calculate_watering("огурцы", 50, 20, 75, self.coefficients)
        vol_hot, _ = calculate_watering("огурцы", 50, 35, 75, self.coefficients)
        self.assertGreater(vol_hot, vol_normal)

    def test_low_moisture_increases_watering(self):
        """Тест: низкая влажность увеличивает полив"""
        vol_normal, _ = calculate_watering("перцы", 50, 22, 65, self.coefficients)
        vol_dry, _ = calculate_watering("перцы", 50, 22, 30, self.coefficients)
        self.assertGreater(vol_dry, vol_normal)

    def test_different_cultures_different_volumes(self):
        """Тест: разные культуры дают разный объём"""
        vol_tomato, _ = calculate_watering("помидоры", 100, 22, 65, self.coefficients)
        vol_cucumber, _ = calculate_watering("огурцы", 100, 22, 65, self.coefficients)
        self.assertNotEqual(vol_tomato, vol_cucumber)

    def test_zero_area_error(self):
        """Тест: ошибка при нулевой площади"""
        with self.assertRaises(ValueError):
            calculate_watering("помидоры", 0, 22, 65, self.coefficients)

    def test_negative_temperature_error(self):
        """Тест: ошибка при слишком низкой температуре"""
        with self.assertRaises(ValueError):
            calculate_watering("помидоры", 10, -100, 65, self.coefficients)

    def test_invalid_moisture_error(self):
        """Тест: ошибка при влажности > 100%"""
        with self.assertRaises(ValueError):
            calculate_watering("помидоры", 10, 22, 150, self.coefficients)

    def test_zero_moisture_error(self):
        """Тест: ошибка при нулевой влажности (деление на ноль)"""
        with self.assertRaises(ValueError):
            calculate_watering("помидоры", 10, 22, 0, self.coefficients)

    def test_unknown_culture_error(self):
        """Тест: ошибка при неизвестной культуре"""
        with self.assertRaises(KeyError):
            calculate_watering("арбузы", 10, 22, 65, self.coefficients)

    def test_compare_cultures(self):
        """Тест сравнения двух культур"""
        result = compare_cultures(
            "помидоры", "огурцы", 100, 25, 70, self.coefficients
        )
        self.assertIn("culture1", result)
        self.assertIn("culture2", result)
        self.assertIn("difference_l", result)
        self.assertGreater(result["difference_l"], 0)

    def test_formula_contains_all_parameters(self):
        """Тест: формула содержит все входные параметры"""
        _, formula = calculate_watering("клубника", 25.5, 23.7, 55.3, self.coefficients)
        self.assertIn("25.5", formula)
        self.assertIn("23.7", formula)
        self.assertIn("55.3", formula)

    def test_small_area(self):
        """Тест: минимальная реалистичная площадь"""
        volume, _ = calculate_watering("салат", 0.1, 20, 75, self.coefficients)
        self.assertGreater(volume, 0)
        self.assertLess(volume, 1)  # Очень маленький объём


if __name__ == "__main__":
    unittest.main(verbosity=2)