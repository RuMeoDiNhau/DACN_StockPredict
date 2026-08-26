#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module ứng dụng web Flask
"""

from flask import Flask
from flask_cors import CORS
import os

from config.settings import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)

def create_app(config_class=Config):
    """
    Factory function để tạo Flask app
    
    Args:
        config_class: Class cấu hình
    
    Returns:
        Flask app instance
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Thiết lập CORS để frontend có thể gọi API
    CORS(app)
    
    # Import và đăng ký blueprints
    from app.routes import main_bp, api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Tạo thư mục cần thiết
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('static/images', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    logger.info("🌐 Flask app đã được khởi tạo")
    
    return app