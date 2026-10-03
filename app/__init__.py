#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module ứng dụng web FastAPI
"""

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import pass_context

from config.settings import Config
from data.database import DatabaseManager
from utils.logger import setup_logger

logger = setup_logger(__name__)


def create_app(config_class=Config):
    """
    Factory function để tạo FastAPI app

    Args:
        config_class: Class cấu hình

    Returns:
        FastAPI app instance
    """
    app = FastAPI(title="StockPredict", version="1.0.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    base_dir = Path(__file__).resolve().parent.parent
    templates_dir = base_dir / "app" / "templates"
    static_dir = base_dir / "app" / "static"

    templates = Jinja2Templates(directory=str(templates_dir))

    @pass_context
    def template_url_for(context, endpoint: str, **values):
        """Đưa helper url_for tương thích với template cũ từ Flask sang FastAPI."""
        request = context.get("request")
        if endpoint == "static" and "filename" in values:
            values["path"] = values.pop("filename")
        return request.url_for(endpoint, **values)

    def get_flashed_messages(with_categories=False):
        """Giả lập helper Flask để template không bị lỗi khi không dùng flash."""
        return []

    templates.env.globals["url_for"] = template_url_for
    templates.env.globals["get_flashed_messages"] = get_flashed_messages
    app.state.templates = templates
    app.state.db = DatabaseManager(db_path=config_class.DATABASE_PATH)
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    from app.routes import main_bp, api_bp

    app.include_router(main_bp)
    app.include_router(api_bp, prefix="/api")

    os.makedirs(static_dir / "css", exist_ok=True)
    os.makedirs(static_dir / "js", exist_ok=True)
    os.makedirs(static_dir / "images", exist_ok=True)
    os.makedirs(templates_dir, exist_ok=True)

    logger.info("🌐 FastAPI app đã được khởi tạo")
    return app
