#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Thu thập dữ liệu chứng khoán bằng vnstock và các nguồn tin tức."""

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
    """Lớp thu thập dữ liệu giá cổ phiếu Việt Nam."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36"
        })
        self.data_dir = "data/raw"
        ensure_directory(self.data_dir)
        logger.info("Khởi tạo DataCollector thành công")

    def get_available_symbols(self) -> List[str]:
        """Trả về các mã cổ phiếu Việt Nam được ứng dụng hỗ trợ."""
        return ["VHM", "FPT", "VCB", "HPG", "VIC", "VNM", "TCB", "MBB"]

    def _save_raw_data(self, data: pd.DataFrame, name: str) -> None:
        """Lưu dữ liệu thu thập được dưới dạng CSV."""
        file_path = os.path.join(self.data_dir, f"{name}.csv")
        data.to_csv(file_path, index=False, encoding="utf-8-sig")

    @staticmethod
    def normalize_ohlcv(data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """Normalize vnstock OHLCV data to the application's stable schema."""
        if data is None or data.empty:
            raise ValueError("OHLCV data is empty")

        symbol = str(symbol).upper().replace(".VN", "").strip()
        if not re.fullmatch(r"[A-Z0-9]{2,10}", symbol):
            raise ValueError(f"Invalid stock symbol: {symbol!r}")

        column_map = {
            "time": "Date",
            "date": "Date",
            "datetime": "Date",
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close",
            "volume": "Volume",
        }
        normalized = data.copy().rename(
            columns={
                column: column_map.get(str(column).strip().lower(), column)
                for column in data.columns
            }
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
        normalized = normalized.dropna(subset=required)
        normalized = normalized.drop_duplicates(subset=["Date"], keep="last")
        normalized = normalized.sort_values("Date").reset_index(drop=True)
        if normalized.empty:
            raise ValueError("No valid OHLCV rows remain after normalization")
        return normalized

    def save_to_database(self, data: pd.DataFrame, db_path: Optional[str] = None) -> int:
        """Persist normalized OHLCV rows to SQLite."""
        from data.database import DatabaseManager

        return DatabaseManager(db_path=db_path).upsert_stock_data(data)

    def collect_stock_data(self, symbol: str, days: int = 365) -> Optional[pd.DataFrame]:
        """Thu thập dữ liệu OHLCV từ vnstock."""
        try:
            symbol = symbol.upper().replace(".VN", "").strip()
            if not symbol:
                raise ValueError("Mã cổ phiếu không được để trống")
            if days <= 0:
                raise ValueError("days phải lớn hơn 0")

            logger.info(f"Đang thu thập dữ liệu cổ phiếu: {symbol}")
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            # Lazy import keeps cache processing and unit tests independent of
            # the optional network client until a live collection is requested.
            from vnstock import Quote

            quote = Quote(symbol=symbol, source="VCI")
            df = quote.history(
                start=start_date.strftime("%Y-%m-%d"),
                end=end_date.strftime("%Y-%m-%d"),
                interval="1D",
            )

            if df is None or df.empty:
                logger.warning(f"Không có dữ liệu cho {symbol}")
                return None

            # Chuẩn hóa tên cột từ vnstock về schema nội bộ của ứng dụng.
            column_map = {
                "time": "Date",
                "date": "Date",
                "open": "Open",
                "high": "High",
                "low": "Low",
                "close": "Close",
                "volume": "Volume",
            }
            df = df.rename(
                columns={
                    column: column_map.get(str(column).lower(), column)
                    for column in df.columns
                }
            )
            required_columns = ["Date", "Open", "High", "Low", "Close", "Volume"]
            missing_columns = [
                column for column in required_columns
                if column not in df.columns
            ]
            if missing_columns:
                raise ValueError(f"vnstock thiếu các cột bắt buộc: {missing_columns}")

            df = df[required_columns].copy()
            df["Date"] = pd.to_datetime(df["Date"])
            df["Symbol"] = symbol
            df = self.normalize_ohlcv(df, symbol)

            self._save_raw_data(
                df, f"stock_{symbol}_{datetime.now().strftime('%Y%m%d')}"
            )
            self.save_to_database(df)
            logger.info(f"Đã thu thập {len(df)} ngày dữ liệu cho {symbol}")
            return df

        except Exception as exc:
            logger.error(f"Lỗi khi thu thập dữ liệu {symbol}: {exc}")
            return None
