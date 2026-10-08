import os
import tempfile
import unittest

import pandas as pd

from data.database import DatabaseManager
from data.validation import validate_ohlcv
from scripts.collect_ohlcv import (
    DEFAULT_INITIAL_DAYS,
    OVERLAP_DAYS,
    parse_symbols,
    positive_days,
    run_daily_update,
)


def make_rows(symbol="VHM", dates=None):
    dates = dates or ["2026-10-01", "2026-10-02"]
    return pd.DataFrame({
        "Symbol": [symbol] * len(dates),
        "Date": dates,
        "Open": [100.0] * len(dates),
        "High": [110.0] * len(dates),
        "Low": [90.0] * len(dates),
        "Close": [105.0] * len(dates),
        "Volume": [1000.0] * len(dates),
    })


class FakeCollector:
    def __init__(self, rows_by_symbol=None, failures=None):
        self.rows_by_symbol = rows_by_symbol or {}
        self.failures = failures or set()
        self.calls = []
        self.saved = []

    def fetch_stock_data(self, symbol, days, source, start_date=None):
        self.calls.append((symbol, days, source, start_date))
        if symbol in self.failures:
            raise RuntimeError("mock source failure")
        return self.rows_by_symbol.get(symbol, make_rows(symbol))

    def save_raw_data(self, data, symbol):
        self.saved.append((symbol, len(data)))
        return os.path.join("data", "raw", f"{symbol}.csv")


class TestCollectionAutomation(unittest.TestCase):
    def test_parse_symbols_and_days(self):
        self.assertEqual(parse_symbols(" vhm, FPT,VHM, ,fpt "), ["VHM", "FPT"])
        self.assertEqual(positive_days("1825"), 1825)
        with self.assertRaises(ValueError):
            parse_symbols(" , ")
        with self.assertRaises(Exception):
            positive_days("0")

    def test_invalid_ohlcv_is_rejected_before_upsert(self):
        invalid = make_rows()
        invalid.loc[1, "Close"] = 120
        with self.assertRaises(ValueError):
            validate_ohlcv(invalid, "VHM")

    def test_daily_update_uses_overlap_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            database = DatabaseManager(os.path.join(directory, "stock.db"))
            database.upsert_stock_data(make_rows("VHM", ["2026-10-01", "2026-10-02"]))
            collector = FakeCollector({"VHM": make_rows("VHM", ["2026-09-27", "2026-10-03"])})

            self.assertEqual(run_daily_update(["VHM"], "VCI", collector=collector, database=database), 0)
            self.assertEqual(collector.calls[0][0], "VHM")
            self.assertEqual(collector.calls[0][3], "2026-09-27")
            self.assertEqual(collector.calls[0][1], (pd.Timestamp.today().date() - pd.Timestamp("2026-09-27").date()).days)
            first_count = len(database.get_stock_data("VHM", limit=100))
            self.assertEqual(run_daily_update(["VHM"], "VCI", collector=collector, database=database), 0)
            self.assertEqual(len(database.get_stock_data("VHM", limit=100)), first_count)

    def test_missing_symbol_uses_initial_window_and_failure_continues(self):
        with tempfile.TemporaryDirectory() as directory:
            database = DatabaseManager(os.path.join(directory, "stock.db"))
            collector = FakeCollector({"FPT": make_rows("FPT")}, failures={"VHM"})
            self.assertEqual(run_daily_update(["VHM", "FPT"], "VCI", collector=collector, database=database), 1)
            self.assertEqual(collector.calls[1][1], DEFAULT_INITIAL_DAYS)
            self.assertIsNotNone(database.get_ingestion_status("VHM")["last_error"])
            self.assertEqual(database.get_ingestion_status("FPT")["last_error"], None)
            self.assertEqual(len(database.get_stock_data("FPT", limit=100)), 2)


if __name__ == "__main__":
    unittest.main()
