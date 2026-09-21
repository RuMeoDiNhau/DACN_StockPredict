#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module thu thập dữ liệu chứng khoán từ các nguồn khác nhau
"""

import yfinance as yf
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import time
import random
import os
from typing import List, Dict, Optional

from utils.logger import setup_logger
from utils.helpers import save_json, ensure_directory

logger = setup_logger(__name__)

class DataCollector:
    """
    Lớp thu thập dữ liệu chứng khoán từ nhiều nguồn
    """
    
    def __init__(self):
        """
        Khởi tạo DataCollector
        """
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Thiết lập thư mục lưu dữ liệu
        self.data_dir = "data/raw"
        ensure_directory(self.data_dir)
        
        logger.info("📊 Khởi tạo DataCollector thành công")

    def get_available_symbols(self) -> List[str]:
        """Trả về các mã cổ phiếu Việt Nam được ứng dụng hỗ trợ."""
        return ['VHM', 'FPT', 'VCB', 'HPG', 'VIC', 'VNM', 'TCB', 'MBB']

    def _save_raw_data(self, data: pd.DataFrame, name: str) -> None:
        """Lưu dữ liệu thu thập được dưới dạng CSV."""
        file_path = os.path.join(self.data_dir, f'{name}.csv')
        data.to_csv(file_path, index=False)
    
    def collect_stock_data(self, symbol: str, days: int = 365) -> Optional[pd.DataFrame]:
        """
        Thu thập dữ liệu giá cổ phiếu từ Yahoo Finance
        
        Args:
            symbol (str): Mã cổ phiếu (VD: VHM.VN)
            days (int): Số ngày lấy dữ liệu về trước
        
        Returns:
            pd.DataFrame: Dữ liệu OHLCV hoặc None nếu lỗi
        """
        try:
            logger.info(f"🔍 Thu thập dữ liệu cổ phiếu: {symbol}")
            
            # Thêm hậu tố .VN cho cổ phiếu Việt Nam
            if not symbol.endswith('.VN'):
                symbol_yahoo = f"{symbol}.VN"
            else:
                symbol_yahoo = symbol
            
            # Tính toán khoảng thời gian
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Lấy dữ liệu từ Yahoo Finance
            ticker = yf.Ticker(symbol_yahoo)
            df = ticker.history(start=start_date, end=end_date)
            
            if df.empty:
                logger.warning(f"⚠️ Không có dữ liệu cho {symbol}")
                return None
            
            # Làm sạch và chuẩn hóa dữ liệu
            df = df.reset_index()
            df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']
            
            # Chỉ giữ các cột cần thiết
            df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']].copy()
            
            # Thêm cột Symbol
            df['Symbol'] = symbol.replace('.VN', '')
            
            # Lưu dữ liệu thô
            self._save_raw_data(df, f"stock_{symbol}_{datetime.now().strftime('%Y%m%d')}")
            
            logger.info(f"✅ Thu thập được {len(df)} ngày dữ liệu cho {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"❌ Lỗi thu thập dữ liệu {symbol}: {str(e)}")
            return None