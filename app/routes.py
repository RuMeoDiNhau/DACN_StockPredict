#!/usr/bin/env python3
"""FastAPI routes for the StockPredict web MVP."""

import re
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from utils.logger import setup_logger

logger = setup_logger(__name__)
main_bp = APIRouter()
api_bp = APIRouter()
db = None

STOCK_DATA_COLUMNS = ["Date", "Open", "High", "Low", "Close", "Volume", "Symbol"]


def _database(request: Request):
    configured_db = getattr(request.app.state, "db", None)
    if configured_db is not None:
        return configured_db
    if db is None:
        raise RuntimeError("Database is not configured")
    return db


def _normalize_symbol(symbol: str) -> str:
    normalized = symbol.strip().upper()
    if not re.fullmatch(r"[A-Z0-9]{2,10}", normalized):
        raise HTTPException(status_code=422, detail={
            "success": False,
            "error": "Invalid stock symbol",
        })
    return normalized


def serialize_stock_data(stock_data):
    """Serialize rows using the public OHLCV schema."""
    if stock_data is None or stock_data.empty:
        return []
    records = stock_data[STOCK_DATA_COLUMNS].to_dict("records")
    for record in records:
        date = record["Date"]
        if hasattr(date, "isoformat"):
            record["Date"] = date.isoformat()
    return records


def get_market_status():
    """Return weekday VN trading-session status in Ho Chi Minh time."""
    now = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))
    is_weekday = now.weekday() < 5
    morning = (9, 0) <= (now.hour, now.minute) < (11, 30)
    afternoon = (13, 0) <= (now.hour, now.minute) < (15, 0)
    is_open = is_weekday and (morning or afternoon)
    return {
        "success": True,
        "status": "open" if is_open else "closed",
        "is_open": is_open,
        "as_of": now.isoformat(),
        "timezone": "Asia/Ho_Chi_Minh",
    }


@main_bp.get("/", response_class=HTMLResponse, name="main.index")
async def index(request: Request):
    try:
        database = _database(request)
        return request.app.state.templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "symbols": database.get_available_symbols()[:10],
                "market_status": get_market_status(),
            },
        )
    except Exception as exc:
        logger.error("Home page error: %s", exc)
        return request.app.state.templates.TemplateResponse(
            "error.html", {"request": request, "error": str(exc)}, status_code=500
        )


@main_bp.get("/symbol/{symbol}", response_class=HTMLResponse, name="main.symbol_detail")
async def symbol_detail(request: Request, symbol: str):
    normalized_symbol = _normalize_symbol(symbol)
    database = _database(request)
    stock_data = database.get_stock_data(normalized_symbol, limit=100)
    templates = request.app.state.templates
    if stock_data is None or stock_data.empty:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": f"No stock data found for {normalized_symbol}"},
            status_code=404,
        )
    predictions = database.get_predictions(normalized_symbol, limit=5)
    return templates.TemplateResponse(
        "symbol_detail.html",
        {
            "request": request,
            "symbol": normalized_symbol,
            "stock_data": serialize_stock_data(stock_data),
            "predictions": predictions.to_dict("records") if predictions is not None else [],
        },
    )


@main_bp.get("/analysis", response_class=HTMLResponse, name="main.analysis")
async def analysis(request: Request):
    return request.app.state.templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "symbols": _database(request).get_available_symbols()[:10],
            "market_status": get_market_status(),
        },
    )


@main_bp.get("/data-management", name="main.data_management")
async def data_management():
    return RedirectResponse(url="/", status_code=302)


@main_bp.get("/models", name="main.models")
async def models():
    return RedirectResponse(url="/", status_code=302)


@api_bp.get("/symbols", name="api.symbols")
async def api_symbols(request: Request):
    return JSONResponse({"success": True, "symbols": _database(request).get_available_symbols()})


@api_bp.get("/stocks/{symbol}", name="api.stock_data")
async def api_stock_data(
    request: Request,
    symbol: str,
    limit: int = Query(default=30, ge=1, le=90),
):
    normalized_symbol = _normalize_symbol(symbol)
    stock_data = _database(request).get_stock_data(normalized_symbol, limit=limit)
    if stock_data is None or stock_data.empty:
        return JSONResponse(
            status_code=404,
            content={"success": False, "symbol": normalized_symbol, "error": "No stock data found"},
        )
    return JSONResponse({
        "success": True,
        "symbol": normalized_symbol,
        "data": serialize_stock_data(stock_data),
    })


@api_bp.get("/market-status", name="api.market_status")
async def api_market_status():
    return JSONResponse(get_market_status())
