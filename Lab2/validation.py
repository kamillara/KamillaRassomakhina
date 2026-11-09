"""
Валидация пользовательского ввода.
- Проверка границ через if-elif-else.
- Циклический ввод до корректного значения.
"""

from __future__ import annotations

from connstans import (
    L_MIN, L_MAX, D_MIN, D_MAX, Q_MIN, Q_MAX, EPS_MIN, EPS_MAX,
)
from logger import log_error


def validate_range(value: float, low: float, high: float) -> tuple[bool, str]:
    """
    Проверка попадания value в [low, high] через if-elif-else.
    :return: (True, "") или (False, сообщение)
    """
    if value < low:
        return False, f"Ошибка: значение меньше нижней границы ({low})."
    elif value > high:
        return False, f"Ошибка: значение больше верхней границы ({high})."
    else:
        return True, ""


def input_number(prompt: str, low: float, high: float) -> float:
    """
    Циклически запрашивать число, пока не будет корректного.
    Проверяет тип (float) через try/except ValueError и границы.
    """
    while True:
        raw = input(prompt).strip()
        try:
            value = float(raw.replace(",", "."))
        except ValueError as e:
            msg = str(e.args[0]) if e.args else str(e)
            msg = f"Ошибка: введено не число ('{raw}'). {msg}"
            print(msg)
            log_error(msg)
            continue

        ok, msg = validate_range(value, low, high)
        if ok:
            return value
        print(msg + " Повторите ввод.")
        log_error(msg)


def input_length() -> float:
    """Циклический ввод длины трубы L (м), допустимо 1..1000."""
    return input_number(
        "Введите длину трубы L, м (1..1000): ",
        L_MIN, L_MAX,
    )


def input_diameter() -> float:
    """Циклический ввод диаметра трубы d (мм), допустимо 10..500."""
    return input_number(
        "Введите диаметр трубы d, мм (10..500): ",
        D_MIN, D_MAX,
    )


def input_flow() -> float:
    """Циклический ввод расхода Q (л/с), допустимо 0.1..100."""
    return input_number(
        "Введите расход Q, л/с (0.1..100): ",
        Q_MIN, Q_MAX,
    )


def input_roughness() -> float:
    """Циклический ввод шероховатости eps (мм), допустимо 0..2."""
    return input_number(
        "Введите шероховатость eps, мм (0..2): ",
        EPS_MIN, EPS_MAX,
    )
