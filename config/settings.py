#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File cấu hình chính cho ứng dụng
Chứa tất cả các thiết lập hệ thống, database, API keys
"""

import os
from datetime import timedelta

class Config:
    """
    Lớp cấu hình chính cho ứng dụng
    """
    
    # ==================== CẤU HÌNH CƠ BẢN ====================
    # Thư mục gốc của project
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Cấu hình Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-for-stock-prediction-2024'
    DEBUG = True  # Đổi thành False khi deploy production
    
    # Cấu hình server
    HOST = '127.0.0.1'  # localhost
    PORT = 5000
    
    # ==================== CẤU HÌNH DATABASE ====================
    # Đường dẫn database SQLite
    DATABASE_PATH = os.path.join(BASE_DIR, 'data', 'stock_prediction.db')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Cấu hình backup database
    BACKUP_INTERVAL = 24  # hours
    MAX_BACKUPS = 7  # giữ lại 7 backup gần nhất
    
    # ==================== CẤU HÌNH AI VÀ ML ====================
    # Cấu hình mô hình LSTM
    LSTM_CONFIG = {
        'sequence_length': 60,  # Sử dụng 60 ngày dữ liệu để dự báo
        'hidden_units': 50,     # Số neurons trong LSTM layer
        'dropout_rate': 0.2,    # Tỷ lệ dropout để tránh overfitting
        'epochs': 50,           # Số epoch huấn luyện
        'batch_size': 32,       # Batch size
        'validation_split': 0.2 # Tỷ lệ validation set
    }
    
    # Cấu hình AI Agent
    ENABLE_AI_AGENT = True
    AI_AGENT_CONFIG = {
        'sentiment_threshold': 0.6,  # Ngưỡng sentiment để tạo signal
        'news_sources': [
            'cafef.vn',
            'vneconomy.vn', 
            'tinnhanhchungkhoan.vn'
        ],
        'update_frequency': 3600  # Cập nhật mỗi 1 giờ (giây)
    }
    
    # ==================== CẤU HÌNH LLM ====================
    # OpenAI API (cần đăng ký và lấy API key)
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY') or 'your-openai-api-key-here'
    OPENAI_MODEL = 'gpt-3.5-turbo'  # Hoặc 'gpt-4' nếu có access
    
    # ==================== CẤU HÌNH SCHEDULER ====================
    ENABLE_SCHEDULER = True  # Bật/tắt background tasks