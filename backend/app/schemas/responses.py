"""Public response models for the REST API."""

from typing import List

from pydantic import BaseModel


class HealthResponse(BaseModel):
    success: bool
    service: str


class SymbolsResponse(BaseModel):
    success: bool
    symbols: List[str]


class OhlcvRecord(BaseModel):
    Date: str
    Open: float
    High: float
    Low: float
    Close: float
    Volume: float
    Symbol: str


class StocksResponse(BaseModel):
    success: bool
    symbol: str
    data: List[OhlcvRecord]


class MarketStatusResponse(BaseModel):
    success: bool
    status: str
    is_open: bool
    as_of: str
    timezone: str
