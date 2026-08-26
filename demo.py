#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo script để test các chức năng của Stock AI Predictor
"""

import sys
import os
import time
from datetime import datetime

# Thêm project root vào Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_demo_header():
    """In header cho demo"""
    print("\n" + "=" * 60)
    print("🎮 STOCK AI PREDICTOR - DEMO")
    print("=" * 60)
    print("Đồ án chuyên ngành - Đại học Bách Khoa TP.HCM")
    print("Tác giả: [Tên sinh viên]")
    print("MSSV: [Mã số sinh viên]")
    print("=" * 60)

def test_basic_imports():
    """Test import các module cơ bản"""
    print("\n📦 TEST 1: IMPORT MODULES")
    print("-" * 40)
    
    try:
        from data.collector import DataCollector
        from data.processor import DataProcessor  
        from data.database import DatabaseManager
        from models.ai_agent import AIAgent
        from app import create_app
        from utils.logger import setup_logger
        
        print("✅ Import tất cả modules thành công")
        return True
        
    except ImportError as e:
        print(f"❌ Lỗi import: {str(e)}")
        return False

def test_data_collection():
    """Test thu thập dữ liệu"""
    print("\n🔍 TEST 2: THU THẬP DỮ LIỆU")
    print("-" * 40)
    
    try:
        from data.collector import DataCollector
        
        collector = DataCollector()
        
        # Test lấy danh sách symbols
        symbols = collector.get_available_symbols()
        print(f"✅ Lấy được {len(symbols)} mã cổ phiếu")
        print(f"   Top 5: {symbols[:5]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi test thu thập dữ liệu: {str(e)}")
        return False

def test_web_app():
    """Test Flask web app"""
    print("\n🌐 TEST 3: WEB APPLICATION")
    print("-" * 40)
    
    try:
        from app import create_app
        
        app = create_app()
        
        with app.test_client() as client:
            # Test trang chủ
            response = client.get('/')
            if response.status_code == 200:
                print("✅ Trang chủ hoạt động")
            
            # Test API
            response = client.get('/api/symbols')
            if response.status_code == 200:
                data = response.get_json()
                if data and data.get('success'):
                    print(f"✅ API symbols: {len(data.get('symbols', []))} mã")
                else:
                    print("⚠️ API symbols trả về dữ liệu trống")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi test web app: {str(e)}")
        return False

def run_demo():
    """Chạy toàn bộ demo"""
    print_demo_header()
    
    tests = [
        ("Import modules", test_basic_imports),
        ("Thu thập dữ liệu", test_data_collection),
        ("Web Application", test_web_app)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🚀 Chạy test: {test_name}")
        start_time = time.time()
        
        try:
            success = test_func()
            duration = time.time() - start_time
            results.append((test_name, success, duration))
            
            if success:
                print(f"✅ {test_name} THÀNH CÔNG ({duration:.2f}s)")
            else:
                print(f"❌ {test_name} THẤT BẠI ({duration:.2f}s)")
                
        except Exception as e:
            duration = time.time() - start_time
            results.append((test_name, False, duration))
            print(f"💥 {test_name} LỖI: {str(e)} ({duration:.2f}s)")
        
        time.sleep(0.5)  # Nghỉ 0.5 giây giữa các test
    
    # Tổng kết
    print("\n" + "=" * 60)
    print("📊 KẾT QUẢ DEMO")
    print("=" * 60)
    
    successful = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    for test_name, success, duration in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name:<20} ({duration:.2f}s)")
    
    print("-" * 60)
    print(f"Tổng kết: {successful}/{total} tests thành công ({successful/total*100:.1f}%)")
    
    if successful == total:
        print("\n🎉 TẤT CẢ TESTS ĐỀU THÀNH CÔNG!")
        print("✅ Hệ thống sẵn sàng để sử dụng")
    else:
        print(f"\n⚠️ CÓ {total-successful} TESTS THẤT BẠI")
        print("🔧 Vui lòng kiểm tra lại cấu hình")
    
    print("\n💡 Để chạy ứng dụng web:")
    print("   python run.py")
    print("   Truy cập: http://localhost:5000")
    
    return successful == total

if __name__ == "__main__":
    try:
        success = run_demo()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏸️ Demo bị ngắt bởi người dùng")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Lỗi không mong muốn: {str(e)}")
        sys.exit(1)