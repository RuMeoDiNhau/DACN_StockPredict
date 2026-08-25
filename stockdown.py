import yfinance as yf

TICKERS = ["SPY", "AAPL"]

print(f"Đang tải dữ liệu và group theo ticker")
data = yf.download(TICKERS, start="2017-01-01", end="2017-04-30",
                       group_by="ticker")

print(f"Đang chuyển dữ liệu thành file .csv...")
data.to_csv("stock_data.csv")

print(f"Đã lưu dữ liệu vào file stock_data.csv")