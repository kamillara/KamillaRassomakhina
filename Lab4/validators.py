"""Валидация ввода данных.

Проверка типа и диапазона вводимых значений, циклический ввод
до получения корректного значения. Используются if-elif-else,
while и try/except.
"""

from constants import D_MIN, D_MAX, N_MIN, N_MAX
import logger


def validate_range(value: float, low: float, high: float) -> tuple[bool, str]:
    """Проверить, что значение лежит в диапазоне [low, high].

    Args:
        value: проверяемое значение.
        low: нижняя граница диапазона.
        high: верхняя граница диапазона.

    Returns:
        Кортеж (True, "") — значение в диапазоне,
        либо (False, "сообщение об ошибке").
    """
    if value < low:
        return (False, f"Ошибка: значение не должно быть меньше {low}")
    elif value > high:
        return (False, f"Ошибка: значение не должно быть больше {high}")
    else:
        return (True, "")


def input_number(prompt: str, low: float, high: float) -> float:
    """Циклический ввод числа с проверкой типа и диапазона.

    Args:
        prompt: приглашение к вводу.
        low: нижняя граница диапазона.
        high: верхняя граница диапазона.

    Returns:
        Корректное число типа float.
    """
    is_valid = False
    while not is_valid:
        try:
            value = float(input(prompt))
        except ValueError:
            message = f"Ошибка: введите число ({prompt})"
            print(message)
            logger.log_error(message)
            continue
        ok, message = validate_range(value, low, high)
        if not ok:
            print(message)
            logger.log_error(message)
            continue
        is_valid = True
    return value


def input_diameter() -> float:
    """Ввести диаметр заготовки с проверкой диапазона.

    Returns:
        Диаметр заготовки в мм.
    """
    return input_number("Введите диаметр заготовки D (мм): ", D_MIN, D_MAX)


def input_frequency() -> float:
    """Ввести частоту вращения с проверкой диапазона.

    Returns:
        Частота вращения в об/мин.
    """
    return input_number("Введите частоту вращения n (об/мин): ", N_MIN, N_MAX)
