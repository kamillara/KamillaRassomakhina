"""Журнал ошибок ввода.

Хранит записи о некорректных вводах пользователя в памяти
и дописывает их в файл LOG_FILE с меткой времени.
"""

from datetime import datetime

from constants import LOG_FILE

_entries: list[str] = []


def log_error(message: str) -> None:
    """Добавить запись в журнал и дописать её в файл.

    Args:
        message: текст ошибки ввода.
    """
    entry = f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {message}"
    _entries.append(entry)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(entry + "\n")
    except OSError:
        pass  # файл недоступен — программа не должна падать


def get_entries() -> list[str]:
    """Вернуть копию журнала в памяти.

    Returns:
        Список строк журнала.
    """
    return list(_entries)


def clear() -> None:
    """Очистить журнал (используется в тестах)."""
    _entries.clear()
