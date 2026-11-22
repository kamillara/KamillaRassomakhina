"""Точка входа: приложение «Алгоритмическая обработка числовых рядов» (вариант 7).

Ряд: 1000 чисел дискретного распределения — random.choices по значениям
[1, 2, 3, 4, 5] с весами [1, 2, 4, 2, 1] (значения и веса можно изменить
флагами --values и --weights).
Доп. показатель: квартили Q1, Q3 и межквартильный размах IQR = Q3 - Q1.
Скользящие средние: SMA (list и deque) и WMA; EMA — опционально (--ema).

Запуск:
python main.py --kind discrete --n 1000 --window 10 --seed 7 --benchmark
python main.py --kind discrete --values 1,2,3,4,5 --weights 1,2,4,2,1
python main.py --load series.json --window 5
python main.py --kind trend --n 20 --window 3 --export out.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from typing import List, Optional

from num_series import (
    discrete_series,
    random_series,
    sine_series,
    trend_series,
    summarize,
    simple_moving_average,
    simple_moving_average_deque,
    exponential_moving_average,
    weighted_moving_average,
    benchmark_moving_average,
    save_series_json,
    load_series_auto,
)


# ---------------------------------------------------------------------------
# Разбор значений и весов
# ---------------------------------------------------------------------------
def parse_float_list(text: Optional[str]) -> Optional[List[float]]:
    """Разбирает строку "1,2,3" в список float; None/пустая строка -> None."""
    if text is None or not text.strip():
        return None
    try:
        return [float(part) for part in text.split(",") if part.strip()]
    except ValueError as err:
        raise ValueError(
            f"Ожидались числа через запятую, получено: {text!r}"
        ) from err


# ---------------------------------------------------------------------------
# Фабрика ряда
# ---------------------------------------------------------------------------
def build_series(
    kind: str,
    n: int,
    seed: int,
    values: Optional[List[float]] = None,
    weights: Optional[List[float]] = None,
) -> List[float]:
    """Возвращает числовой ряд заданного типа.

    kind = "discrete" — дискретное распределение (вариант 7): значения и
        веса по умолчанию [1, 2, 3, 4, 5] и [1, 2, 4, 2, 1];
    kind = "random"   — равномерное распределение на [-50, 50];
    kind = "sine"     — синусоида с амплитудой 10, частотой 2 и шумом 1.5;
    kind = "trend"    — линейный тренд с шагом 1.0 и шумом 0.5.
    """
    if kind == "discrete":
        return discrete_series(
            n,
            values=values if values is not None else [1, 2, 3, 4, 5],
            weights=weights if weights is not None else [1, 2, 4, 2, 1],
            seed=seed,
        )
    if kind == "random":
        return random_series(n, low=-50, high=50, seed=seed)
    if kind == "sine":
        return sine_series(n, amplitude=10, frequency=2, noise=1.5, seed=seed)
    if kind == "trend":
        return trend_series(n, start=0, step=1.0, noise=0.5, seed=seed)
    raise ValueError(f"Неизвестный тип ряда: {kind!r}")


# ---------------------------------------------------------------------------
# Печать
# ---------------------------------------------------------------------------
PREVIEW = 10  # сколько первых значений показывать для длинных рядов


def print_series(
    title: str,
    values: List[float],
    full: bool = False,
    fmt: str = "{:>10.3f}",
) -> None:
    """Печатает ряд в одну строку (для длинных рядов — первые PREVIEW точек)."""
    if full or len(values) <= PREVIEW:
        shown = values
        note = ""
    else:
        shown = values[:PREVIEW]
        note = f" (показаны первые {PREVIEW} из {len(values)})"
    print(f"\n{title} (n={len(values)}){note}:")
    print(" " + " ".join(fmt.format(v) for v in shown))


def print_header(kind: str, n: int) -> None:
    print("=" * 60)
    print(f"Тип ряда: {kind}, n = {n}")
    print("-" * 60)


def print_stats(stats: dict) -> None:
    """Печатает блок статистических показателей (вариант 7: + Q1, Q3, IQR)."""
    print(f"Среднее арифметическое : {stats['mean']:>10.4f}")
    print(f"Медиана                : {stats['median']:>10.4f}")
    print(f"Размах (max - min)     : {stats['spread']:>10.4f}")
    print(f"min / max              : {stats['min']:>10.4f} / {stats['max']:.4f}")
    print(f"Квартиль Q1 (25%)      : {stats['q1']:>10.4f}")
    print(f"Квартиль Q3 (75%)      : {stats['q3']:>10.4f}")
    print(f"IQR = Q3 - Q1          : {stats['iqr']:>10.4f}")


def print_footer() -> None:
    print("=" * 60)


# ---------------------------------------------------------------------------
# Разбор аргументов
# ---------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Алгоритмическая обработка числовых рядов (вариант 7)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--kind",
        choices=["discrete", "random", "sine", "trend"],
        default="discrete",
        help="тип генерируемого ряда",
    )
    parser.add_argument(
        "--n", type=int, default=1000,
        help="количество точек в ряде",
    )
    parser.add_argument(
        "--window", type=int, default=10,
        help="размер окна для скользящих средних (k)",
    )
    parser.add_argument(
        "--values", type=str, default="1,2,3,4,5",
        help="значения дискретного ряда через запятую (вариант 7)",
    )
    parser.add_argument(
        "--weights", type=str, default="1,2,4,2,1",
        help="веса значений через запятую (вариант 7)",
    )
    parser.add_argument(
        "--alpha", type=float, default=0.3,
        help="коэффициент сглаживания для EMA, 0 < alpha <= 1",
    )
    parser.add_argument(
        "--ema", action="store_true",
        help="дополнительно вывести EMA",
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="зерно ГПСЧ для воспроизводимости",
    )
    parser.add_argument(
        "--full", action="store_true",
        help="печатать ряды целиком (по умолчанию — первые 10 значений)",
    )
    parser.add_argument(
        "--benchmark", action="store_true",
        help="замерить время выполнения SMA для list и deque",
    )
    parser.add_argument(
        "--save", metavar="FILE", help="сохранить ряд в JSON-файл"
    )
    parser.add_argument(
        "--load", metavar="FILE",
        help="загрузить ряд из файла (JSON, CSV или txt; '-' — stdin)",
    )
    parser.add_argument(
        "--export", metavar="FILE", help="экспорт в CSV"
    )
    parser.add_argument(
        "--json", action="store_true",
        help="вывести результат в формате JSON",
    )
    return parser


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main(argv: List[str] | None = None) -> int:
    """Точка входа. Возвращает код выхода (0 — успех, 1 — ошибка)."""
    args = build_parser().parse_args(argv)
    try:
        if args.load:
            data = load_series_auto(args.load)
        else:
            values = parse_float_list(args.values)
            weights = parse_float_list(args.weights)
            data = build_series(args.kind, args.n, args.seed, values, weights)

        stats = summarize(data)
        sma = simple_moving_average(data, args.window)
        wma = weighted_moving_average(data, args.window)
        ema = exponential_moving_average(data, args.alpha) if args.ema else None
        timings = (
            benchmark_moving_average(data, args.window, repeats=1000)
            if args.benchmark
            else None
        )
    except ValueError as err:
        # Понятное сообщение вместо «сырого» трейсбека
        print(f"Ошибка: {err}", file=sys.stderr)
        return 1

    if args.json:
        # Режим JSON: машинночитаемый вывод вместо обычной печати
        payload = {"data": data, "stats": stats, "sma": sma, "wma": wma}
        if ema is not None:
            payload["ema"] = ema
        print(json.dumps(payload, indent=2))
        return 0

    print_header(args.kind if not args.load else f"загружено из {args.load}", len(data))
    print_stats(stats)
    print_series("Исходный ряд", data, full=args.full)
    print_series(f"SMA (window={args.window})", sma, full=args.full)
    print_series(f"SMA через deque (window={args.window})", simple_moving_average_deque(data, args.window), full=args.full)
    print_series(f"WMA (window={args.window})", wma, full=args.full)
    if ema is not None:
        print_series(f"EMA (alpha={args.alpha})", ema, full=args.full)

    if timings is not None:
        print("-" * 60)
        print("Замер времени выполнения SMA (среднее за 1000 повторов):")
        print(f"  list  : {timings['list']:.8f} c")
        print(f"  deque : {timings['deque']:.8f} c")
        print(f"  отношение (list/deque): {timings['list'] / timings['deque']:.2f}")

    if args.save:
        meta = {
            "kind": args.kind,
            "n": len(data),
            "seed": args.seed,
            "window": args.window,
            "variant": 7,
        }
        save_series_json(data, args.save, meta=meta)
        print(f"\nСохранено в {args.save}")

    if args.export:
        with open(args.export, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["i", "value", "sma", "wma"])
            for i, v in enumerate(data):
                w.writerow([i, v, sma[i] if i < len(sma) else "", wma[i] if i < len(wma) else ""])
        print(f"Экспортировано в {args.export}")

    print_footer()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
