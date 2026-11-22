"""Тесты CLI (main.py) и модулей ввода-вывода."""

import contextlib
import io
import json
import os
import tempfile
import unittest

import main as app
from num_series import io_json, io_file
from num_series.generator import discrete_series


class TestParser(unittest.TestCase):
    def test_defaults(self):
        args = app.build_parser().parse_args([])
        self.assertEqual(args.kind, "discrete")
        self.assertEqual(args.n, 1000)
        self.assertEqual(args.window, 10)
        self.assertEqual(args.seed, 42)

    def test_invalid_kind(self):
        with self.assertRaises(SystemExit):
            app.build_parser().parse_args(["--kind", "unknown"])


class TestBuildSeries(unittest.TestCase):
    def test_discrete_values(self):
        data = app.build_series("discrete", 100, 1)
        self.assertEqual(len(data), 100)
        self.assertTrue(set(data).issubset({1.0, 2.0, 3.0, 4.0, 5.0}))

    def test_custom_values_weights(self):
        data = app.build_series("discrete", 50, 1, values=[7, 8], weights=[1, 0])
        self.assertTrue(set(data).issubset({7.0}))

    def test_unknown_kind(self):
        with self.assertRaises(ValueError):
            app.build_series("unknown", 10, 1)

    def test_parse_float_list(self):
        self.assertEqual(app.parse_float_list("1,2,3"), [1.0, 2.0, 3.0])
        self.assertIsNone(app.parse_float_list(None))
        with self.assertRaises(ValueError):
            app.parse_float_list("1,a,3")


class TestMain(unittest.TestCase):
    def run_main(self, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = app.main(argv)
        return rc, out.getvalue()

    def test_basic_run(self):
        rc, out = self.run_main(["--kind", "discrete", "--n", "50", "--window", "5", "--seed", "1"])
        self.assertEqual(rc, 0)
        for phrase in ("Квартиль Q1", "Квартиль Q3", "IQR", "WMA", "SMA"):
            self.assertIn(phrase, out)

    def test_even_and_odd_n(self):
        # Краевой кейс варианта 7: чётное и нечётное n
        for n in (9, 10):
            rc, out = self.run_main(["--kind", "discrete", "--n", str(n), "--window", "3", "--seed", "2"])
            self.assertEqual(rc, 0)
            self.assertIn("Медиана", out)

    def test_window_greater_than_n(self):
        rc, _ = self.run_main(["--kind", "discrete", "--n", "5", "--window", "10"])
        self.assertEqual(rc, 1)

    def test_benchmark(self):
        rc, out = self.run_main(
            ["--kind", "discrete", "--n", "50", "--window", "5", "--benchmark"]
        )
        self.assertEqual(rc, 0)
        self.assertIn("Замер времени выполнения SMA", out)
        self.assertIn("list", out)
        self.assertIn("deque", out)

    def test_json_output(self):
        rc, out = self.run_main(
            ["--kind", "discrete", "--n", "20", "--window", "3", "--json"]
        )
        self.assertEqual(rc, 0)
        payload = json.loads(out)
        for key in ("data", "stats", "sma", "wma"):
            self.assertIn(key, payload)
        self.assertIn("iqr", payload["stats"])

    def test_save_load_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "series.json")
            rc, _ = self.run_main(
                ["--kind", "discrete", "--n", "50", "--window", "5", "--seed", "3", "--save", path]
            )
            self.assertEqual(rc, 0)
            self.assertTrue(os.path.exists(path))
            loaded = io_json.load_series_json(path)
            self.assertEqual(loaded, app.build_series('discrete', 50, 3))

    def test_export_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "out.csv")
            rc, _ = self.run_main(
                ["--kind", "discrete", "--n", "20", "--window", "3", "--export", path]
            )
            self.assertEqual(rc, 0)
            with open(path, encoding="utf-8") as f:
                lines = f.read().strip().splitlines()
            self.assertEqual(lines[0], "i,value,sma,wma")
            self.assertEqual(len(lines), 21)


class TestIO(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def path(self, name):
        return os.path.join(self.tmp.name, name)

    def test_load_txt(self):
        p = self.path("s.txt")
        with open(p, "w", encoding="utf-8") as f:
            f.write("1\n2.5\n\n3\n")
        self.assertEqual(io_file.load_series_txt(p), [1.0, 2.5, 3.0])

    def test_load_txt_non_numeric_line(self):
        p = self.path("bad.txt")
        with open(p, "w", encoding="utf-8") as f:
            f.write("1\nabc\n")
        with self.assertRaises(ValueError) as cm:
            io_file.load_series_txt(p)
        self.assertIn("Строка 2", str(cm.exception))

    def test_load_csv_with_header(self):
        p = self.path("s.csv")
        with open(p, "w", encoding="utf-8") as f:
            f.write("i,value\n0,1.5\n1,2.5\n")
        self.assertEqual(io_file.load_series_csv(p), [1.5, 2.5])

    def test_load_csv_without_header(self):
        p = self.path("s2.csv")
        with open(p, "w", encoding="utf-8") as f:
            f.write("4.5,1\n5.5,2\n")
        self.assertEqual(io_file.load_series_csv(p), [4.5, 5.5])

    def test_load_auto_json(self):
        p = self.path("s.json")
        io_json.save_series_json([1.0, 2.0], p, meta={"kind": "test"})
        self.assertEqual(io_file.load_series_auto(p), [1.0, 2.0])

    def test_load_json_bad_structure(self):
        p = self.path("bad.json")
        with open(p, "w", encoding="utf-8") as f:
            f.write(json.dumps({"nope": 1}))
        with self.assertRaises(ValueError):
            io_file.load_series_auto(p)


if __name__ == "__main__":
    unittest.main()
