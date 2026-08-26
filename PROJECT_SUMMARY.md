# 📊 TÓM TẮT DỰ ÁN - STOCK AI PREDICTOR

## 🎯 Thông tin dự án
- **Tên đề tài:** Ứng dụng AI Agent Và LLM Vào Dự Báo Giá Chứng Khoán Dựa Trên Dữ Liệu Trên Internet
- **Loại:** Đồ án chuyên ngành
- **Trường:** Đại học Bách Khoa TP.HCM
- **Khoa:** Khoa học Máy tính
- **Năm học:** 2024

## 📈 Mục tiêu dự án
- Xây dựng hệ thống dự báo giá chứng khoán Việt Nam
- Áp dụng AI Agent và LLM để phân tích dữ liệu
- Tạo giao diện web tương tự TradingView
- Tích hợp thu thập dữ liệu tự động từ internet

## 🛠️ Công nghệ sử dụng
- **Backend:** Python, Flask
- **AI/ML:** TensorFlow, LSTM, scikit-learn
- **Data Collection:** yfinance, BeautifulSoup, requests
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap, Chart.js
- **Database:** SQLite (có thể mở rộng PostgreSQL)
- **LLM:** OpenAI GPT (tùy chọn), TextBlob

## 🗂️ Cấu trúc dự án

### 📊 Thống kê
- **Tổng files Python:** 20 files
- **Templates HTML:** 3 files
- **Tổng dòng code:** 3000+ lines
- **Modules chính:** 8 modules

### 📁 Cấu trúc thư mục
```
doancn/
├── 📄 README.md (Hướng dẫn chính)
├── 📄 SETUP.md (Cài đặt chi tiết)
├── 🚀 run.py (Khởi chạy ứng dụng)
├── 🚀 install.py (Cài đặt tự động)
├── 🚀 demo.py (Test hệ thống)
├── ⚙️ config/ (Cấu hình)
├── 📊 data/ (Thu thập & xử lý)
├── 🤖 models/ (AI/ML models)
├── 🌐 app/ (Web application)
├── 🛠️ utils/ (Tiện ích)
└── 🧪 tests/ (Kiểm thử)
```

## 🎯 Tính năng chính

### 🔍 1. Thu thập dữ liệu
- Thu thập từ Yahoo Finance, tin tức
- Hỗ trợ 25+ mã cổ phiếu VN
- Lên lịch tự động hàng ngày
- Backup dữ liệu thô

### ⚙️ 2. Xử lý dữ liệu
- Làm sạch, chuẩn hóa dữ liệu
- Technical indicators (SMA, EMA, MACD, RSI)
- Feature engineering cho LSTM
- Normalization (MinMax, Standard)

### 🧠 3. Mô hình AI/ML
- LSTM cho dự báo giá
- AI Agent phân tích sentiment
- Auto-evaluation độ chính xác
- Model caching để tối ưu

### 🌐 4. Giao diện web
- Dashboard tương tự TradingView
- Real-time charts với Chart.js
- Mobile responsive Bootstrap
- RESTful API endpoints

### 💾 5. Quản lý dữ liệu
- SQLite operations
- Logging chi tiết
- Auto backup
- Error handling toàn diện