#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Routes cho FastAPI web application
"""

from datetime import datetime

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from data.collector import DataCollector
from data.database import DatabaseManager
from models.trainer import ModelTrainer
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Tạo routers
main_bp = APIRouter()
api_bp = APIRouter()

# Khởi tạo các components
db = DatabaseManager()
collector = DataCollector()
trainer = ModelTrainer()


@main_bp.get("/", response_class=HTMLResponse, name="main.index")
async def index(request: Request):
    """
    Trang chủ - Dashboard chính
    """
    try:
        popular_symbols = collector.get_available_symbols()[:10]
        market_status = get_market_status()

        templates = request.app.state.templates
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "symbols": popular_symbols, "market_status": market_status},
        )
    except Exception as e:
        logger.error(f"❌ Lỗi trang chủ: {str(e)}")
        templates = request.app.state.templates
        return templates.TemplateResponse("error.html", {"request": request, "error": str(e)})


@main_bp.get("/symbol/{symbol}", response_class=HTMLResponse, name="main.symbol_detail")
async def symbol_detail(request: Request, symbol: str):
    """
    Trang chi tiết mã cổ phiếu
    """
    try:
        stock_data = db.get_stock_data(symbol, limit=100)

        if stock_data is None:
            templates = request.app.state.templates
            return templates.TemplateResponse(
                "error.html",
                {"request": request, "error": f"Không tìm thấy dữ liệu cho {symbol}"},
            )

        predictions = db.get_predictions(symbol, limit=5)
        templates = request.app.state.templates

        return templates.TemplateResponse(
            "symbol_detail.html",
            {
                "request": request,
                "symbol": symbol,
                "stock_data": stock_data.to_dict("records"),
                "predictions": predictions.to_dict("records") if predictions is not None else [],
            },
        )

    except Exception as e:
        logger.error(f"❌ Lỗi chi tiết symbol {symbol}: {str(e)}")
        templates = request.app.state.templates
        return templates.TemplateResponse("error.html", {"request": request, "error": str(e)})


@main_bp.get("/analysis", response_class=HTMLResponse, name="main.analysis")
async def analysis(request: Request):
    """Trang phân tích AI."""
    templates = request.app.state.templates
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "symbols": collector.get_available_symbols()[:10],
            "market_status": get_market_status(),
        },
    )


@main_bp.get("/data-management", name="main.data_management")
async def data_management():
    """Trang quản lý dữ liệu."""
    return RedirectResponse(url="/", status_code=302)


@main_bp.get("/models", name="main.models")
async def models():
    """Trang quản lý mô hình."""
    return RedirectResponse(url="/", status_code=302)


@api_bp.get("/symbols", name="api.symbols")
async def api_symbols():
    """API trả về danh sách mã cổ phiếu hỗ trợ."""
    return JSONResponse({"success": True, "symbols": collector.get_available_symbols()})


def get_market_status():
    """Trả về trạng thái giao dịch hiện tại."""
    now = datetime.now()
    is_weekday = now.weekday() < 5
    is_open = is_weekday and 9 <= now.hour < 15
    return {"is_open": is_open, "status": "open" if is_open else "closed"}