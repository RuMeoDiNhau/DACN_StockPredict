#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Routes cho Flask web application
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
import json
from datetime import datetime, timedelta

from data.collector import DataCollector
from data.database import DatabaseManager
from models.trainer import ModelTrainer
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Tạo blueprints
main_bp = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__)

# Khởi tạo các components
db = DatabaseManager()
collector = DataCollector()
trainer = ModelTrainer()

@main_bp.route('/')
def index():
    """
    Trang chủ - Dashboard chính
    """
    try:
        # Lấy danh sách mã cổ phiếu phổ biến
        popular_symbols = collector.get_available_symbols()[:10]
        
        # Lấy thông tin thị trường
        market_status = get_market_status()
        
        return render_template('index.html', 
                             symbols=popular_symbols,
                             market_status=market_status)
    except Exception as e:
        logger.error(f"❌ Lỗi trang chủ: {str(e)}")
        return render_template('error.html', error=str(e))

@main_bp.route('/symbol/<symbol>')
def symbol_detail(symbol):
    """
    Trang chi tiết mã cổ phiếu
    """
    try:
        # Lấy dữ liệu cổ phiếu
        stock_data = db.get_stock_data(symbol, limit=100)
        
        if stock_data is None:
            return render_template('error.html', 
                                 error=f"Không tìm thấy dữ liệu cho {symbol}")
        
        # Lấy dự báo gần nhất
        predictions = db.get_predictions(symbol, limit=5)
        
        return render_template('symbol_detail.html',
                             symbol=symbol,
                             stock_data=stock_data.to_dict('records'),
                             predictions=predictions.to_dict('records') if predictions is not None else [])
    
    except Exception as e:
        logger.error(f"❌ Lỗi chi tiết symbol {symbol}: {str(e)}")
        return render_template('error.html', error=str(e))