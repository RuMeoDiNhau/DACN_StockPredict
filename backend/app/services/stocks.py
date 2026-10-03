"""Business logic between API routes and SQLite data access."""

import re
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import HTTPException


OHLCV_COLUMNS = ["Date", "Open", "High", "Low", "Close", "Volume", "Symbol"]
MARKET_TIMEZONE = "Asia/Ho_Chi_Minh"


def normalize_symbol(symbol: str) -> str:
    """Normalize a route symbol or raise a client-safe 422 response."""
    normalized = symbol.strip().upper()
    if not re.fullmatch(r"[A-Z0-9]{2,10}", normalized):
        raise HTTPException(status_code=422, detail="Invalid stock symbol")
    return normalized


def serialize_ohlcv(stock_data):
    """Return SQLite rows in the single public OHLCV JSON schema."""
    if stock_data is None or stock_data.empty:
        return []

    records = stock_data[OHLCV_COLUMNS].to_dict("records")
    for row in records:
        date = row["Date"]
        row["Date"] = date.isoformat() if hasattr(date, "isoformat") else str(date)
        for field in ("Open", "High", "Low", "Close", "Volume"):
            row[field] = float(row[field])
        row["Symbol"] = str(row["Symbol"]).upper()
    return records


def get_market_status():
    """Return a documented, local-time market-session indicator."""
    now = datetime.now(ZoneInfo(MARKET_TIMEZONE))
    is_weekday = now.weekday() < 5
    morning = (9, 0) <= (now.hour, now.minute) < (11, 30)
    afternoon = (13, 0) <= (now.hour, now.minute) < (15, 0)
    is_open = is_weekday and (morning or afternoon)
    return {
        "success": True,
        "status": "open" if is_open else "closed",
        "is_open": is_open,
        "as_of": now.isoformat(),
        "timezone": MARKET_TIMEZONE,
    }
