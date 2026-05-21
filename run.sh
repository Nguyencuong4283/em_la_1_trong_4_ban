#!/bin/bash

# Di chuyển đến thư mục của script này
cd "$(dirname "$0")"

echo "=========================================================="
echo "   UIT Class Registration Tool - Trình khởi chạy macOS/Linux"
echo "=========================================================="

# Kiểm tra Python3
if ! command -v python3 &> /dev/null; then
    echo "[-] Lỗi: Không tìm thấy Python3 trên hệ thống của bạn."
    echo "    Vui lòng tải và cài đặt Python từ https://www.python.org/"
    exit 1
fi

# Kiểm tra và khởi tạo thư mục venv
if [ ! -d "venv" ]; then
    echo "[*] Không tìm thấy thư mục venv. Đang tiến hành tạo môi trường ảo Python..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "[-] Lỗi: Không thể tạo môi trường ảo venv."
        exit 1
    fi
    echo "[+] Đã tạo môi trường ảo thành công."
    
    echo "[*] Đang kích hoạt venv và cài đặt các thư viện yêu cầu..."
    source venv/bin/activate
    
    echo "[*] Nâng cấp pip..."
    pip install --upgrade pip
    
    echo "[*] Cài đặt các gói từ requirements.txt..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[-] Lỗi: Cài đặt thư viện thất bại."
        exit 1
    fi
    
    echo "[*] Cài đặt trình duyệt Playwright Chromium..."
    playwright install chromium
    if [ $? -ne 0 ]; then
        echo "[-] Lỗi: Cài đặt trình duyệt Playwright thất bại."
        exit 1
    fi
    echo "[+] Hoàn tất thiết lập môi trường!"
else
    echo "[+] Đã phát hiện môi trường ảo venv."
    source venv/bin/activate
fi

# Chạy Web UI Dashboard
echo "=========================================================="
echo "[*] Đang khởi chạy Giao diện Web UI Dashboard..."
echo "[*] Vui lòng truy cập địa chỉ: http://localhost:8000"
echo "=========================================================="
echo "Nhấn Ctrl+C để dừng chương trình."
echo ""
if [ -f "venv/bin/python3" ]; then
    venv/bin/python3 web_server.py
else
    python3 web_server.py
fi
