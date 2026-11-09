from validation import input_length, input_diameter, input_flow, input_roughness
from menu import show_menu, select_medium, medium_name
from operations import flow_velocity, reynolds, friction_factor, pressure_loss, flow_regime
from connstans import PA_IN_KPA


def main() -> None:
    """Главный сценарий."""
    print("=== Расчёт потерь давления в трубопроводе (Дарси-Вейсбах) ===")

    while True:
        show_menu()
        medium = select_medium()
        if medium is None:
            print("Работа завершена.")
            break

        rho, mu = medium

        length = input_length()
        d = input_diameter()
        q = input_flow()
        eps = input_roughness()

        v = flow_velocity(q, d)
        re = reynolds(rho, v, d, mu)
        lam = friction_factor(re, eps, d)
        dp = pressure_loss(lam, length, d, rho, v)
        regime = flow_regime(re)

        print("\n Результаты ")
        print(f"Среда:            {medium_name(medium)} (rho = {rho}, mu = {mu})")
        print(f"v  (скорость):    {v:.3f} м/с")
        print(f"Re (Рейнольдс):   {re:.0f}")
        print(f"lambda (трение):  {lam:.4f}")
        print(f"dp (потери):      {dp:.1f} Па = {dp / PA_IN_KPA:.3f} кПа")
        print(f"Режим течения:    {regime}")
        print("\n")


if __name__ == "__main__":
    main()
