import math

# --- Свойства сред (Вариант 7) ---
RHO_WATER: float = 1000.0   # плотность воды, кг/м3
MU_WATER: float = 0.001     # вязкость воды, Па*с
RHO_OIL: float = 900.0      # плотность масла, кг/м3
MU_OIL: float = 0.05        # вязкость масла, Па*с
RHO_AIR: float = 1.2        # плотность воздуха, кг/м3
MU_AIR: float = 1.8e-5      # вязкость воздуха, Па*с

# --- Допустимые диапазоны входных данных ---
L_MIN: float = 1.0      # длина трубы, м
L_MAX: float = 1000.0
D_MIN: float = 10.0     # диаметр, мм
D_MAX: float = 500.0
Q_MIN: float = 0.1      # расход, л/с
Q_MAX: float = 100.0
EPS_MIN: float = 0.0    # шероховатость, мм
EPS_MAX: float = 2.0

# --- Границы по числу Рейнольдса ---
RE_LAMINAR_MAX: float = 2300.0     # Re < 2300 — ламинарный
RE_TURBULENT_MIN: float = 10000.0  # Re > 10000 — турбулентный

# --- Коэффициенты формул трения ---
BLASIUS_COEF: float = 0.3164     # лямбда = 0.3164 / Re^0.25
COLEBROOK_COEF: float = 0.11     # лямбда = 0.11 * (eps/d + 68/Re)^0.25
COLEBROOK_TERM: float = 68.0

# --- Прочее ---
PA_IN_KPA: float = 1000.0   # 1 кПа = 1000 Па
PI: float = math.pi

# --- Файл журнала ошибок ---
LOG_FILE: str = "input_errors.log"
