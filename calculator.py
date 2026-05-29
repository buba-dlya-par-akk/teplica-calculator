"""
Модуль расчёта объёма полива теплицы.
Содержит функцию расчёта и загрузки коэффициентов.
"""

from typing import Dict, Tuple


def load_coefficients(filepath: str = None) -> Dict:
    """
    Возвращает словарь с коэффициентами культур.
    """
    return {
        "cultures": {
            "помидоры": {
                "base_rate_l_per_m2": 4.5,
                "temp_coefficient": 0.08,
                "opt_moisture": 70
            },
            "огурцы": {
                "base_rate_l_per_m2": 6.0,
                "temp_coefficient": 0.1,
                "opt_moisture": 80
            },
            "перцы": {
                "base_rate_l_per_m2": 3.5,
                "temp_coefficient": 0.07,
                "opt_moisture": 65
            },
            "клубника": {
                "base_rate_l_per_m2": 2.0,
                "temp_coefficient": 0.05,
                "opt_moisture": 60
            },
            "салат": {
                "base_rate_l_per_m2": 3.0,
                "temp_coefficient": 0.06,
                "opt_moisture": 75
            }
        }
    }


def calculate_watering(
    culture: str,
    area: float,
    temperature: float,
    soil_moisture: float,
    coefficients: Dict = None
) -> Tuple[float, str]:
    """
    Рассчитывает объём полива и возвращает результат с формулой.

    Формула:
    Объём = Площадь × БазовыйРасход × (1 + (Темп - 20) × Ктемп) × (ОптВлаж / ТекВлаж)
    """
    # Валидация
    if area <= 0:
        raise ValueError("Площадь должна быть положительным числом")
    if area > 10000:
        raise ValueError("Площадь не может превышать 10000 м²")
    if temperature < -50 or temperature > 60:
        raise ValueError("Температура должна быть от -50 до 60°C")
    if soil_moisture < 0 or soil_moisture > 100:
        raise ValueError("Влажность почвы должна быть от 0 до 100%")
    if soil_moisture == 0:
        raise ValueError("Влажность почвы не может быть равна 0")

    if coefficients is None:
        coefficients = load_coefficients()

    if culture not in coefficients["cultures"]:
        available = ", ".join(coefficients["cultures"].keys())
        raise KeyError(f"Культура '{culture}' не найдена. Доступны: {available}")

    cult_data = coefficients["cultures"][culture]
    base_rate = cult_data["base_rate_l_per_m2"]
    temp_coef = cult_data["temp_coefficient"]
    opt_moisture = cult_data["opt_moisture"]

    temp_factor = 1 + (temperature - 20) * temp_coef
    moisture_factor = opt_moisture / soil_moisture

    volume = area * base_rate * temp_factor * moisture_factor
    volume = round(volume, 2)

    formula = (
        f"Объём = {area} × {base_rate} × (1 + ({temperature} - 20) × {temp_coef}) "
        f"× ({opt_moisture} / {soil_moisture})\n"
        f"Объём = {area} × {base_rate} × {round(temp_factor, 4)} × {round(moisture_factor, 4)}\n"
        f"Объём = {volume} литров"
    )

    return volume, formula


def compare_cultures(
    culture1: str,
    culture2: str,
    area: float,
    temperature: float,
    soil_moisture: float,
    coefficients: Dict = None
) -> Dict:
    """
    Сравнивает расход воды для двух культур.
    """
    vol1, formula1 = calculate_watering(culture1, area, temperature, soil_moisture, coefficients)
    vol2, formula2 = calculate_watering(culture2, area, temperature, soil_moisture, coefficients)

    diff = round(abs(vol1 - vol2), 2)
    percent = round((diff / max(vol1, vol2)) * 100, 1) if max(vol1, vol2) > 0 else 0

    return {
        "culture1": {"name": culture1, "volume": vol1, "formula": formula1},
        "culture2": {"name": culture2, "volume": vol2, "formula": formula2},
        "difference_l": diff,
        "difference_percent": percent
    }