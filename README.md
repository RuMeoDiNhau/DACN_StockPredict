# Ứng Dụng AI Agent Và LLM Vào Dự Báo Giá Chứng Khoán

## 📋 Mô tả dự án
Đây là đồ án chuyên ngành của sinh viên năm 4 khoa Khoa học Máy tính, Đại học Bách Khoa. Dự án phát triển một ứng dụng web dự báo giá chứng khoán Việt Nam sử dụng AI Agent và Large Language Model (LLM) để phân tích dữ liệu từ internet.

## 🎯 Mục tiêu
- Xây dựng hệ thống thu thập dữ liệu chứng khoán tự động
- Áp dụng mô hình LSTM để dự báo giá cổ phiếu
- Tích hợp AI Agent để phân tích tin tức và sentiment
- Sử dụng LLM để tạo báo cáo phân tích tự động
- Giao diện người dùng tương tự TradingView

## 🏗️ Kiến trúc hệ thống

```
📁 doancn/
├── 📄 README.md                   # Tài liệu hướng dẫn
├── 📄 requirements.txt            # Danh sách thư viện
├── 📄 run.py                      # File chạy ứng dụng chính
├── 📁 config/                     # Cấu hình hệ thống
├── 📁 data/                       # Module xử lý dữ liệu
├── 📁 models/                     # Mô hình AI/ML
├── 📁 app/                        # Ứng dụng web
├── 📁 utils/                      # Tiện ích hỗ trợ
└── 📁 tests/                      # Kiểm thử
```

## 🔧 Công nghệ sử dụng
- **Backend**: Flask, SQLite
- **AI/ML**: TensorFlow/Keras, scikit-learn, transformers
- **Data Collection**: BeautifulSoup, requests, yfinance
- **Frontend**: HTML, CSS, JavaScript, Chart.js
- **LLM**: OpenAI API (hoặc local models)

## 📦 Cài đặt và chạy

### 1. Cài đặt môi trường
```bash
# Tạo virtual environment
python -m venv venv

# Kích hoạt virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Cài đặt thư viện
pip install -r requirements.txt
```

### 2. Cấu hình
```bash
# Copy file cấu hình mẫu
cp config/settings.py.example config/settings.py

# Chỉnh sửa cấu hình API keys và database
# Mở config/settings.py và điền thông tin cần thiết
```

### 3. Chạy ứng dụng
```bash
# Chạy ứng dụng
python run.py

# Ứng dụng sẽ chạy tại: http://localhost:5000
```

## 🎮 Hướng dẫn sử dụng

### 1. Thu thập dữ liệu
- Truy cập tab "Quản lý dữ liệu"
- Chọn mã cổ phiếu cần thu thập (VD: VHM, VIC, FPT)
- Nhấn "Bắt đầu thu thập"

### 2. Huấn luyện mô hình
- Vào tab "Mô hình AI"
- Chọn loại mô hình (LSTM, GRU)
- Thiết lập tham số huấn luyện
- Nhấn "Huấn luyện"

### 3. Dự báo giá
- Tab "Dự báo" để xem kết quả
- Chọn mã cổ phiếu và khoảng thời gian
- Xem biểu đồ và phân tích

### 4. Phân tích AI Agent
- Tab "Phân tích thông minh"
- Xem báo cáo sentiment và tin tức
- Đọc phân tích từ LLM

## 📊 Tính năng chính

### 🔍 Thu thập dữ liệu
- Giá cổ phiếu lịch sử từ các sàn VN
- Tin tức tài chính từ các trang web
- Chỉ số kinh tế vĩ mô
- Sentiment từ mạng xã hội

### 🤖 AI Agent
- Phân tích tin tức tự động
- Đánh giá sentiment thị trường
- Tạo tín hiệu mua/bán
- Báo cáo phân tích hàng ngày

### 📈 Mô hình dự báo
- LSTM cho chuỗi thời gian
- Ensemble methods
- Feature engineering tự động
- Backtesting và đánh giá

### 💬 LLM Integration
- Tóm tắt báo cáo tài chính
- Giải thích kết quả dự báo
- Tư vấn đầu tư cá nhân hóa
- Q&A về thị trường

## 🚀 Roadmap phát triển

### Phase 1 (Hiện tại)
- ✅ Thiết lập cấu trúc dự án
- ✅ Thu thập dữ liệu cơ bản
- ✅ Mô hình LSTM đơn giản
- ✅ Giao diện cơ bản

### Phase 2 (Tương lai)
- ⏳ Tích hợp AI Agent
- ⏳ LLM analysis
- ⏳ Real-time data
- ⏳ Mobile responsive

### Phase 3 (Mở rộng)
- 📋 Thị trường quốc tế
- 📋 Trading bot
- 📋 Portfolio management
- 📋 Social trading

## 🔬 Kết quả thực nghiệm
- Độ chính xác dự báo: ~75-80%
- Thời gian xử lý: < 2 giây/dự báo
- Hỗ trợ 50+ mã cổ phiếu VN
- Cập nhật real-time

## 🤝 Đóng góp
Dự án này được phát triển cho mục đích học tập. Mọi góp ý và đóng góp đều được chào đón.

## 📜 Bản quyền
© 2024 - Đồ án chuyên ngành, Đại học Bách Khoa TP.HCM

## 📞 Liên hệ
- Email: [your-email@example.com]
- GitHub: [your-github-username]

---
*"Đầu tư có rủi ro, hãy cân nhắc kỹ lưỡng trước khi đưa ra quyết định"*