@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

:: Di chuyển đến thư mục của script
cd /d "%~dp0"

echo ==========================================================
echo    UIT Class Registration Tool - Trình khởi chạy Windows
echo ==========================================================

:: Kiểm tra Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [-] Lỗi: Không tìm thấy Python trên hệ thống của bạn.
    echo     Vui lòng tải và cài đặt Python từ https://www.python.org/
    echo     Đảm bảo đã tick chọn "Add Python to PATH" khi cài đặt.
    pause
    exit /b 1
)

:: Kiểm tra và khởi tạo venv
if not exist "venv\" (
    echo [*] Không tìm thấy thư mục venv. Đang tiến hành tạo môi trường ảo Python...
    python -m venv venv
    if !errorlevel! neq 0 (
        echo [-] Lỗi: Không thể tạo môi trường ảo venv.
        pause
        exit /b 1
    )
    echo [+] Đã tạo môi trường ảo thành công.
    
    echo [*] Đang kích hoạt venv và cài đặt các thư viện yêu cầu...
    call venv\Scripts\activate.bat
    
    echo [*] Nâng cấp pip...
    python -m pip install --upgrade pip
    
    echo [*] Cài đặt các gói từ requirements.txt...
    pip install -r requirements.txt
    if !errorlevel! neq 0 (
        echo [-] Lỗi: Cài đặt thư viện thất bại.
        pause
        exit /b 1
    )
    
    echo [*] Cài đặt trình duyệt Playwright Chromium...
    playwright install chromium
    if !errorlevel! neq 0 (
        echo [-] Lỗi: Cài đặt trình duyệt Playwright thất bại.
        pause
        exit /b 1
    )
    echo [+] Hoàn tất thiết lập môi trường^!
) else (
    echo [+] Đã phát hiện môi trường ảo venv.
    call venv\Scripts\activate.bat
)

:: Chạy Web UI Dashboard
echo ==========================================================
echo [*] Đang khởi chạy Giao diện Web UI Dashboard...
echo [*] Vui lòng truy cập địa chỉ: http://localhost:8000
echo ==========================================================
echo Nhấn Ctrl+C để dừng chương trình.
echo.
if exist "venv\Scripts\python.exe" (
    venv\Scripts\python.exe web_server.py
) else (
    python web_server.py
)
pause
