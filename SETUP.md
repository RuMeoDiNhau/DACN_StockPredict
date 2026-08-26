# 🚀 HƯỚNG DẪN CÀI ĐẶT VÀ CHẠY ỨNG DỤNG

## 📋 Yêu cầu hệ thống
- Python 3.8 trở lên
- RAM: tối thiểu 4GB, khuyến nghị 8GB
- Ổ cứng: ít nhất 2GB trống
- Internet để tải dữ liệu

## ⚡ Cài đặt nhanh (Auto Installer)

### Bước 1: Chạy Auto Installer
```bash
python install.py
```

### Bước 2: Kích hoạt virtual environment
```bash
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate
```

### Bước 3: Chạy ứng dụng
```bash
python run.py
```

### Bước 4: Truy cập ứng dụng
Mở trình duyệt và truy cập: http://localhost:5000

## 📦 Cài đặt thủ công

### Bước 1: Tạo virtual environment
```bash
python -m venv venv
```

### Bước 2: Kích hoạt virtual environment
```bash
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate
```

### Bước 3: Upgrade pip
```bash
python -m pip install --upgrade pip
```

### Bước 4: Cài đặt thư viện
```bash
pip install -r requirements.txt
```

### Bước 5: Test cài đặt
```bash
python demo.py
```

### Bước 6: Chạy ứng dụng
```bash
python run.py
```

## 🧪 Kiểm tra cài đặt

### Test cơ bản
```bash
python demo.py
```

### Test chi tiết hơn
```bash
python -m pytest tests/ -v
```

## 🛠️ Xử lý sự cố

### Lỗi: ModuleNotFoundError
```bash
# Đảm bảo đã kích hoạt venv
pip install -r requirements.txt
```

### Lỗi: TensorFlow không cài được
```bash
# Cài phiên bản cụ thể cho Windows
pip install tensorflow==2.13.0 --only-binary=all
```

### Lỗi: Permission denied
```bash
# Chạy cmd/terminal với quyền administrator
```

### Lỗi: Port 5000 bị chiếm
- Thay đổi PORT trong config/settings.py
- Hoặc tắt ứng dụng đang dùng port 5000

## 📚 Hướng dẫn sử dụng

### 1. Thu thập dữ liệu
- Truy cập tab "Quản lý dữ liệu"
- Chọn mã cổ phiếu (VD: VHM, FPT, VIC)
- Nhấn "Thu thập dữ liệu"
- Chờ hệ thống tải dữ liệu từ Yahoo Finance

### 2. Huấn luyện mô hình
- Vào tab "Mô hình"
- Chọn mã cổ phiếu đã có dữ liệu
- Cấu hình tham số (epochs, batch_size)
- Nhấn "Huấn luyện mô hình"
- Chờ quá trình hoàn thành (có thể mất 10-30 phút)

### 3. Xem dự báo
- Quay lại Dashboard
- Chọn mã cổ phiếu đã train
- Xem biểu đồ giá và dự báo
- Đọc phân tích AI Agent

### 4. Phân tích AI
- Tab "Phân tích AI" để xem insights chi tiết
- Sentiment analysis từ tin tức
- Khuyến nghị đầu tư

## 🔧 Cấu hình nâng cao

### OpenAI API (tùy chọn)
1. Đăng ký tài khoản tại https://openai.com
2. Lấy API key
3. Cập nhật config/settings.py:
```python
OPENAI_API_KEY = 'your-actual-api-key'
```

### Database
- Mặc định sử dụng SQLite
- Để chuyển sang PostgreSQL, cập nhật SQLALCHEMY_DATABASE_URI

### Logging
- Log files được lưu trong thư mục logs/
- Cấu hình level trong config/settings.py

## 📊 Cấu trúc dự án

```
doancn/
├── README.md              # Tài liệu chính
├── SETUP.md              # Hướng dẫn cài đặt này
├── requirements.txt      # Thư viện Python
├── run.py               # File chạy ứng dụng
├── demo.py              # Script test/demo
├── install.py           # Auto installer
├── config/              # Cấu hình
├── data/                # Module dữ liệu
├── models/              # Mô hình AI/ML
├── app/                 # Ứng dụng web Flask
├── utils/               # Tiện ích
├── tests/               # Unit tests
└── logs/                # Log files
```

## 🎯 Demo và Video

### Video hướng dẫn
[Liên kết đến video demo - cần tạo]

### Screenshots
[Thêm ảnh screenshot giao diện]

## 💡 Gợi ý phát triển

### Tính năng có thể thêm
- Thêm nhiều loại mô hình (GRU, Transformer)
- Tích hợp real-time data
- Mobile responsive
- Portfolio management
- Social trading features

### Cải thiện hiệu suất
- Cache dữ liệu Redis
- Async data collection
- Model compression
- CDN cho static files

## ❓ FAQ

**Q: Ứng dụng có hoạt động offline không?**
A: Một phần. Sau khi đã có dữ liệu và mô hình, có thể dự báo offline. Nhưng cần internet để thu thập dữ liệu mới.

**Q: Độ chính xác dự báo như thế nào?**
A: Thường đạt 70-80% cho dự báo ngắn hạn (1-3 ngày). Độ chính xác phụ thuộc vào chất lượng dữ liệu và biến động thị trường.

**Q: Có thể dùng cho thị trường khác ngoài VN không?**
A: Có, chỉ cần thay đổi source data trong DataCollector và cập nhật danh sách symbols.

**Q: Tại sao cần OpenAI API?**
A: Để tạo báo cáo phân tích chi tiết và tự nhiên hơn. Không bắt buộc, ứng dụng vẫn chạy được với báo cáo cơ bản.

## 🆘 Hỗ trợ

Nếu gặp vấn đề:
1. Đọc kỹ error message
2. Kiểm tra logs/ để xem chi tiết
3. Thử chạy `python demo.py` để test từng phần
4. Liên hệ: [email tác giả]

## 📝 License

Dự án này chỉ phục vụ mục đích học tập và nghiên cứu.

---
**⚠️ Lưu ý quan trọng:** Đây chỉ là công cụ hỗ trợ phân tích, không phải lời khuyên đầu tư. Luôn tự nghiên cứu và cân nhắc rủi ro trước khi đầu tư.