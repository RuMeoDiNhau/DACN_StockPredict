#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cleaning and feature preparation for stock time-series data."""

from typing import Dict

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from utils.logger import setup_logger

logger = setup_logger(__name__)


class DataProcessor:
    """Prepare stable, leakage-safe input data for the ML pipeline."""

    PRICE_COLUMNS = ["Open", "High", "Low", "Close", "Volume"]

    def __init__(self):
        self.scalers: Dict[str, MinMaxScaler] = {}
        self.feature_columns = []
        logger.info("DataProcessor initialized")

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate OHLCV data without mutating the input frame."""
        if df is None or df.empty:
            return pd.DataFrame(columns=list(df.columns) if df is not None else [])

        cleaned = df.copy()
        if "Date" not in cleaned.columns:
            raise ValueError("Stock data must contain a Date column")

        cleaned["Date"] = pd.to_datetime(cleaned["Date"], errors="coerce")
        cleaned = cleaned.dropna(subset=["Date"])
        cleaned = cleaned.sort_values("Date")
        cleaned = cleaned.drop_duplicates(subset=["Date"], keep="last")

        present = [column for column in self.PRICE_COLUMNS if column in cleaned]
        if not present:
            raise ValueError("Stock data has no OHLCV columns")

        for column in present:
            cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")
            if cleaned[column].notna().sum() == 0:
                raise ValueError(f"Column {column} contains no numeric values")
            cleaned[column] = cleaned[column].interpolate(limit_direction="both")

        price_columns = [
            column for column in ["Open", "High", "Low", "Close"]
            if column in cleaned
        ]
        if price_columns:
            cleaned = cleaned[(cleaned[price_columns] > 0).all(axis=1)]
        if "Volume" in cleaned:
            cleaned = cleaned[cleaned["Volume"] >= 0]
        if {"High", "Low"}.issubset(cleaned):
            cleaned = cleaned[cleaned["High"] >= cleaned["Low"]]
        if {"Open", "High", "Low", "Close"}.issubset(cleaned):
            cleaned = cleaned[
                (cleaned["High"] >= cleaned["Open"])
                & (cleaned["High"] >= cleaned["Close"])
                & (cleaned["Low"] <= cleaned["Open"])
                & (cleaned["Low"] <= cleaned["Close"])
            ]

        cleaned = cleaned.replace([np.inf, -np.inf], np.nan)
        cleaned = cleaned.dropna(subset=present)
        cleaned = cleaned.reset_index(drop=True)
        logger.info("Cleaned %s stock data rows", len(cleaned))
        return cleaned

    def fit_scale(self, df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """Fit a MinMaxScaler on the provided training frame only."""
        cleaned = self.clean_data(df)
        columns = [column for column in self.PRICE_COLUMNS if column in cleaned]
        if not columns:
            raise ValueError("No numeric feature columns available for scaling")
        scaler = MinMaxScaler()
        result = cleaned.copy()
        result[columns] = scaler.fit_transform(result[columns])
        self.scalers[symbol.upper()] = scaler
        self.feature_columns = columns
        return result
