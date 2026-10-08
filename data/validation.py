"""Validation helpers for normalized daily OHLCV data."""

import re

import numpy as np
import pandas as pd


REQUIRED_OHLCV_COLUMNS = ["Symbol", "Date", "Open", "High", "Low", "Close", "Volume"]
SYMBOL_PATTERN = re.compile(r"[A-Z0-9]{2,10}")


def validate_ohlcv(data: pd.DataFrame, symbol: str) -> pd.DataFrame:
    """Validate one complete OHLCV batch and return a defensive copy.

    Validation is deliberately strict: a batch containing a null, duplicate
    date, non-finite/negative value, or impossible OHLC relationship is
    rejected before it can be written to SQLite.
    """
    normalized_symbol = str(symbol).upper().replace(".VN", "").strip()
    if not SYMBOL_PATTERN.fullmatch(normalized_symbol):
        raise ValueError(f"Invalid stock symbol: {normalized_symbol!r}")
    if data is None or data.empty:
        raise ValueError("OHLCV data is empty")

    missing = [column for column in REQUIRED_OHLCV_COLUMNS if column not in data.columns]
    if missing:
        raise ValueError(f"Missing OHLCV columns: {missing}")

    rows = data[REQUIRED_OHLCV_COLUMNS].copy()
    symbols = rows["Symbol"].astype(str).str.upper().str.strip()
    if not symbols.eq(normalized_symbol).all():
        raise ValueError(f"OHLCV rows contain a symbol different from {normalized_symbol}")

    dates = pd.to_datetime(rows["Date"], errors="coerce")
    if dates.isna().any():
        raise ValueError("Date contains null or unparseable values")
    date_keys = dates.dt.strftime("%Y-%m-%d")
    if date_keys.duplicated().any():
        raise ValueError("Date contains duplicate rows")

    numeric_columns = ["Open", "High", "Low", "Close", "Volume"]
    for column in numeric_columns:
        values = pd.to_numeric(rows[column], errors="coerce")
        if values.isna().any():
            raise ValueError(f"{column} contains null or non-numeric values")
        if not np.isfinite(values.to_numpy()).all():
            raise ValueError(f"{column} contains non-finite values")
        if (values < 0).any():
            raise ValueError(f"{column} contains negative values")
        rows[column] = values.astype(float)

    if not ((rows["Low"] <= rows["Open"]) & (rows["Open"] <= rows["High"])).all():
        raise ValueError("OHLC relationship Low <= Open <= High is invalid")
    if not ((rows["Low"] <= rows["Close"]) & (rows["Close"] <= rows["High"])).all():
        raise ValueError("OHLC relationship Low <= Close <= High is invalid")

    rows["Symbol"] = normalized_symbol
    rows["Date"] = dates
    return rows.sort_values("Date").reset_index(drop=True)
