"""Пакет алгоритмической обработки числовых рядов (вариант 7).

Публичный API пакета:
Генерация ряда:
    discrete_series (вариант 7), random_series, sine_series, trend_series
Статистика:
    mean, median, spread, quantile, q1, q3, iqr, summarize
Скользящие средние (list):
    simple_moving_average, simple_moving_average_deque,
    centered_moving_average, exponential_moving_average,
    weighted_moving_average, benchmark_moving_average
Скользящие средние (deque, расширение 5.1):
    centered_moving_average_deque, exponential_moving_average_deque,
    weighted_moving_average_deque
Ввод-вывод:
    save_series_json, load_series_json,
    load_series_txt, load_series_csv, load_series_auto
"""

from .generator import (
    discrete_series,
    random_series,
    sine_series,
    trend_series,
)
from .stats import (
    mean,
    median,
    spread,
    quantile,
    q1,
    q3,
    iqr,
    summarize,
)
from .moving_average import (
    simple_moving_average,
    simple_moving_average_deque,
    centered_moving_average,
    exponential_moving_average,
    weighted_moving_average,
    benchmark_moving_average,
)
from .deque_average import (
    centered_moving_average_deque,
    exponential_moving_average_deque,
    weighted_moving_average_deque,
)
from .io_json import save_series_json, load_series_json
from .io_file import load_series_txt, load_series_csv, load_series_auto

__all__ = [
    # генерация
    "discrete_series", "random_series", "sine_series", "trend_series",
    # статистика
    "mean", "median", "spread", "quantile", "q1", "q3", "iqr", "summarize",
    # скользящие средние (list)
    "simple_moving_average", "simple_moving_average_deque",
    "centered_moving_average", "exponential_moving_average",
    "weighted_moving_average", "benchmark_moving_average",
    # скользящие средние (deque, 5.1)
    "centered_moving_average_deque",
    "exponential_moving_average_deque",
    "weighted_moving_average_deque",
    # ввод-вывод
    "save_series_json", "load_series_json",
    "load_series_txt", "load_series_csv", "load_series_auto",
]

__version__ = "1.8.0"
