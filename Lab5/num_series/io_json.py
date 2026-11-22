"""Сохранение и чтение числовых рядов в формате JSON.

Формат файла:
{
  "meta": {
    "kind": "discrete",
    "n": 1000,
    "seed": 42,
    "created": "2025-01-15T10:30:00"
  },
  "data": [1.0, 3.0, 3.0, ...]
}

Метаданные опциональны — при чтении они не обязательны.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

PathLike = Union[str, Path]


def save_series_json(
    data: List[float],
    path: PathLike,
    meta: Optional[Dict[str, Any]] = None,
    indent: int = 2,
) -> None:
    """Сохраняет числовой ряд в JSON-файл.

    Args:
        data: числовой ряд (непустой список float/int).
        path: путь к файлу (создастся или перезапишется).
        meta: произвольные метаданные (kind, seed, ...). Автоматически
            добавляется поле "created" с текущим временем.
        indent: отступ для pretty-print JSON.

    Raises:
        ValueError: если data пуст.
    """
    if not data:
        raise ValueError("Нельзя сохранить пустой ряд")
    payload: Dict[str, Any] = {"data": [float(x) for x in data]}
    meta_out = dict(meta) if meta else {}
    meta_out["created"] = datetime.now().isoformat(timespec="seconds")
    payload["meta"] = meta_out
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=indent)


def load_series_json(path: PathLike) -> List[float]:
    """Читает числовой ряд из JSON-файла.

    Args:
        path: путь к JSON-файлу формата {"meta": ..., "data": [...]}.

    Returns:
        Список float.

    Raises:
        ValueError: если структура файла не соответствует ожидаемой
            или в data встречаются нечисловые элементы.
    """
    with open(path, encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, dict) or "data" not in payload:
        raise ValueError(f"Ожидался JSON с ключом 'data': {path}")
    data = payload["data"]
    if not isinstance(data, list) or not data:
        raise ValueError("Ключ 'data' должен быть непустым списком чисел")
    result: List[float] = []
    for i, x in enumerate(data, start=1):
        try:
            result.append(float(x))
        except (TypeError, ValueError) as err:
            raise ValueError(f"Элемент №{i} не число: {x!r}") from err
    return result
