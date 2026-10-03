# Cài đặt và chạy StockPredict Web MVP

## Yêu cầu

- Python có các dependency trong `requirements.txt`.
- SQLite được dùng qua thư viện chuẩn Python; không cần PostgreSQL.
- Internet chỉ cần khi chạy collector vnstock để nạp dữ liệu mới. Dashboard và test endpoint không gọi mạng.

## Chạy server

```powershell
.\.venv\Scripts\Activate.ps1
python run.py
```

Truy cập <http://127.0.0.1:5000> hoặc <http://localhost:5000>.

`run.py` khởi động FastAPI và phục vụ frontend tĩnh. Không tự chạy ML, prediction hoặc crawler tin tức.

## Kiểm tra API

```powershell
Invoke-RestMethod http://127.0.0.1:5000/api/health
Invoke-RestMethod http://127.0.0.1:5000/api/symbols
Invoke-RestMethod 'http://127.0.0.1:5000/api/stocks/VHM?limit=30'
Invoke-RestMethod http://127.0.0.1:5000/api/market-status
```

`/api/stocks/{symbol}` trả `404` khi SQLite chưa có mã đó, và `422` khi symbol hoặc `limit` sai. Các giá trị OHLCV trả về có schema `Date`, `Open`, `High`, `Low`, `Close`, `Volume`, `Symbol`.

## Kiểm thử offline

```powershell
python -m pytest -q
git diff --check
```

Tests tạo SQLite tạm thời và không sửa database production.

## Dữ liệu trống

Khi dashboard báo SQLite chưa có dữ liệu, chạy quy trình collector riêng để nạp OHLCV. Không có dữ liệu giả được hiển thị. Sau khi dữ liệu được lưu, tải lại dashboard để chọn mã và xem biểu đồ/bảng OHLCV.
