"""Чтение числовых рядов из txt и csv (и автоопределение формата).

- load_series_txt: каждое число в отдельной строке; "-" — stdin;
  нечисловая строка — ValueError с номером строки.
- load_series_csv: колонка "value" (или первая колонка, если заголовка нет).
- load_series_auto: по расширению файла (.json -> JSON, .csv -> CSV,
  иначе -> txt); "-" — stdin.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path
from typing import List, Union

PathLike = Union[str, Path]


def load_series_txt(path: PathLike) -> List[float]:
    """Читает ряд из txt: каждое число в отдельной строке.

    Args:
        path: путь к файлу или "-" для чтения из stdin.

    Returns:
        Список float.

    Raises:
        ValueError: если файл пуст или строка не является числом
            (в сообщении указывается номер строки).
    """
    if path == "-":
        lines = sys.stdin
        close = False
    else:
        lines = open(path, encoding="utf-8")
        close = True
    result: List[float] = []
    try:
        for i, line in enumerate(lines, start=1):
            text = line.strip()
            if not text:
                continue
            try:
                result.append(float(text.replace(",", ".")))
            except ValueError as err:
                raise ValueError(f"Строка {i}: не число ({text!r})") from err
    finally:
        if close:
            lines.close()
    if not result:
        raise ValueError("Файл пуст: не найдено ни одного числа")
    return result


def load_series_csv(path: PathLike, value_column: str = "value") -> List[float]:
    """Читает ряд из CSV: колонка value_column (по умолчанию "value").

    Если первая строка не содержит колонку value_column, она считается
    заголовком общего вида и данные берутся из первой колонки.

    Raises:
        ValueError: если файл пуст или встречена нечисловая ячейка
            (в сообщении указывается номер строки).
    """
    with open(path, newline="", encoding="utf-8") as f:
        rows = [row for row in csv.reader(f) if row]
    if not rows:
        raise ValueError("CSV пуст: не найдено ни одной строки")
    start = 0
    col = 0
    if value_column in [c.strip().lower() for c in rows[0]]:
        col = [c.strip().lower() for c in rows[0]].index(value_column)
        start = 1
    result: List[float] = []
    for i, row in enumerate(rows[start:], start=start + 1):
        if col >= len(row):
            raise ValueError(f"Строка {i}: нет колонки {value_column!r}")
        text = row[col].strip()
        try:
            result.append(float(text.replace(",", ".")))
        except ValueError as err:
            raise ValueError(f"Строка {i}: не число ({text!r})") from err
    if not result:
        raise ValueError("CSV не содержит числовых данных")
    return result


def load_series_auto(path: PathLike) -> List[float]:
    """Автоопределение формата по расширению: .json, .csv, иначе txt."""
    if path == "-":
        return load_series_txt(path)
    suffix = Path(path).suffix.lower()
    if suffix == ".json":
        from .io_json import load_series_json
        return load_series_json(path)
    if suffix == ".csv":
        return load_series_csv(path)
    return load_series_txt(path)
