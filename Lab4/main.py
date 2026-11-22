"""Точка входа программы «Расчёт скорости резания при токарной обработке».

Связывает модули проекта и реализует главный цикл программы.
Валидация и расчёты здесь не выполняются — только связывание модулей.
"""

from validators import input_diameter, input_frequency
from menu import show_menu, select_mode, mode_name
from operations import cutting_speed, adjusted_speed, diameter_class


def main() -> None:
    """Главный сценарий: меню, ввод данных, расчёт и вывод результатов."""
    print("Расчёт скорости резания при токарной обработке")
    while True:
        show_menu()
        k = select_mode()
        if k is None:
            print("Работа завершена.")
            break
        d = input_diameter()
        n = input_frequency()
        v = cutting_speed(d, n)
        v_adj = adjusted_speed(v, k)
        cls = diameter_class(d)
        print(f"\nРежим обработки: {mode_name(k)} (k = {k})")
        print(f"Скорость резания V = {v:.2f} м/мин")
        print(f"Скорректированная скорость V_adj = {v_adj:.2f} м/мин")
        print(f"Диаметр заготовки: {cls}")


if __name__ == "__main__":
    main()
