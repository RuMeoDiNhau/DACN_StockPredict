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
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
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
            ''')
            conn.commit()
    
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