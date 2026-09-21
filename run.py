#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File chính để chạy ứng dụng dự báo chứng khoán bằng FastAPI
Khởi động server và background scheduler qua lifespan
"""

import asyncio
import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime

import uvicorn

# Thêm thư mục gốc vào Python path để import các module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from config.settings import Config
from data.collector import DataCollector
from models.trainer import ModelTrainer
from utils.logger import setup_logger

# Thiết lập logging
logger = setup_logger(__name__)


async def run_daily_checks() -> None:
    """Kiểm tra định kỳ và chạy task đúng thời điểm."""
    while True:
        now = datetime.now()
        if now.hour == 18 and now.minute == 0:
            await asyncio.to_thread(collect_daily_data)
        if now.weekday() == 6 and now.hour == 2 and now.minute == 0:
            await asyncio.to_thread(retrain_models)
        await asyncio.sleep(60)


def collect_daily_data():
    """
    Thu thập dữ liệu hàng ngày
    """
    try:
        logger.info("Bắt đầu thu thập dữ liệu hàng ngày")
        collector = DataCollector()
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
        symbols = ['VHM', 'VIC', 'FPT', 'VCB', 'BID']

        for symbol in symbols:
            trainer.train_lstm_model(symbol)

        logger.info("Hoàn thành huấn luyện lại mô hình")
    except Exception as e:
        logger.error(f"Lỗi khi huấn luyện mô hình: {str(e)}")


@asynccontextmanager
async def lifespan(app):
    """Quản lý background scheduler ở mức FastAPI lifespan."""
    if Config.ENABLE_SCHEDULER:
        scheduler_task = asyncio.create_task(run_daily_checks())
        logger.info("✅ Background scheduler đã khởi động")
        try:
            yield
        finally:
            scheduler_task.cancel()
            try:
                await scheduler_task
            except asyncio.CancelledError:
                pass
    else:
        yield


def main():
    """
    Hàm main để khởi động ứng dụng
    """
    try:
        logger.info("=" * 50)
        logger.info("🚀 KHỞI ĐỘNG ỨNG DỤNG DỰ BÁO CHỨNG KHOÁN")
        logger.info("=" * 50)

        app = create_app()
        app.router.lifespan_context = lifespan

        if not os.path.exists(Config.DATABASE_PATH):
            logger.warning("Database chưa tồn tại, sẽ tạo mới")

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

        uvicorn.run(app, host=Config.HOST, port=Config.PORT, log_level="info")

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