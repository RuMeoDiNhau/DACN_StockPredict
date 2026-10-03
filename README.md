# StockPredict Web MVP

StockPredict MVP hiển thị dữ liệu cổ phiếu OHLCV đã lưu cục bộ.

```text
vnstock → data/collector.py → data/processor.py → SQLite → FastAPI REST API → frontend
```

## Kiến trúc

```text
backend/app/       FastAPI factory, REST routes, services và Pydantic schemas
frontend/          HTML, CSS, JavaScript; chỉ gọi REST API bằng fetch
data/              collector, processor, DatabaseManager/SQLite
run.py             entry point localhost
```

MVP không cung cấp dự báo ML, đăng nhập, tin tức, agent, PostgreSQL hoặc deploy production.

## Chạy cục bộ

```powershell
.\.venv\Scripts\Activate.ps1
python run.py
```

Mở <http://127.0.0.1:5000>. Server dùng SQLite tại `data/stock_prediction.db`. Nếu database chưa có dữ liệu, dashboard hiện hướng dẫn nạp OHLCV thay vì dữ liệu giả.

Xem hướng dẫn cài đặt và kiểm tra chi tiết ở [SETUP.md](SETUP.md).

## API contract

Mọi response thành công có `success: true`; lỗi API có `success: false`, `error` và HTTP status phù hợp.

| Endpoint | Kết quả |
| --- | --- |
| `GET /api/health` | `200`, trạng thái API |
| `GET /api/symbols` | `200`, danh sách mã có dữ liệu trong SQLite |
| `GET /api/stocks/{symbol}?limit=1..90` | `200` OHLCV; `404` nếu không có dữ liệu; `422` nếu symbol/limit sai |
| `GET /api/market-status` | `200`, trạng thái phiên và timezone `Asia/Ho_Chi_Minh` |

Schema OHLCV công khai luôn là: `Date`, `Open`, `High`, `Low`, `Close`, `Volume`, `Symbol`.

`/` phục vụ dashboard. `/symbol/{symbol}` phục vụ trang chi tiết tĩnh, tải dữ liệu qua API nên có thể mở trực tiếp hoặc reload.

## Kiểm thử

```powershell
python -m pytest -q
git diff --check
```

Endpoint tests dùng SQLite tạm và không gọi vnstock hay internet.

## Nạp dữ liệu

Việc thu thập là bước riêng, không tự chạy khi tải dashboard. `DataCollector.collect_stock_data(symbol)` lấy dữ liệu qua vnstock, chuẩn hóa schema OHLCV và lưu qua `DatabaseManager`. Cần có cấu hình/môi trường vnstock hợp lệ để chạy bước thu thập thực tế.

> Dữ liệu và biểu đồ chỉ phục vụ mục đích học tập, không phải khuyến nghị đầu tư.
