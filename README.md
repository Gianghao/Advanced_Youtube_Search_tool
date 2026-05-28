# Advance Youtube Search Tool 🚀

Dự án công cụ tìm kiếm cảnh quay trong video YouTube tích hợp AI (AI Video Scene Search Engine). 

## 📂 Cấu trúc thư mục

```text
.
├── backend/                  # Chứa toàn bộ mã nguồn phía máy chủ (FastAPI)
│   ├── api/                  # Các router định tuyến (VD: auth_router.py)
│   ├── app/                  # Các cấu hình và model Pydantic
│   │   ├── config.py         # Cấu hình biến môi trường
│   │   └── models/           # Định nghĩa các schema dữ liệu (UserSignUp, UserSignIn...)
│   ├── services/             # Logic xử lý nghiệp vụ (AuthService, Supabase interaction...)
│   ├── static/               # Các file tĩnh (CSS, JS, hình ảnh)
│   ├── templates/            # Các file HTML mẫu (Jinja2)
│   ├── main.py               # File chạy ứng dụng FastAPI chính
│   ├── .env.example          # File mẫu chứa các biến môi trường cần thiết
│   └── .env                  # File chứa các key cấu hình (Không push lên Github)
├── tests/                    # Thư mục chứa các bài kiểm thử (Pytest)
│   └── test_auth.py          # Kiểm thử tính năng đăng nhập/đăng ký
├── frontend/                 # Chứa mã nguồn giao diện người dùng (nếu có)
├── pyproject.toml            # Cấu hình dự án (dependencies, pytest config)
├── requirements.txt          # Danh sách tất cả các thư viện cần cài đặt
└── setup.sh                  # Script tự động cài đặt môi trường
```

## 🛠️ Hướng dẫn cài đặt & Khởi chạy (Dành cho người mới clone code về)

Dự án này sử dụng môi trường Python ảo và các gói phụ thuộc được liệt kê trong file `requirements.txt`.

### Cách 1: Cài đặt tự động bằng Script (Khuyên dùng)
Dành cho hệ điều hành Linux / MacOS hoặc môi trường Git Bash trên Windows:

1. Mở terminal tại thư mục gốc của dự án.
2. Cấp quyền thực thi và chạy file cài đặt:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```
3. Sau khi chạy xong, script sẽ tự động tạo một file `backend/.env`. Bạn cần mở file này lên và điền thông tin **Supabase URL** và **Supabase Key** của bạn vào.
4. Cuối cùng, khởi động server:
   ```bash
   uv run uvicorn backend.main:app --reload
   ```
   *(Server sẽ chạy tại `http://127.0.0.1:8000`)*

### Cách 2: Cài đặt thủ công bằng công cụ `uv` (Hoặc `pip`)
1. Tạo môi trường ảo (Virtual Environment):
   ```bash
   uv venv
   # Kích hoạt môi trường (Linux/Mac):
   source .venv/bin/activate
   # Kích hoạt môi trường (Windows):
   # .venv\Scripts\activate
   ```
2. Cài đặt các thư viện cần thiết:
   ```bash
   uv pip install -r requirements.txt
   ```
3. Copy file môi trường:
   ```bash
   cp backend/.env.example backend/.env
   ```
   *Nhớ chỉnh sửa file `backend/.env` bằng key Supabase thật của bạn.*
4. Chạy dự án:
   ```bash
   uv run uvicorn backend.main:app --reload
   ```

## 🧪 Hướng dẫn chạy Test (Kiểm thử)
Dự án đã được cấu hình tự động nhận diện `PYTHONPATH`. Bạn có thể chạy tất cả các bài kiểm thử (không yêu cầu Supabase thật vì đã sử dụng Mock):
```bash
uv run pytest
```
Hoặc test riêng một file:
```bash
uv run pytest tests/test_auth.py
```
