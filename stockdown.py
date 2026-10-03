"""Tải dữ liệu giá mẫu bằng vnstock."""

import os

from vnstock import Quote


TICKERS = ["VHM", "FPT"]


for symbol in TICKERS:
    print(f"Đang tải dữ liệu cho {symbol}")
    data = Quote(symbol=symbol, source="VCI").history(
        start="2017-01-01",
        end="2017-04-30",
        interval="1D",
    )
    output_path = f"stock_data_{symbol}.csv"
    data.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"Đã lưu dữ liệu vào {os.path.abspath(output_path)}")
