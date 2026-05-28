#!/bin/bash

echo "🚀 Bắt đầu cài đặt dự án..."

# Kiểm tra xem uv đã được cài đặt chưa
if ! command -v uv &> /dev/null
then
    echo "⚠️ 'uv' chưa được cài đặt. Đang tiến hành cài đặt uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

echo "📦 Đang cài đặt các thư viện từ requirements.txt..."
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

if [ ! -f backend/.env ]; then
    echo "⚙️ Tạo file .env từ .env.example..."
    cp backend/.env.example backend/.env
    echo "⚠️ Vui lòng mở file backend/.env và điền thông tin Supabase của bạn vào!"
fi

echo "✅ Cài đặt hoàn tất! Bạn có thể chạy server bằng lệnh:"
echo "uv run uvicorn backend.main:app --reload"
