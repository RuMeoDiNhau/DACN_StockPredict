#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Collect daily OHLCV data from vnstock."""

import os
import re
from datetime import datetime, timedelta
from typing import List, Optional

import pandas as pd
import requests

from utils.helpers import ensure_directory
from utils.logger import setup_logger

logger = setup_logger(__name__)


class DataCollector:
    """Fetch and normalize Vietnamese stock daily prices."""

    def __init__(self, data_dir: str = "data/raw"):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36"
        })
        self.data_dir = data_dir
        ensure_directory(self.data_dir)

    def get_available_symbols(self) -> List[str]:
        return ["VHM", "FPT", "VCB", "HPG", "VIC", "VNM", "TCB", "MBB"]

    def _save_raw_data(self, data: pd.DataFrame, name: str) -> None:
        file_path = os.path.join(self.data_dir, f"{name}.csv")
        data.to_csv(file_path, index=False, encoding="utf-8-sig")

    def save_raw_data(self, data: pd.DataFrame, symbol: str) -> str:
        """Save one normalized batch and return the CSV path."""
        name = f"stock_{symbol.upper().strip()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self._save_raw_data(data, name)
        return os.path.join(self.data_dir, f"{name}.csv")

    @staticmethod
    def normalize_ohlcv(
        data: pd.DataFrame, symbol: str, drop_invalid: bool = True
    ) -> pd.DataFrame:
        """Normalize vnstock columns to the application's stable schema."""
        if data is None or data.empty:
            raise ValueError("OHLCV data is empty")
        symbol = str(symbol).upper().replace(".VN", "").strip()
        if not re.fullmatch(r"[A-Z0-9]{2,10}", symbol):
            raise ValueError(f"Invalid stock symbol: {symbol!r}")
        column_map = {
            "time": "Date", "date": "Date", "datetime": "Date",
            "open": "Open", "high": "High", "low": "Low",
            "close": "Close", "volume": "Volume",
        }
        normalized = data.copy().rename(
            columns={column: column_map.get(str(column).strip().lower(), column)
                     for column in data.columns}
        )
        required = ["Date", "Open", "High", "Low", "Close", "Volume"]
        missing = [column for column in required if column not in normalized.columns]
        if missing:
            raise ValueError(f"vnstock is missing required columns: {missing}")
        normalized = normalized[required].copy()
        normalized["Date"] = pd.to_datetime(normalized["Date"], errors="coerce")
        for column in required[1:]:
            normalized[column] = pd.to_numeric(normalized[column], errors="coerce")
        normalized["Symbol"] = symbol
        if drop_invalid:
            normalized = normalized.dropna(subset=required)
            normalized = normalized.drop_duplicates(subset=["Date"], keep="last")
        normalized = normalized.sort_values("Date").reset_index(drop=True)
        if normalized.empty:
            raise ValueError("No valid OHLCV rows remain after normalization")
        return normalized

    def save_to_database(self, data: pd.DataFrame, db_path: Optional[str] = None) -> int:
        from data.database import DatabaseManager
        return DatabaseManager(db_path=db_path).upsert_stock_data(data)

    def fetch_stock_data(
        self,
        symbol: str,
        days: int = 365,
        source: str = "VCI",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Optional[pd.DataFrame]:
        """Fetch and normalize OHLCV without writing a database or CSV."""
        symbol = symbol.upper().replace(".VN", "").strip()
        if not re.fullmatch(r"[A-Z0-9]{2,10}", symbol):
            raise ValueError(f"Invalid stock symbol: {symbol!r}")
        if days <= 0:
            raise ValueError("days must be greater than zero")
        end_value = datetime.now() if end_date is None else datetime.fromisoformat(str(end_date))
        start_value = (
            end_value - timedelta(days=days)
            if start_date is None
            else datetime.fromisoformat(str(start_date))
        )
        # Lazy import keeps offline tests independent of the optional client.
        from vnstock import Quote
        quote = Quote(symbol=symbol, source=source)
        raw = quote.history(
            start=start_value.strftime("%Y-%m-%d"),
            end=end_value.strftime("%Y-%m-%d"),
            interval="1D",
        )
        if raw is None or raw.empty:
            return None
        return self.normalize_ohlcv(raw, symbol, drop_invalid=False)

    def collect_stock_data(
        self, symbol: str, days: int = 365, source: str = "VCI"
    ) -> Optional[pd.DataFrame]:
        """Legacy-compatible fetch, raw-save, and database-save operation."""
        try:
            data = self.fetch_stock_data(symbol, days=days, source=source)
            if data is not None:
                from data.validation import validate_ohlcv
                data = validate_ohlcv(data, symbol)
                self.save_raw_data(data, symbol)
                self.save_to_database(data)
            return data
        except Exception as exc:
            logger.error("Collection failed for %s: %s", symbol, exc)
            return None
