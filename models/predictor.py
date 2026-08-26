#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module dự báo giá cổ phiếu sử dụng các mô hình đã được huấn luyện
"""

import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
import joblib
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

from utils.logger import setup_logger
from data.processor import DataProcessor
from data.database import DatabaseManager
from config.settings import Config

logger = setup_logger(__name__)

class StockPredictor:
    """
    Lớp dự báo giá cổ phiếu
    """
    
    def __init__(self):
        """
        Khởi tạo StockPredictor
        """
        self.processor = DataProcessor()
        self.db = DatabaseManager()
        self.models_dir = "models/trained"
        self.loaded_models = {}  # Cache cho các mô hình đã load
        self.loaded_scalers = {}  # Cache cho các scaler đã load
        
        logger.info("🔮 Khởi tạo StockPredictor thành công")
    
    def load_model_and_scaler(self, symbol: str) -> Tuple[object, object]:
        """
        Load mô hình và scaler cho symbol
        
        Args:
            symbol: Mã cổ phiếu
        
        Returns:
            Tuple (model, scaler) hoặc (None, None) nếu lỗi
        """
        try:
            # Kiểm tra cache trước
            if symbol in self.loaded_models and symbol in self.loaded_scalers:
                return self.loaded_models[symbol], self.loaded_scalers[symbol]
            
            # Đường dẫn file
            model_path = os.path.join(self.models_dir, f"lstm_{symbol}.h5")
            scaler_path = os.path.join(self.models_dir, f"scaler_{symbol}.pkl")
            
            # Kiểm tra file tồn tại
            if not os.path.exists(model_path) or not os.path.exists(scaler_path):
                logger.warning(f"⚠️ Không tìm thấy mô hình cho {symbol}")
                return None, None
            
            # Load model
            model = load_model(model_path)
            
            # Load scaler
            scaler = joblib.load(scaler_path)
            
            # Cache lại
            self.loaded_models[symbol] = model
            self.loaded_scalers[symbol] = scaler
            
            logger.info(f"✅ Load mô hình {symbol} thành công")
            return model, scaler
            
        except Exception as e:
            logger.error(f"❌ Lỗi load mô hình {symbol}: {str(e)}")
            return None, None