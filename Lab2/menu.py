"""
Меню выбора среды (трубопровода) через match-case.
"""

from __future__ import annotations

import connstans
from connstans import RHO_WATER, MU_WATER, RHO_OIL, MU_OIL, RHO_AIR, MU_AIR

# Тип-псевдоним: пара (плотность, вязкость)
Medium = tuple[float, float]


def show_menu() -> None:
    """Вывести меню выбора среды."""
    print("\n Выберите среду:")
    print("  1 — вода   (rho = 1000 кг/м3, mu = 0.001 Па*с)")
    print("  2 — масло  (rho = 900 кг/м3,  mu = 0.05 Па*с)")
    print("  3 — воздух (rho = 1.2 кг/м3,  mu = 1.8e-5 Па*с)")
    print("  0 — выход")


def select_medium() -> Medium | None:
    """
    Циклически запрашивать среду и возвращать пару (rho, mu).

    Использует match-case для маршрутизации.
    Возвращает None, если выбран выход (0).
    """
    while True:
        choice = input("Введите номер среды (от 0 до 3): ").strip()
        match choice:
            case "1":
                return (RHO_WATER, MU_WATER)
            case "2":
                return (RHO_OIL, MU_OIL)
            case "3":
                return (RHO_AIR, MU_AIR)
            case "0":
                return None
            case _:
                print("Ошибка: неверный пункт меню. Повторите ввод.")


def medium_name(medium: Medium) -> str:
    """Вернуть название среды по паре (rho, mu)."""
    match medium:
        case (connstans.RHO_WATER, connstans.MU_WATER):
            return "вода"
        case (connstans.RHO_OIL, connstans.MU_OIL):
            return "масло"
        case (connstans.RHO_AIR, connstans.MU_AIR):
            return "воздух"
        case _:
            return "неизвестная среда"
