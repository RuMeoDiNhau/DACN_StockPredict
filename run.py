#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File chính để chạy ứng dụng dự báo chứng khoán
Khởi động Flask server và các background tasks
"""

import os
import sys
from datetime import datetime
import threading
import schedule
import time

# Thêm thư mục gốc vào Python path để import các module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from config.settings import Config
from data.collector import DataCollector
from models.trainer import ModelTrainer
from utils.logger import setup_logger

# Thiết lập logging
logger = setup_logger(__name__)

def run_scheduled_tasks():
    """
    Chạy các tác vụ được lên lịch (thu thập dữ liệu, huấn luyện mô hình)
    """
    logger.info("Bắt đầu background scheduler")
    
    # Lên lịch thu thập dữ liệu hàng ngày lúc 18:00
    schedule.every().day.at("18:00").do(collect_daily_data)
    
    # Lên lịch huấn luyện lại mô hình vào Chủ nhật hàng tuần
    schedule.every().sunday.at("02:00").do(retrain_models)
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Kiểm tra mỗi phút

def collect_daily_data():
    """
    Thu thập dữ liệu hàng ngày
    """
    try:
        logger.info("Bắt đầu thu thập dữ liệu hàng ngày")
        collector = DataCollector()
        
        # Danh sách các mã cổ phiếu chính của VN
        symbols = ['VHM', 'VIC', 'FPT', 'VCB', 'BID', 'CTG', 'MSN', 'MWG', 'HPG', 'SAB']
        
        for symbol in symbols:
            collector.collect_stock_data(symbol, days=30)
            collector.collect_news_data(symbol)
            
        logger.info("Hoàn thành thu thập dữ liệu hàng ngày")
        
    except Exception as e:
        logger.error(f"Lỗi khi thu thập dữ liệu: {str(e)}")

def retrain_models():
    """
    Huấn luyện lại các mô hình hàng tuần
    """
    try:
        logger.info("Bắt đầu huấn luyện lại mô hình")
        trainer = ModelTrainer()
        
        # Huấn luyện mô hình cho các mã chính
        symbols = ['VHM', 'VIC', 'FPT', 'VCB', 'BID']
        
        for symbol in symbols:
            trainer.train_lstm_model(symbol)
            
        logger.info("Hoàn thành huấn luyện lại mô hình")
        
    except Exception as e:
        logger.error(f"Lỗi khi huấn luyện mô hình: {str(e)}")

def main():
    """
    Hàm main để khởi động ứng dụng
    """
    try:
        logger.info("=" * 50)
        logger.info("🚀 KHỞI ĐỘNG ỨNG DỤNG DỰ BÁO CHỨNG KHOÁN")
        logger.info("=" * 50)
        
        # Tạo Flask app
        app = create_app()
        
        # Kiểm tra cấu hình
        if not os.path.exists(Config.DATABASE_PATH):
            logger.warning("Database chưa tồn tại, sẽ tạo mới")
            
        # Khởi động background scheduler trong thread riêng
        if Config.ENABLE_SCHEDULER:
            scheduler_thread = threading.Thread(target=run_scheduled_tasks, daemon=True)
            scheduler_thread.start()
            logger.info("✅ Background scheduler đã khởi động")
        
        # Hiển thị thông tin ứng dụng
        print(f"""
🌟 ỨNG DỤNG DỰ BÁO CHỨNG KHOÁN BẰNG AI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🌐 URL: http://localhost:{Config.PORT}
🔧 Mode: {'Development' if Config.DEBUG else 'Production'}
📊 Database: {Config.DATABASE_PATH}
🤖 AI Features: {'Enabled' if Config.ENABLE_AI_AGENT else 'Disabled'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 Hướng dẫn sử dụng:
   1. Mở trình duyệt và truy cập http://localhost:{Config.PORT}
   2. Chọn mã cổ phiếu để phân tích
   3. Xem dự báo và báo cáo AI
   
🛑 Để dừng ứng dụng: Nhấn Ctrl+C
""")
        
        # Chạy Flask server
        app.run(
            host=Config.HOST,
            port=Config.PORT,
            debug=Config.DEBUG,
            threaded=True
        )
        
    except KeyboardInterrupt:
        logger.info("🛑 Người dùng dừng ứng dụng")
        print("\n👋 Cảm ơn bạn đã sử dụng ứng dụng!")
        
    except Exception as e:
        logger.error(f"❌ Lỗi khởi động ứng dụng: {str(e)}")
        print(f"\n❌ Có lỗi xảy ra: {str(e)}")
        print("🔧 Vui lòng kiểm tra log để biết thêm chi tiết")
        
    finally:
        logger.info("🔚 Ứng dụng đã tắt")

if __name__ == '__main__':
    main()