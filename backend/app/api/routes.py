"""REST API routes for the StockPredict MVP."""

from fastapi import APIRouter, HTTPException, Query, Request

from backend.app.schemas import HealthResponse, MarketStatusResponse, StocksResponse, SymbolsResponse
from backend.app.services import get_market_status, normalize_symbol, serialize_ohlcv

router = APIRouter(prefix="/api", tags=["stocks"])


def _database(request: Request):
    return request.app.state.db


@router.get("/health", response_model=HealthResponse)
async def health():
    return {"success": True, "service": "stockpredict-api"}


@router.get("/symbols", response_model=SymbolsResponse)
async def symbols(request: Request):
    return {"success": True, "symbols": _database(request).get_available_symbols()}


@router.get("/stocks/{symbol}", response_model=StocksResponse)
async def stocks(request: Request, symbol: str, limit: int = Query(30, ge=1, le=90)):
    normalized_symbol = normalize_symbol(symbol)
    rows = _database(request).get_stock_data(normalized_symbol, limit=limit)
    if rows is None or rows.empty:
        raise HTTPException(status_code=404, detail=f"No stock data found for {normalized_symbol}")
    return {"success": True, "symbol": normalized_symbol, "data": serialize_ohlcv(rows)}


@router.get("/market-status", response_model=MarketStatusResponse)
async def market_status():
    return get_market_status()
