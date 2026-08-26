#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module huấn luyện các mô hình Machine Learning
"""

import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
import joblib
import os
from typing import Dict, Tuple, Optional

from utils.logger import setup_logger
from utils.helpers import ensure_directory, save_model
from data.processor import DataProcessor
from config.settings import Config

logger = setup_logger(__name__)

class ModelTrainer:
    """
    Lớp huấn luyện mô hình dự báo chứng khoán
    """
    
    def __init__(self):
        """
        Khởi tạo ModelTrainer
        """
        self.processor = DataProcessor()
        self.models_dir = "models/trained"
        ensure_directory(self.models_dir)
        
        # Lấy cấu hình LSTM từ settings
        self.lstm_config = Config.LSTM_CONFIG
        
        logger.info("🧠 Khởi tạo ModelTrainer thành công")
    
    def create_lstm_model(self, sequence_length: int, features: int = 1) -> Sequential:
        """
        Tạo mô hình LSTM
        
        Args:
            sequence_length: Độ dài sequence input
            features: Số lượng features
        
        Returns:
            Sequential model
        """
        try:
            logger.info(f"🏗️ Tạo mô hình LSTM: seq_len={sequence_length}, features={features}")
            
            model = Sequential()
            
            # Layer đầu vào
            model.add(Input(shape=(sequence_length, features)))
            
            # LSTM layers
            model.add(LSTM(
                units=self.lstm_config['hidden_units'],
                return_sequences=True,
                dropout=self.lstm_config['dropout_rate'],
                recurrent_dropout=self.lstm_config['dropout_rate']
            ))
            
            model.add(LSTM(
                units=self.lstm_config['hidden_units']//2,
                dropout=self.lstm_config['dropout_rate']
            ))
            
            # Dense layers
            model.add(Dense(25, activation='relu'))
            model.add(Dropout(0.1))
            model.add(Dense(1))  # Output layer cho regression
            
            # Compile model
            model.compile(
                optimizer=Adam(learning_rate=0.001),
                loss='mean_squared_error',
                metrics=['mae']
            )
            
            logger.info("✅ Tạo mô hình LSTM thành công")
            return model
            
        except Exception as e:
            logger.error(f"❌ Lỗi tạo mô hình LSTM: {str(e)}")
            return None