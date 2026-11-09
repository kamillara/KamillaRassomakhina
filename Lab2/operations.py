"""
Расчёты: скорость потока v, число Рейнольдса Re, коэффициент трения
лямбда, потери давления dp и классификация режима течения.
"""

from typing import Annotated

from connstans import (
    PI,
    RE_LAMINAR_MAX,
    RE_TURBULENT_MIN,
    BLASIUS_COEF,
    COLEBROOK_COEF,
    COLEBROOK_TERM,
)


def flow_velocity(
    q: Annotated[float, "Расход, л/с"],
    d: Annotated[float, "Диаметр трубы, мм"],
) -> float:
    """
    Рассчитать скорость потока v = (Q/1000) / (pi * (d/1000)^2 / 4), м/с.

    Args:
        q: расход, л/с.
        d: диаметр трубы, мм.

    Returns:
        Скорость потока, м/с.
    """
    area = PI * (d / 1000.0) ** 2 / 4.0  # площадь сечения, м2
    return (q / 1000.0) / area


def reynolds(
    rho: Annotated[float, "Плотность среды, кг/м3"],
    v: Annotated[float, "Скорость потока, м/с"],
    d: Annotated[float, "Диаметр трубы, мм"],
    mu: Annotated[float, "Вязкость среды, Па*с"],
) -> float:
    """
    Рассчитать число Рейнольдса Re = rho * v * (d/1000) / mu.

    Args:
        rho: плотность среды, кг/м3.
        v: скорость потока, м/с.
        d: диаметр трубы, мм.
        mu: динамическая вязкость, Па*с.

    Returns:
        Число Рейнольдса (безразмерное).
    """
    return rho * v * (d / 1000.0) / mu


def friction_factor(
    re: Annotated[float, "Число Рейнольдса"],
    eps: Annotated[float, "Шероховатость, мм"],
    d: Annotated[float, "Диаметр трубы, мм"],
) -> float:
    """
    Коэффициент гидравлического трения лямбда.

    Если Re < 1e4 — формула Блазиуса: лямбда = 0.3164 / Re^0.25;
    иначе — упрощённый Коулбрук: лямбда = 0.11 * (eps/d + 68/Re)^0.25.

    Args:
        re: число Рейнольдса.
        eps: шероховатость стенки, мм.
        d: диаметр трубы, мм.

    Returns:
        Коэффициент трения лямбда (безразмерный).
    """
    if re < RE_TURBULENT_MIN:
        return BLASIUS_COEF / re ** 0.25
    rel_rough = eps / d
    return COLEBROOK_COEF * (rel_rough + COLEBROOK_TERM / re) ** 0.25


def pressure_loss(
    lam: Annotated[float, "Коэффициент трения лямбда"],
    length: Annotated[float, "Длина трубы, м"],
    d: Annotated[float, "Диаметр трубы, мм"],
    rho: Annotated[float, "Плотность среды, кг/м3"],
    v: Annotated[float, "Скорость потока, м/с"],
) -> float:
    """
    Потери давления по Дарси-Вейсбаху:
    dp = лямбда * (L / (d/1000)) * rho * v^2 / 2, Па.

    Args:
        lam: коэффициент трения лямбда.
        length: длина трубы, м.
        d: диаметр трубы, мм.
        rho: плотность среды, кг/м3.
        v: скорость потока, м/с.

    Returns:
        Потери давления, Па.
    """
    return lam * (length / (d / 1000.0)) * rho * v ** 2 / 2.0


def flow_regime(
    re: Annotated[float, "Число Рейнольдса"],
) -> str:
    """
    Классифицировать режим течения через if-elif-else.

    Re < 2300 — ламинарный;
    2300 <= Re <= 10000 — переходный;
    Re > 10000 — турбулентный.

    Args:
        re: число Рейнольдса.

    Returns:
        Строка с названием режима течения.
    """
    if re < RE_LAMINAR_MAX:
        return "ламинарный"
    elif re <= RE_TURBULENT_MIN:
        return "переходный"
    else:
        return "турбулентный"
