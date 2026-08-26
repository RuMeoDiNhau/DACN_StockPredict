#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script tự động cài đặt và thiết lập môi trường cho Stock AI Predictor
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_header():
    """In header cho script"""
    print("=" * 60)
    print("🚀 STOCK AI PREDICTOR - AUTO INSTALLER")
    print("=" * 60)
    print("Đồ án chuyên ngành - Đại học Bách Khoa TP.HCM")
    print("Ứng dụng AI Agent Và LLM Vào Dự Báo Giá Chứng Khoán")
    print("=" * 60)

def check_python_version():
    """Kiểm tra phiên bản Python"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Cần Python 3.8 trở lên!")
        print(f"   Phiên bản hiện tại: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
    return True

def create_virtual_environment():
    """Tạo virtual environment"""
    print("\n📦 Tạo virtual environment...")
    
    try:
        # Kiểm tra xem venv đã tồn tại chưa
        if os.path.exists("venv"):
            print("   Virtual environment đã tồn tại")
            return True
        
        # Tạo venv
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Tạo virtual environment thành công")
        return True
        
    except subprocess.CalledProcessError:
        print("❌ Lỗi tạo virtual environment")
        return False

def install_requirements():
    """Cài đặt requirements"""
    print("\n📚 Cài đặt thư viện...")
    
    try:
        # Đường dẫn pip trong venv
        if platform.system() == "Windows":
            pip_path = "venv\\Scripts\\pip.exe"
        else:
            pip_path = "venv/bin/pip"
        
        # Upgrade pip
        subprocess.run([pip_path, "install", "--upgrade", "pip"], check=True)
        
        # Install requirements
        subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
        
        print("✅ Cài đặt thư viện thành công")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi cài đặt thư viện: {e}")
        return False