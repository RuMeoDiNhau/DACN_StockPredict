import os
import sys
import tempfile
import unittest

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.collector import DataCollector
from data.database import DatabaseManager
from data.processor import DataProcessor


class TestDataPipeline(unittest.TestCase):
    def setUp(self):
        self.raw = pd.DataFrame(
            {
                "time": ["2024-01-03", "2024-01-02", "2024-01-02", "2024-01-01"],
                "open": [103, 102, 202, 100],
                "high": [105, 104, 204, 101],
                "low": [101, 100, 200, 99],
                "close": [104, 103, 203, 100],
                "volume": [1000, 900, 800, 700],
            }
        )

    def test_normalize_ohlcv_has_stable_schema(self):
        result = DataCollector.normalize_ohlcv(self.raw, "vhm.vn")
        self.assertEqual(
            list(result.columns),
            ["Date", "Open", "High", "Low", "Close", "Volume", "Symbol"],
        )
        self.assertEqual(len(result), 3)
        self.assertEqual(result.iloc[0]["Symbol"], "VHM")
        self.assertTrue(result["Date"].is_monotonic_increasing)

    def test_processor_removes_invalid_rows_and_fills_isolated_missing_values(self):
        source = DataCollector.normalize_ohlcv(self.raw, "VHM")
        source.loc[1, "Close"] = None
        source.loc[2, "Low"] = -1
        result = DataProcessor().clean_data(source)
        self.assertFalse(result.isna().any().any())
        self.assertTrue((result["Close"] > 0).all())
        self.assertTrue((result["Low"] > 0).all())

    def test_database_upsert_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            db_path = os.path.join(directory, "stock.db")
            database = DatabaseManager(db_path)
            rows = DataCollector.normalize_ohlcv(self.raw, "VHM")
            self.assertEqual(database.upsert_stock_data(rows), 3)
            self.assertEqual(database.upsert_stock_data(rows), 3)
            stored = database.get_stock_data("VHM", limit=10)
            self.assertEqual(len(stored), 3)
            self.assertEqual(list(stored["Symbol"].unique()), ["VHM"])


if __name__ == "__main__":
    unittest.main()
