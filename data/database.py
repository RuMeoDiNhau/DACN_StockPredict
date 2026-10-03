#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module quản lý database SQLite cho ứng dụng
"""

import sqlite3
import pandas as pd
import os
from datetime import datetime
from typing import List, Dict, Optional, Any
from contextlib import contextmanager

from utils.logger import setup_logger
from config.settings import Config

logger = setup_logger(__name__)

class DatabaseManager:
    """
    Lớp quản lý database SQLite
    """
    
    def __init__(self, db_path: str = None):
        """
        Khởi tạo DatabaseManager
        
        Args:
            db_path: Đường dẫn database file
        """
        self.db_path = db_path or Config.DATABASE_PATH
        
        # Tạo thư mục chứa database nếu chưa có
        db_dir = os.path.dirname(os.path.abspath(self.db_path))
        os.makedirs(db_dir, exist_ok=True)
        
        # Khởi tạo database
        self.init_database()
        
        logger.info(f"💾 Khởi tạo DatabaseManager: {self.db_path}")

    def init_database(self) -> None:
        """Tạo các bảng lưu dữ liệu giá và dự báo nếu chưa tồn tại."""
        with self.get_connection() as conn:
            conn.executescript('''
                CREATE TABLE IF NOT EXISTS stock_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    date TEXT NOT NULL,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume REAL,
                    UNIQUE(symbol, date)
                );
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    prediction_date TEXT NOT NULL,
                    predicted_price REAL,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_stock_data_symbol_date
                    ON stock_data(symbol, date);
            ''')
            conn.commit()

    def upsert_stock_data(self, data: pd.DataFrame) -> int:
        """Insert or update normalized OHLCV rows and return row count.

        The operation is idempotent by ``(symbol, date)`` so daily collection
        can safely be run again without creating duplicates.
        """
        required = ["Symbol", "Date", "Open", "High", "Low", "Close", "Volume"]
        missing = [column for column in required if column not in data.columns]
        if missing:
            raise ValueError(f"Missing stock data columns: {missing}")
        if data.empty:
            return 0

        rows = data[required].copy()
        rows["Symbol"] = rows["Symbol"].astype(str).str.upper().str.strip()
        rows["Date"] = pd.to_datetime(rows["Date"], errors="raise").dt.strftime("%Y-%m-%d")
        for column in required[2:]:
            rows[column] = pd.to_numeric(rows[column], errors="raise")
        rows = rows.drop_duplicates(subset=["Symbol", "Date"], keep="last")

        sql = """
            INSERT INTO stock_data
                (symbol, date, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(symbol, date) DO UPDATE SET
                open=excluded.open,
                high=excluded.high,
                low=excluded.low,
                close=excluded.close,
                volume=excluded.volume
        """
        values = [tuple(row) for row in rows.itertuples(index=False, name=None)]
        with self.get_connection() as conn:
            conn.executemany(sql, values)
            conn.commit()
        return len(values)

    def get_stock_data(self, symbol: str, limit: int = 100) -> pd.DataFrame:
        """Return the newest OHLCV rows for a symbol in chronological order."""
        limit = max(1, int(limit))
        query = """
            SELECT symbol AS Symbol, date AS Date, open AS Open,
                   high AS High, low AS Low, close AS Close, volume AS Volume
            FROM stock_data
            WHERE symbol = ?
            ORDER BY date DESC
            LIMIT ?
        """
        with self.get_connection() as conn:
            result = pd.read_sql_query(query, conn, params=[symbol.upper(), limit])
        if not result.empty:
            result["Date"] = pd.to_datetime(result["Date"])
            result = result.sort_values("Date").reset_index(drop=True)
        return result

    def get_available_symbols(self) -> List[str]:
        """Return symbols that currently have persisted OHLCV data."""
        query = "SELECT DISTINCT symbol FROM stock_data ORDER BY symbol"
        with self.get_connection() as conn:
            rows = conn.execute(query).fetchall()
        return [row[0] for row in rows]

    def get_predictions(self, symbol: str, limit: int = 5) -> pd.DataFrame:
        """Return the newest predictions for a symbol."""
        limit = max(1, int(limit))
        query = """
            SELECT symbol, prediction_date, predicted_price, created_at
            FROM predictions
            WHERE symbol = ?
            ORDER BY created_at DESC
            LIMIT ?
        """
        with self.get_connection() as conn:
            return pd.read_sql_query(query, conn, params=[symbol.upper(), limit])
    
    @contextmanager
    def get_connection(self):
        """
        Context manager để quản lý connection
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Cho phép truy cập cột bằng tên
        try:
            yield conn
        finally:
            conn.close()
