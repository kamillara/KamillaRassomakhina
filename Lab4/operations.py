"""Расчёты: скорость резания, скорректированная скорость, класс диаметра."""

import constants


def cutting_speed(d: float, n: float) -> float:
    """Рассчитать скорость резания.

    Args:
        d: диаметр заготовки, мм.
        n: частота вращения, об/мин.

    Returns:
        Скорость резания V = pi * D * n / 1000, м/мин.
    """
    return constants.PI_ * d * n / 1000.0


def adjusted_speed(v: float, k: float) -> float:
    """Рассчитать скорректированную скорость резания.

    Args:
        v: скорость резания, м/мин.
        k: коэффициент режима обработки.

    Returns:
        Скорректированная скорость V_adj = V * k, м/мин.
    """
    return v * k


def diameter_class(d: float) -> str:
    """Классифицировать диаметр заготовки.

    Args:
        d: диаметр заготовки, мм.

    Returns:
        «малый диаметр», «нормальный диаметр» или «крупный диаметр».
    """
    if d < constants.D_SMALL_LIMIT:
        return "малый диаметр"
    elif d > constants.D_LARGE_LIMIT:
        return "крупный диаметр"
    else:
        return "нормальный диаметр"
