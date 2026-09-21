#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Các hàm tiện ích hỗ trợ cho ứng dụng
"""

import os
import json
import pickle
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import requests
import re
from typing import List, Dict, Any, Optional


def validate_stock_symbol(symbol: str) -> bool:
    """Kiểm tra mã cổ phiếu gồm 3 đến 5 chữ cái."""
    return isinstance(symbol, str) and bool(re.fullmatch(r'[A-Za-z]{3,5}', symbol.strip()))


def format_currency(amount: float, currency: str = 'VND') -> str:
    """Định dạng số tiền theo loại tiền được yêu cầu."""
    if currency == 'VND':
        return f'{amount:,.0f} ₫'
    return f'{amount:,.2f} {currency}'


def save_model(model: Any, file_path: str) -> bool:
    """Lưu mô hình Keras hoặc mô hình hỗ trợ giao diện ``save``."""
    try:
        ensure_directory(os.path.dirname(file_path))
        model.save(file_path)
        return True
    except Exception as e:
        print(f"❌ Lỗi lưu model: {str(e)}")
        return False

def ensure_directory(path: str) -> None:
    """
    Tạo thư mục nếu chưa tồn tại
    
    Args:
        path (str): Đường dẫn thư mục
    """
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"✅ Đã tạo thư mục: {path}")

def save_json(data: Dict[str, Any], file_path: str) -> bool:
    """
    Lưu dữ liệu dạng JSON
    
    Args:
        data: Dữ liệu cần lưu
        file_path: Đường dẫn file
    
    Returns:
        bool: True nếu thành công
    """
    try:
        ensure_directory(os.path.dirname(file_path))
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"❌ Lỗi lưu JSON: {str(e)}")
        return False

def load_json(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Đọc dữ liệu JSON
    
    Args:
        file_path: Đường dẫn file
    
    Returns:
        Dict hoặc None nếu lỗi
    """
    try:
        if not os.path.exists(file_path):
            return None
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Lỗi đọc JSON: {str(e)}")
        return None