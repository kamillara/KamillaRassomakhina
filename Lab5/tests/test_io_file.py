"""Тесты чтения txt/CSV и автоподбора формата (tmp_path)."""

import pytest

from num_series.io_file import load_series_auto, load_series_csv, load_series_txt
from num_series.io_json import save_series_json


# ---------------------------------------------------------------------------
# TXT: каждое число — отдельная строка
# ---------------------------------------------------------------------------
def test_txt_roundtrip(tmp_path):
    path = tmp_path / "series.txt"
    path.write_text("1.5\n2\n-3,5\n", encoding="utf-8")  # запятая -> точка
    assert load_series_txt(path) == [1.5, 2.0, -3.5]


def test_txt_empty(tmp_path):
    path = tmp_path / "empty.txt"
    path.write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="Файл пуст"):
        load_series_txt(path)


def test_txt_bad_line(tmp_path):
    path = tmp_path / "bad.txt"
    path.write_text("1\nabc\n3\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Строка 2"):
        load_series_txt(path)


# ---------------------------------------------------------------------------
# CSV
# ---------------------------------------------------------------------------
def test_csv_with_header(tmp_path):
    path = tmp_path / "series.csv"
    path.write_text("value\n1\n2\n3\n", encoding="utf-8")
    assert load_series_csv(path) == [1.0, 2.0, 3.0]


def test_csv_without_header(tmp_path):
    path = tmp_path / "series.csv"
    path.write_text("1\n2\n3\n", encoding="utf-8")
    assert load_series_csv(path) == [1.0, 2.0, 3.0]


def test_csv_decimal_comma_quoted(tmp_path):
    # Запятая-разделитель целой/дробной части: ячейка берётся в кавычки,
    # иначе csv.reader разрежет "1,5" на две колонки.
    path = tmp_path / "decimal.csv"
    path.write_text('value\n"1,5"\n"2,25"\n', encoding="utf-8")
    assert load_series_csv(path) == [1.5, 2.25]


def test_csv_empty(tmp_path):
    path = tmp_path / "empty.csv"
    path.write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="CSV пуст"):
        load_series_csv(path)


def test_csv_bad_cell(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("value\n1\nabc\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Строка 3"):
        load_series_csv(path)


def test_csv_value_not_first_column(tmp_path):
    path = tmp_path / "wide.csv"
    path.write_text("name,value\na,1\nb,2\n", encoding="utf-8")
    assert load_series_csv(path) == [1.0, 2.0]


# ---------------------------------------------------------------------------
# Автоопределение формата
# ---------------------------------------------------------------------------
def test_auto_json(tmp_path):
    path = tmp_path / "series.json"
    save_series_json([1.0, 2.0], path)
    assert load_series_auto(path) == [1.0, 2.0]


def test_auto_csv(tmp_path):
    path = tmp_path / "series.csv"
    path.write_text("value\n4\n5\n", encoding="utf-8")
    assert load_series_auto(path) == [4.0, 5.0]


def test_auto_txt_by_unknown_extension(tmp_path):
    path = tmp_path / "series.dat"
    path.write_text("7\n8\n", encoding="utf-8")
    assert load_series_auto(path) == [7.0, 8.0]


def test_missing_file_raises(tmp_path):
    with pytest.raises(OSError):
        load_series_txt(tmp_path / "no_such_file.txt")
