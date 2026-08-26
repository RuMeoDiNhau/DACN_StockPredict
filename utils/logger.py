#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module logging cho ứng dụng
Cung cấp hệ thống log với rotation và formatting
"""

import logging
import logging.handlers
import os
from datetime import datetime

def setup_logger(name, log_file=None, level=logging.INFO):
    """
    Thiết lập logger với file rotation và console output
    
    Args:
        name (str): Tên logger
        log_file (str): Đường dẫn file log (optional)
        level: Mức độ log (DEBUG, INFO, WARNING, ERROR)
    
    Returns:
        logging.Logger: Logger đã được cấu hình
    """
    
    # Tạo logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Tránh tạo handler trùng lặp
    if logger.handlers:
        return logger
    
    # Định dạng log
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler - hiển thị log ra màn hình
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler - ghi log vào file với rotation
    if log_file:
        # Tạo thư mục logs nếu chưa có
        log_dir = os.path.dirname(log_file)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        # Rotating file handler - tự động rotate khi file quá lớn
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,          # Giữ lại 5 file backup
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def log_function_call(func):
    """
    Decorator để log khi function được gọi
    
    Usage:
        @log_function_call
        def my_function():
            pass
    """
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        logger.info(f"🚀 Gọi function: {func.__name__}")
        
        try:
            result = func(*args, **kwargs)
            logger.info(f"✅ Hoàn thành: {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"❌ Lỗi trong {func.__name__}: {str(e)}")
            raise
    
    return wrapper

def log_execution_time(func):
    """
    Decorator để đo thời gian thực thi function
    """
    import time
    
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"⏱️ {func.__name__} thực thi trong {execution_time:.2f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"❌ {func.__name__} lỗi sau {execution_time:.2f}s: {str(e)}")
            raise
    
    return wrapper

class StockPredictionLogger:
    """
    Logger chuyên dụng cho ứng dụng dự báo chứng khoán
    """
    
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Các logger cho từng module
        self.app_logger = setup_logger(
            'app',
            os.path.join(log_dir, 'app.log'),
            logging.INFO
        )
        
        self.data_logger = setup_logger(
            'data',
            os.path.join(log_dir, 'data_collection.log'),
            logging.INFO
        )
        
        self.model_logger = setup_logger(
            'model',
            os.path.join(log_dir, 'model_training.log'),
            logging.INFO
        )
        
        self.prediction_logger = setup_logger(
            'prediction',
            os.path.join(log_dir, 'predictions.log'),
            logging.INFO
        )
    
    def log_data_collection(self, symbol, status, message=""):
        """Log quá trình thu thập dữ liệu"""
        self.data_logger.info(f"📊 {symbol} - {status}: {message}")
    
    def log_model_training(self, symbol, epoch, loss, val_loss):
        """Log quá trình huấn luyện mô hình"""
        self.model_logger.info(
            f"🧠 {symbol} - Epoch {epoch}: Loss={loss:.4f}, Val_Loss={val_loss:.4f}"
        )
    
    def log_prediction(self, symbol, predicted_price, confidence, actual_price=None):
        """Log kết quả dự báo"""
        if actual_price:
            accuracy = abs(predicted_price - actual_price) / actual_price * 100
            self.prediction_logger.info(
                f"🎯 {symbol} - Dự báo: {predicted_price:.2f}, "
                f"Thực tế: {actual_price:.2f}, "
                f"Độ chính xác: {100-accuracy:.1f}%, "
                f"Confidence: {confidence:.2f}"
            )
        else:
            self.prediction_logger.info(
                f"🔮 {symbol} - Dự báo: {predicted_price:.2f}, "
                f"Confidence: {confidence:.2f}"
            )
    
    def log_error(self, module, error_msg, exception=None):
        """Log lỗi hệ thống"""
        logger = getattr(self, f"{module}_logger", self.app_logger)
        if exception:
            logger.error(f"❌ {error_msg}: {str(exception)}", exc_info=True)
        else:
            logger.error(f"❌ {error_msg}")

# Khởi tạo logger global cho toàn bộ ứng dụng
main_logger = StockPredictionLogger()