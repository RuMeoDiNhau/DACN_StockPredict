#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module xử lý và làm sạch dữ liệu chứng khoán
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from typing import Tuple, Optional, List, Dict
from datetime import datetime

from utils.logger import setup_logger

logger = setup_logger(__name__)

class DataProcessor:
    """
    Lớp xử lý dữ liệu chứng khoán cho machine learning
    """
    
    def __init__(self):
        """
        Khởi tạo DataProcessor
        """
        self.scalers = {}  # Lưu trữ các scaler đã fit
        self.feature_columns = []
        logger.info("⚙️ Khởi tạo DataProcessor thành công")
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Làm sạch dữ liệu cơ bản
        
        Args:
            df: DataFrame chứa dữ liệu thô
        
        Returns:
            DataFrame đã được làm sạch
        """
        try:
            logger.info("🧹 Bắt đầu làm sạch dữ liệu")
            
            # Copy để không thay đổi dữ liệu gốc
            df_clean = df.copy()
            
            # Sắp xếp theo ngày
            if 'Date' in df_clean.columns:
                df_clean['Date'] = pd.to_datetime(df_clean['Date'])
                df_clean = df_clean.sort_values('Date').reset_index(drop=True)
            
            # Xử lý missing values
            numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            for col in numeric_columns:
                if col in df_clean.columns:
                    # Fill missing values bằng forward fill, sau đó backward fill
                    df_clean[col] = df_clean[col].fillna(method='ffill').fillna(method='bfill')
            
            # Xóa outliers cực đoan (giá âm hoặc volume âm)
            for col in ['Open', 'High', 'Low', 'Close']:
                if col in df_clean.columns:
                    df_clean = df_clean[df_clean[col] > 0]
            
            if 'Volume' in df_clean.columns:
                df_clean = df_clean[df_clean['Volume'] >= 0]
            
            # Kiểm tra logic giá (High >= Low, etc.)
            if all(col in df_clean.columns for col in ['High', 'Low', 'Open', 'Close']):
                # High phải >= Low
                valid_price = df_clean['High'] >= df_clean['Low']
                df_clean = df_clean[valid_price]
            
            logger.info(f"✅ Làm sạch hoàn thành. Còn lại {len(df_clean)} dòng dữ liệu")
            return df_clean
            
        except Exception as e:
            logger.error(f"❌ Lỗi làm sạch dữ liệu: {str(e)}")
            return df