"""Интеграционные тесты CLI (main.py) через subprocess."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

import main as app
from num_series.generator import discrete_series

ROOT = Path(__file__).resolve().parent.parent


def run_cli(*args: str) -> subprocess.CompletedProcess:
    """Запускает main.py в отдельном процессе операционной системы."""
    return subprocess.run(
        [sys.executable, str(ROOT / "main.py"), *args],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )


# ---------------------------------------------------------------------------
# Разбор аргументов (модульный уровень)
# ---------------------------------------------------------------------------
def test_parser_defaults():
    args = app.build_parser().parse_args([])
    assert args.kind == "discrete"
    assert args.n == 1000
    assert args.window == 10
    assert args.seed == 42


def test_parser_invalid_kind():
    with pytest.raises(SystemExit):
        app.build_parser().parse_args(["--kind", "unknown"])


@pytest.mark.parametrize(
    "text, expected",
    [
        ("1,2,3", [1.0, 2.0, 3.0]),
        (" 1 , 2 ", [1.0, 2.0]),
        (None, None),
        ("", None),
    ],
)
def test_parse_float_list(text, expected):
    assert app.parse_float_list(text) == expected


def test_parse_float_list_bad():
    with pytest.raises(ValueError):
        app.parse_float_list("1,a,3")


def test_build_series_discrete():
    data = app.build_series("discrete", 100, 1)
    assert len(data) == 100
    assert set(data).issubset({1.0, 2.0, 3.0, 4.0, 5.0})


def test_build_series_unknown_kind():
    with pytest.raises(ValueError, match="Неизвестный тип ряда"):
        app.build_series("unknown", 10, 1)


# ---------------------------------------------------------------------------
# Интеграционные тесты CLI через subprocess
# ---------------------------------------------------------------------------
def test_cli_help():
    result = run_cli("--help")
    assert result.returncode == 0
    assert "--window" in result.stdout


def test_cli_basic_run():
    result = run_cli("--kind", "discrete", "--n", "50", "--window", "5", "--seed", "1")
    assert result.returncode == 0
    for phrase in ("Квартиль Q1", "Квартиль Q3", "IQR", "WMA", "SMA"):
        assert phrase in result.stdout


@pytest.mark.parametrize("n", ["9", "10"])
def test_cli_even_and_odd_n(n):
    """Краевой кейс варианта 7: чётное и нечётное n."""
    result = run_cli("--kind", "discrete", "--n", n, "--window", "3", "--seed", "2")
    assert result.returncode == 0
    assert "Медиана" in result.stdout


def test_cli_benchmark():
    result = run_cli("--n", "300", "--window", "5", "--benchmark")
    assert result.returncode == 0
    assert "list" in result.stdout
    assert "deque" in result.stdout


def test_cli_window_greater_than_n():
    result = run_cli("--n", "5", "--window", "10")
    assert result.returncode == 1
    assert "Ошибка" in result.stderr


def test_cli_save_and_load(tmp_path):
    saved = tmp_path / "series.json"
    save_res = run_cli("--n", "40", "--seed", "3", "--save", str(saved))
    assert save_res.returncode == 0
    assert saved.exists()

    load_res = run_cli("--load", str(saved), "--window", "5")
    assert load_res.returncode == 0
    assert "загружено из" in load_res.stdout


def test_cli_export_csv(tmp_path):
    out = tmp_path / "out.csv"
    result = run_cli("--n", "30", "--window", "4", "--export", str(out))
    assert result.returncode == 0
    assert out.exists()
    lines = out.read_text(encoding="utf-8").strip().splitlines()
    assert lines[0] == "i,value,sma,wma"
    assert len(lines) == 31  # заголовок + 30 строк данных


def test_cli_json_output():
    result = run_cli("--n", "20", "--window", "4", "--json")
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert set(payload) == {"data", "stats", "sma", "wma"}
    assert len(payload["data"]) == 20
    assert len(payload["sma"]) == 20 - 4 + 1
    assert set(payload["stats"]) >= {"mean", "median", "q1", "q3", "iqr"}


def test_cli_unknown_kind_subprocess():
    result = run_cli("--kind", "unknown")
    assert result.returncode != 0
