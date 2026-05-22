import os
import sys

def ensure_venv():
    if sys.prefix == sys.base_prefix:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if sys.platform == "win32":
            venv_python = os.path.join(current_dir, "venv", "Scripts", "python.exe")
        else:
            venv_python = os.path.join(current_dir, "venv", "bin", "python3")
            
        if os.path.exists(venv_python):
            os.execv(venv_python, [venv_python] + sys.argv)

ensure_venv()

import json
import argparse
import time
import random
from playwright.sync_api import sync_playwright

def check_for_updates():
    """
    Kiểm tra xem có bản cập nhật mới trên GitHub hay không.
    """
    import urllib.request
    version_path = os.path.join(os.path.dirname(__file__), "version.txt")
    
    local_version = "1.2.2"
    if os.path.exists(version_path):
        try:
            with open(version_path, "r", encoding="utf-8") as f:
                local_version = f.read().strip()
        except Exception:
            pass
            
    url = "https://raw.githubusercontent.com/Nguyencuong4283/em_la_1_trong_4_ban/main/version.txt"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=3) as response:
            remote_version = response.read().decode('utf-8').strip()
            if remote_version and remote_version != local_version:
                print("\n" + "="*58)
                print(f"[!] PHÁT HIỆN BẢN CẬP NHẬT MỚI: v{remote_version} (Hiện tại: v{local_version})")
                print("[!] Vui lòng chạy lệnh 'git pull' để cập nhật tính năng mới nhất.")
                print("="*58 + "\n")
                return remote_version
    except Exception:
        pass
    return None

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    default_config = {
        "target_url": "https://dkhp.uit.edu.vn",
        "username": "",
        "password": "",
        "class_codes": [],
        "headless": False,
        "auto_click_submit": True,
        "scan_interval_ms": 5000,
        "submit_delay_ms": 1500,
        "open_time": ""
    }
    if not os.path.exists(config_path):
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            print("[+] Đã tự động tạo tệp cấu hình config.json mặc định.")
        except Exception as e:
            print(f"[-] Không thể tạo tệp cấu hình: {e}")
            return default_config
            
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[-] Không thể đọc tệp cấu hình config.json: {e}")
        return default_config


def send_desktop_notification(title, message):
    """
    Gửi thông báo trực tiếp đến màn hình desktop của người dùng.
    Hỗ trợ macOS, Windows và Linux.
    """
    import platform
    import shutil
    import subprocess
    
    title_escaped = title.replace('"', '\\"')
    message_escaped = message.replace('"', '\\"')
    
    try:
        system = platform.system()
        if system == "Darwin":  # macOS
            cmd = f'osascript -e \'display notification "{message_escaped}" with title "{title_escaped}" sound name "Glass"\''
            subprocess.run(cmd, shell=True, capture_output=True)
        elif system == "Windows":  # Windows
            ps_script = f'''
            [void] [System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms")
            $objNotifyIcon = New-Object System.Windows.Forms.NotifyIcon
            $objNotifyIcon.Icon = [System.Drawing.SystemIcons]::Information
            $objNotifyIcon.BalloonTipIcon = "Info"
            $objNotifyIcon.BalloonTipTitle = "{title_escaped}"
            $objNotifyIcon.BalloonTipText = "{message_escaped}"
            $objNotifyIcon.Visible = $True
            $objNotifyIcon.ShowBalloonTip(5000)
            '''
            subprocess.run(["powershell", "-Command", ps_script], capture_output=True)
        else:  # Linux
            if shutil.which("notify-send"):
                subprocess.run(["notify-send", title, message])
    except Exception as e:
        print(f"[-] Không thể gửi thông báo desktop: {e}")



def find_checkbox_for_class(page, class_code):
    """
    Tìm checkbox liên quan đến mã lớp cụ thể.
    """
    text_selectors = [
        f"text={class_code}",
        f"xpath=//*[text()='{class_code}']",
        f"xpath=//*[contains(text(), '{class_code}')]"
    ]
    
    for selector in text_selectors:
        try:
            loc = page.locator(selector)
            count = loc.count()
            for i in range(count):
                element = loc.nth(i)
                if not element.is_visible():
                    continue
                
                # 1. Tìm phần tử hàng (TR hoặc tương đương) chứa class_code
                row = None
                for depth in range(1, 5):
                    ancestor = element.locator(f"xpath=./ancestor::*[position()={depth}]")
                    if ancestor.count() > 0:
                        is_row = ancestor.evaluate("el => el.tagName === 'TR' || el.getAttribute('role') === 'row' || (el.classList && el.classList.contains('row'))")
                        if is_row:
                            row = ancestor
                            break
                
                # 2. Nếu tìm thấy hàng, tìm checkbox CHỈ bên trong hàng đó
                if row:
                    checkbox = row.locator("input[type='checkbox']")
                    if checkbox.count() > 0:
                        return checkbox.first
                    
                    checkbox_role = row.locator("[role='checkbox']")
                    if checkbox_role.count() > 0:
                        return checkbox_role.first
                else:
                    # 3. Fallback: Nếu không xác định được hàng, tìm ở parent/sibling trực tiếp nhưng tránh đi quá xa lên tbody/table
                    parent = element.locator("xpath=..")
                    if parent.count() > 0:
                        parent_tag = parent.evaluate("el => el.tagName")
                        if parent_tag not in ["TBODY", "TABLE"]:
                            checkbox = parent.locator("input[type='checkbox']")
                            if checkbox.count() > 0:
                                return checkbox.first
                            
                            grandparent = parent.locator("xpath=..")
                            if grandparent.count() > 0:
                                grandparent_tag = grandparent.evaluate("el => el.tagName")
                                if grandparent_tag not in ["TBODY", "TABLE"]:
                                    checkbox = grandparent.locator("input[type='checkbox']")
                                    if checkbox.count() > 0:
                                        return checkbox.first
        except Exception:
            pass
            
    return None

def click_submit_button(page):
    """
    Tìm và bấm nút xác nhận đăng ký.
    """
    submit_selectors = [
        "#btn-submit-registration",
        "button:has-text('Xác nhận đăng ký')",
        "button:has-text('Xác nhận')",
        "button:has-text('Đăng ký')",
        "input[type='submit']",
        "button.btn-submit",
        "button.btn-success",
        "button:has-text('Confirm')",
        "button:has-text('Submit')",
        "button:has-text('Register')"
    ]
    
    for selector in submit_selectors:
        try:
            btn = page.locator(selector)
            if btn.count() > 0 and btn.first.is_visible():
                print(f"[+] Tìm thấy nút bấm xác nhận bằng selector: '{selector}'")
                btn.first.click()
                print("[+] ĐĂNG KÝ THÀNH CÔNG: Đã bấm nút Xác Nhận Đăng Ký!")
                return True
        except Exception:
            pass
    return False

def handle_auto_login(page, username, password):
    """
    Tự động điền tài khoản và mật khẩu nếu phát hiện biểu mẫu đăng nhập.
    """
    if not username or not password:
        return False
        
    try:
        # Tìm ô mật khẩu (đặc trưng nhất của trang đăng nhập)
        password_input = page.locator("input[type='password']")
        if password_input.count() > 0 and password_input.first.is_visible():
            # Tìm ô tài khoản (input dạng text/email hoặc chứa từ khóa user/name/login)
            username_selectors = [
                "input[id*='user']", "input[id*='name']", "input[id*='login']",
                "input[name*='user']", "input[name*='name']", "input[name*='login']",
                "input[type='text']", "input[type='email']"
            ]
            username_input = None
            for selector in username_selectors:
                loc = page.locator(selector)
                if loc.count() > 0 and loc.first.is_visible():
                    username_input = loc.first
                    break
            
            if username_input and username_input != password_input.first:
                print("[i] Phát hiện trang đăng nhập. Đang tự động điền thông tin...")
                username_input.fill(username)
                password_input.first.fill(password)
                
                # Tìm nút đăng nhập
                submit_selectors = [
                    "#btn-login-mock",  # ID nút đăng nhập giả lập
                    "button[type='submit']",
                    "input[type='submit']",
                    "button:has-text('Đăng nhập')",
                    "button:has-text('Login')",
                    "a:has-text('Đăng nhập')",
                    "a:has-text('Login')"
                ]
                
                for submit_sel in submit_selectors:
                    btn = page.locator(submit_sel)
                    if btn.count() > 0 and btn.first.is_visible():
                        btn.first.click()
                        print("[+] Đã tự động bấm đăng nhập!")
                        # Đợi một chút để trang tải/chuyển tiếp sau khi click đăng nhập
                        page.wait_for_timeout(1000)
                        return True
    except Exception as e:
        print(f"[-] Lỗi khi cố gắng tự động đăng nhập: {e}")
    return False

def get_row_text_for_class(page, class_code):
    """
    Lấy toàn bộ nội dung văn bản của hàng chứa mã lớp.
    """
    text_selectors = [
        f"text={class_code}",
        f"xpath=//*[text()='{class_code}']",
        f"xpath=//*[contains(text(), '{class_code}')]"
    ]
    for selector in text_selectors:
        try:
            loc = page.locator(selector)
            count = loc.count()
            for i in range(count):
                element = loc.nth(i)
                if not element.is_visible():
                    continue
                # Đi lên các phần tử cha để tìm thẻ TR
                for depth in range(1, 5):
                    ancestor = element.locator(f"xpath=./ancestor::*[position()={depth}]")
                    if ancestor.count() > 0:
                        tag_name = ancestor.evaluate("el => el.tagName")
                        if tag_name == "TR":
                            return ancestor.text_content()
        except Exception:
            pass
    return None

def wait_until_open_time(page, open_time_str):
    """
    Chờ cho đến khi tới giờ mở cổng đăng ký (định dạng HH:MM hoặc HH:MM:SS).
    Trong thời gian chờ, in ra đếm ngược và giữ trình duyệt hiển thị ở trang đăng ký.
    Khi đạt đến thời điểm, F5 reload trang 1 lần.
    """
    if not open_time_str:
        return
        
    import datetime
    try:
        parts = list(map(int, open_time_str.split(":")))
        if len(parts) == 2:
            open_hour, open_minute = parts
            open_second = 0
        elif len(parts) == 3:
            open_hour, open_minute, open_second = parts
        else:
            raise ValueError
    except Exception:
        print(f"[-] Định dạng giờ mở đăng ký không hợp lệ: '{open_time_str}'. Yêu cầu định dạng HH:MM hoặc HH:MM:SS. Bỏ qua chế độ hẹn giờ.")
        return

    now = datetime.datetime.now()
    open_time = now.replace(hour=open_hour, minute=open_minute, second=open_second, microsecond=0)
    
    # Nếu giờ mở đăng ký nhỏ hơn giờ hiện tại (đã qua giờ mở trong ngày), ta không cần chờ
    if now >= open_time:
        return
        
    print(f"\n[>>>] ĐÃ BẬT CHẾ ĐỘ CHỜ GIỜ MỞ ĐĂNG KÝ: {open_time_str} [<<<]")
    print(f"[i] Trình duyệt đang giữ kết nối ở trang đăng ký học phần...")
    
    # Vòng lặp đếm ngược giây
    last_print_time = 0
    while True:
        now = datetime.datetime.now()
        diff = open_time - now
        seconds_left = int(diff.total_seconds())
        if seconds_left <= 0:
            break
            
        # In đếm ngược mỗi giây một lần
        if seconds_left != last_print_time:
            print(f"[i] Đang chờ mở cổng đăng ký. Đếm ngược: {seconds_left} giây...   ", end="\r")
            last_print_time = seconds_left
            
        time.sleep(0.2)
        
    print("\n[+] ĐÃ ĐẾN GIỜ MỞ ĐĂNG KÝ! Đang tự động F5 tải lại trang...")
    try:
        page.reload()
        page.wait_for_timeout(2000)
    except Exception as e:
        print(f"[-] Lỗi khi reload trang: {e}")

def is_slots_full(row_text):
    """
    Kiểm tra xem lớp đã hết slot dựa trên tỉ số sĩ số trong văn bản hàng (ví dụ: 30/30).
    """
    if not row_text:
        return False
    import re
    # Loại bỏ các chuỗi ngày tháng dạng DD/MM/YYYY hoặc DD/MM/YY để tránh so sánh nhầm ngày (ví dụ 20/07/2026)
    text_clean = re.sub(r"\b\d{1,2}\s*/\s*\d{1,2}\s*/\s*\d{2,4}\b", "", row_text)
    
    # Tìm dạng số/số (ví dụ 30/30, 45/45, 30 / 30, v.v.)
    matches = re.findall(r"(?<!/)\b(\d+)\s*/\s*(\d+)\b(?!/)", text_clean)
    for current_str, total_str in matches:
        try:
            current = int(current_str)
            total = int(total_str)
            if total > 0 and current >= total:
                return True
        except ValueError:
            pass
    return False

def get_class_status(page, class_code):
    """
    Đánh giá trạng thái hiện tại của một mã lớp:
    - REGISTERED: Đã đăng ký thành công (checkbox đã check hoặc nằm trong danh sách đã đk).
    - OUT_OF_SLOTS: Hết slot đăng ký (checkbox bị disabled và unchecked, hoặc có chữ 'hết chỗ'/'hết slot'/...).
    - AVAILABLE: Lớp có sẵn để đăng ký (checkbox enabled và unchecked).
    - NOT_FOUND: Không tìm thấy lớp học trên trang.
    """
    checkbox = find_checkbox_for_class(page, class_code)
    
    # 1. Nếu không tìm thấy checkbox, kiểm tra xem lớp có hiện diện trên trang không
    if not checkbox:
        row_text = get_row_text_for_class(page, class_code)
        if row_text:
            row_text_lower = row_text.lower()
            # Kiểm tra xem có từ khóa báo đăng ký thành công không
            if any(kw in row_text_lower for kw in ["đã đăng ký", "đã đk", "registered", "đã chọn", "đã nhận"]):
                return "REGISTERED"
            # Kiểm tra xem có từ khóa báo hết slot không
            if any(kw in row_text_lower for kw in ["hết chỗ", "hết slot", "đầy", "sĩ số đầy", "hết hạn"]):
                return "OUT_OF_SLOTS"
            # Kiểm tra tỉ số slots (ví dụ 30/30)
            if is_slots_full(row_text):
                return "OUT_OF_SLOTS"
            # Nếu không tìm thấy checkbox và không có dấu hiệu đã đăng ký nhưng lớp vẫn hiển thị,
            # mặc định là lớp đã hết slot (hoặc không khả dụng để đăng ký)
            return "OUT_OF_SLOTS"
        return "NOT_FOUND"
        
    try:
        is_checked = checkbox.is_checked()
        is_disabled = checkbox.is_disabled()
    except Exception:
        return "NOT_FOUND"
        
    # 2. Đánh giá dựa trên checkbox và nội dung văn bản của hàng
    if is_disabled:
        if is_checked:
            return "REGISTERED"
        else:
            return "OUT_OF_SLOTS"
    else:
        if is_checked:
            return "REGISTERED"
        else:
            row_text = get_row_text_for_class(page, class_code)
            if row_text:
                row_text_lower = row_text.lower()
                if any(kw in row_text_lower for kw in ["hết chỗ", "hết slot", "đầy", "sĩ số đầy"]):
                    return "OUT_OF_SLOTS"
                if is_slots_full(row_text):
                    return "OUT_OF_SLOTS"
            return "AVAILABLE"

def is_on_registration_page(page):
    """
    Kiểm tra xem trình duyệt đã ở trang đăng ký học phần hay chưa.
    Dựa trên sự hiện diện của bảng đăng ký hoặc nút xác nhận đăng ký hiển thị trên màn hình.
    """
    submit_selectors = [
        "#btn-submit-registration",
        "button:has-text('Xác nhận đăng ký')",
        "button:has-text('Xác nhận')",
        "button:has-text('Đăng ký')"
    ]
    for selector in submit_selectors:
        try:
            btn = page.locator(selector).first
            if btn.count() > 0 and btn.is_visible():
                return True
        except Exception:
            pass
            
    try:
        checkboxes = page.locator("input[type='checkbox']")
        count = checkboxes.count()
        for i in range(count):
            if checkboxes.nth(i).is_visible():
                return True
    except Exception:
        pass
        
    return False
def check_and_handle_load_failure(page):
    """
    Kiểm tra xem trang đăng ký có bị lỗi tải (không hiện danh sách lớp/checkbox/nút xác nhận) hay không.
    Nếu bị lỗi (và không phải trang đăng nhập hay dashboard):
    - Đợi 10 giây kèm theo bộ đếm ngược F5.
    - Tiến hành page.reload() tải lại trang.
    Trả về True nếu phát hiện lỗi và đã reload, ngược lại trả về False.
    """
    # 1. Nếu đang ở biểu mẫu đăng nhập, không làm gì cả để người dùng/hàm tự động đăng nhập xử lý
    try:
        if page.locator("input[type='password']").count() > 0 and page.locator("input[type='password']").first.is_visible():
            return False
    except Exception:
        pass

    # 2. Nếu đã ở trang đăng ký (có checkbox hoặc nút bấm xác nhận), tức là tải thành công
    if is_on_registration_page(page):
        return False

    # 3. Kiểm tra xem có phải trang dashboard không
    # Nếu trang dashboard hiển thị bình thường (có liên kết đến trang đăng ký), không tự động reload ở đây
    # mà để ensure_registration_page xử lý việc click chuyển trang
    nav_selectors = [
        "a:has-text('Đăng ký học phần')",
        "a:has-text('Đăng ký môn học')",
        "a:has-text('Đăng ký')",
        "a:has-text('Registration')",
        "a:has-text('Register')",
        "button:has-text('Đăng ký học phần')",
        "button:has-text('Đăng ký môn học')",
        "a[href*='registration']",
        "a[href*='dang-ky']",
        "#lnk-registration"
    ]
    
    dashboard_visible = False
    for selector in nav_selectors:
        try:
            link = page.locator(selector).first
            if link.count() > 0 and link.is_visible():
                dashboard_visible = True
                break
        except Exception:
            pass

    # 4. Xác định xem có phải trang bị lỗi tải không
    # Lỗi tải khi: URL chứa từ khóa đăng ký/đã click chuyển tiếp (hoặc test mode),
    # HOẶC không thấy thanh điều hướng dashboard (có thể là trang trắng, 502, 503...)
    current_url = page.url.lower()
    is_registration_url = any(keyword in current_url for keyword in ["dang-ky", "dangky", "registration", "register", "mock_register.html"])
    
    # Nếu không phải dashboard và (ở URL đăng ký hoặc không hiển thị thanh điều hướng/trang trắng/502)
    if not dashboard_visible or is_registration_url:
        # Chờ thêm 3 giây phòng trường hợp mạng chậm trang đang tải dở
        page.wait_for_timeout(3000)
        if is_on_registration_page(page):
            return False

        print("\n[-] Không load được danh sách lớp hoặc trang bị lỗi (502/503/Mất kết nối).")
        for i in range(10, 0, -1):
            print(f"[i] Sẽ tự động F5 tải lại trang sau {i} giây...", flush=True)
            page.wait_for_timeout(1000)
            
        print("[i] Đang tiến hành F5 tải lại trang...")
        try:
            page.reload()
            page.wait_for_timeout(2000) # Đợi 2 giây sau reload để trang bắt đầu tải
        except Exception as e:
            print(f"[-] Lỗi khi tải lại trang (F5): {e}")
        return True

    return False

def ensure_registration_page(page, target_url):
    """
    Tự động chuyển hướng sang trang đăng ký học phần từ trang chủ hoặc dashboard.
    """
    # Nếu đang ở biểu mẫu đăng nhập, bỏ qua để người dùng/hàm tự động đăng nhập xử lý
    try:
        if page.locator("input[type='password']").count() > 0 and page.locator("input[type='password']").first.is_visible():
            return
    except Exception:
        pass

    if is_on_registration_page(page):
        return

    print("[i] Chưa vào trang đăng ký học phần. Đang quét liên kết chuyển trang...")
    
    # Danh sách các thẻ link/nút có thể chứa liên kết đến trang đăng ký môn học
    nav_selectors = [
        "a:has-text('Đăng ký học phần')",
        "a:has-text('Đăng ký môn học')",
        "a:has-text('Đăng ký')",
        "a:has-text('Registration')",
        "a:has-text('Register')",
        "button:has-text('Đăng ký học phần')",
        "button:has-text('Đăng ký môn học')",
        "a[href*='registration']",
        "a[href*='dang-ky']",
        "#lnk-registration"
    ]
    
    for selector in nav_selectors:
        try:
            link = page.locator(selector).first
            if link.count() > 0 and link.is_visible():
                print(f"[+] Phát hiện liên kết chuyển trang: '{selector}'. Đang tự động click...")
                link.click()
                page.wait_for_timeout(2000) # Đợi trang tải
                if is_on_registration_page(page):
                    print("[+] Đã chuyển sang trang đăng ký học phần thành công!")
                    return
        except Exception:
            pass
            
    print(f"[i] Cảnh báo: Vẫn chưa ở trang đăng ký học phần (URL hiện tại: {page.url}).")

def main():
    check_for_updates()
    parser = argparse.ArgumentParser(description="UIT Class Registration Auto-Ticking Tool")
    parser.add_argument("--test", action="store_true", help="Chạy chế độ thử nghiệm với trang mock_register.html cục bộ")
    parser.add_argument("--mode", type=str, default=None, choices=["1", "2"], help="Chế độ hoạt động (1: Auto-pilot, 2: Manual)")
    parser.add_argument("--non-interactive", action="store_true", help="Chạy không tương tác (bỏ qua nhấn ENTER)")
    args = parser.parse_args()

    config = load_config()
    registration_completed = False
    
    target_url = config.get("target_url", "https://dkhp.uit.edu.vn")
    username = config.get("username", "")
    password = config.get("password", "")
    class_codes = config.get("class_codes", [])
    headless = config.get("headless", False)
    auto_click_submit = config.get("auto_click_submit", True)
    scan_interval_ms = config.get("scan_interval_ms", 200)
    submit_delay_ms = max(1500, config.get("submit_delay_ms", 5000))
    wait_for_empty_slot = config.get("wait_for_empty_slot", False)

    if args.test:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        mock_file_path = os.path.join(current_dir, "mock_register.html")
        target_url = f"file://{mock_file_path}"
        print(f"[i] Đang chạy chế độ THỬ NGHIỆM cục bộ với file: {mock_file_path}")
        # Ghi đè danh sách lớp học để phù hợp với trang giả lập mock_register.html
        class_codes = ["SE104.O21", "IT002.O22", "MA004.O23", "SS001.O24", "ENG02.Q33"]
    else:
        print(f"[i] Đang cấu hình kết nối tới: {target_url}")

    print(f"[i] Danh sách mã lớp cần đăng ký: {class_codes}")
    print(f"[i] Tần suất quét: {scan_interval_ms}ms")
    print(f"[i] Chờ slot trống: {'Bật (F5 ngẫu nhiên 20-30s khi hết slot)' if wait_for_empty_slot else 'Tắt'}")
    print(f"[i] Độ trễ tự động bấm nút đăng ký: {submit_delay_ms / 1000}s")

    with sync_playwright() as p:
        print("[i] Đang mở trình duyệt Chrome...")
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()
        
        print(f"[i] Đang tải trang web: {target_url}...")
        page.goto(target_url)

        # Thử tự động đăng nhập lúc tải trang ban đầu
        if username and password:
            handle_auto_login(page, username, password)

        mode = args.mode
        if not mode:
            print("\n=================== CHẾ ĐỘ HOẠT ĐỘNG ===================")
            print("1. [Khuyên dùng] Tự động quét liên tục (Auto-pilot)")
            print(f"   - Chương trình sẽ tự quét trang mỗi {scan_interval_ms}ms.")
            print(f"   - Khi tìm thấy lớp, sẽ TỰ ĐỘNG tick chọn và đợi {submit_delay_ms / 1000}s trước khi TỰ ĐỘNG bấm xác nhận.")
            print("2. Kích hoạt thủ công (Manual-trigger)")
            print("   - Chờ bạn đăng nhập xong, nhấn ENTER ở terminal để bắt đầu tick chọn 1 lần.")
            
            mode = input("\nChọn chế độ hoạt động (1 hoặc 2, mặc định 1): ").strip()
            if mode not in ["1", "2"]:
                mode = "1"

        if mode == "1":
            print("\n[>>>] CHẾ ĐỘ TỰ ĐỘNG QUÉT LIÊN TỤC ĐANG BẬT [<<<]")
            print("[i] Vui lòng đăng nhập và di chuyển đến trang chọn môn học.")
            
            # Hẹn giờ chờ mở đăng ký nếu được cấu hình
            open_time_str = config.get("open_time", "")
            if open_time_str:
                # Đảm bảo trình duyệt đã ở trang đăng ký trước khi chờ
                ensure_registration_page(page, target_url)
                wait_until_open_time(page, open_time_str)
                
            print(f"[i] Chương trình đang quét tìm các lớp học mỗi {scan_interval_ms}ms...")
            if not args.non_interactive:
                print("[i] Nhấn Ctrl+C trong Terminal để tắt chương trình.")
            
            total_targets = len(class_codes)
            last_stats_str = ""
            last_print_time = 0
            
            # Khởi tạo biến theo dõi cho chờ slot trống
            previously_registered = set()
            previously_full = set()
            print_not_found_notified = set()
            last_reload_time = time.time()
            current_reload_interval = random.uniform(20.0, 30.0)
            init_registered_scan = True
            
            try:
                while True:
                    # Kiểm tra xem có cần tự động đăng nhập lại không (đề phòng phiên đăng nhập hết hạn)
                    if username and password:
                        handle_auto_login(page, username, password)
                        
                    # Tự động điều hướng sang trang đăng ký học phần nếu cần
                    ensure_registration_page(page, target_url)
                    
                    # Kiểm tra và tự động F5 nếu không tải được danh sách lớp
                    if check_and_handle_load_failure(page):
                        continue
                    
                    if not is_on_registration_page(page):
                        page.wait_for_timeout(scan_interval_ms)
                        continue
                    
                    # Đánh giá trạng thái các lớp mục tiêu
                    stats = {
                        "REGISTERED": [],
                        "OUT_OF_SLOTS": [],
                        "AVAILABLE": [],
                        "NOT_FOUND": []
                    }
                    
                    for code in class_codes:
                        code = code.strip()
                        if not code:
                            continue
                        status = get_class_status(page, code)
                        stats[status].append(code)

                    # Khởi tạo trạng thái đăng ký ban đầu từ lần quét đầu tiên để tránh trùng lặp thông báo
                    if init_registered_scan:
                        previously_registered = set(stats["REGISTERED"])
                        init_registered_scan = False

                    # Cập nhật danh sách các lớp từng bị hết slot
                    for code in stats["OUT_OF_SLOTS"]:
                        previously_full.add(code)

                    # In cảnh báo mã lớp không tồn tại một lần duy nhất
                    for code in stats["NOT_FOUND"]:
                        if code not in print_not_found_notified:
                            print(f"[-] MÃ LỚP KHÔNG TỒN TẠI: Lớp '{code}' không tìm thấy trên trang chọn môn học.")
                            print_not_found_notified.add(code)

                    # Phát hiện các lớp vừa đăng ký thành công mới để gửi thông báo desktop
                    new_registrations = [code for code in stats["REGISTERED"] if code not in previously_registered]
                    for code in new_registrations:
                        msg = f"Đã đăng ký thành công lớp {code}!"
                        print(f"[+] THÔNG BÁO: {msg}")
                        send_desktop_notification("UIT Auto Registration", msg)
                        previously_registered.add(code)
                        
                    # Chuỗi tóm tắt trạng thái
                    stats_str = f"Đăng ký: {len(stats['REGISTERED'])} | Hết slot: {len(stats['OUT_OF_SLOTS'])} | Có sẵn: {len(stats['AVAILABLE'])} | Chưa thấy: {len(stats['NOT_FOUND'])}"
                    current_time = time.time()
                    
                    # Giới hạn in log để tránh flood màn hình (chỉ in khi thay đổi hoặc sau mỗi 5 giây)
                    if stats_str != last_stats_str or (current_time - last_print_time) >= 5:
                        print(f"[i] Trạng thái lớp: {stats_str}")
                        if stats_str != last_stats_str:
                            if stats["REGISTERED"]:
                                print(f"    -> Đã đăng ký: {stats['REGISTERED']}")
                            if stats["OUT_OF_SLOTS"]:
                                print(f"    -> Hết slot: {stats['OUT_OF_SLOTS']}")
                            if stats["AVAILABLE"]:
                                print(f"    -> Có sẵn: {stats['AVAILABLE']}")
                            if stats["NOT_FOUND"]:
                                print(f"    -> Chưa thấy: {stats['NOT_FOUND']}")
                        last_stats_str = stats_str
                        last_print_time = current_time
                        
                    # Cơ chế tự ngắt thông minh khi tất cả lớp đã hoàn thành
                    if wait_for_empty_slot:
                        # Nếu bật chờ slot: dừng khi tất cả lớp mục tiêu đều đã được REGISTERED hoặc NOT_FOUND
                        stop_condition = (len(stats["REGISTERED"]) + len(stats["NOT_FOUND"]) == total_targets)
                    else:
                        # Nếu tắt chờ slot: dừng khi tất cả lớp là REGISTERED, OUT_OF_SLOTS hoặc NOT_FOUND
                        stop_condition = (len(stats["REGISTERED"]) + len(stats["OUT_OF_SLOTS"]) + len(stats["NOT_FOUND"]) == total_targets)

                    if stop_condition:
                        print("\n=================== HOÀN THÀNH QUÉT ===================")
                        print(f"[+] Tất cả lớp học mục tiêu đã được xử lý (Tổng số: {total_targets})")
                        print(f"    - Đã đăng ký thành công: {len(stats['REGISTERED'])} lớp {stats['REGISTERED']}")
                        if stats["OUT_OF_SLOTS"]:
                            print(f"    - Không thể đăng ký (hết slot): {len(stats['OUT_OF_SLOTS'])} lớp {stats['OUT_OF_SLOTS']}")
                        if stats["NOT_FOUND"]:
                            print(f"    - Không tồn tại trên hệ thống: {len(stats['NOT_FOUND'])} lớp {stats['NOT_FOUND']}")
                        print("[+] Chương trình tự động dừng quét và giữ trình duyệt mở.")
                        print("=======================================================")
                        registration_completed = True
                        break
                        
                    found_any_new = False
                    for code in stats["AVAILABLE"]:
                        # Bỏ qua nếu lớp đã được đăng ký thành công
                        if code in previously_registered:
                            continue
                            
                        # Nếu lớp này từng hết slot và bây giờ có sẵn, hiển thị thông báo phát hiện slot trống
                        if code in previously_full:
                            print(f"[+] PHÁT HIỆN: Lớp '{code}' từng hết slot nay đã có chỗ trống!")

                        checkbox = find_checkbox_for_class(page, code)
                        if checkbox:
                            try:
                                if not checkbox.is_checked():
                                    checkbox.check(force=True)
                                    print(f"    [OK] Đã tự động tick chọn: {code}")
                                    found_any_new = True
                            except Exception:
                                try:
                                    checkbox.click(force=True)
                                    print(f"    [OK] Đã tự động click chọn: {code} (click ép buộc)")
                                    found_any_new = True
                                except Exception:
                                    pass
                    
                    if found_any_new and auto_click_submit:
                        print(f"[i] Đã tick chọn lớp mới. Đợi {submit_delay_ms / 1000} giây trước khi tự động gửi đăng ký...")
                        page.wait_for_timeout(submit_delay_ms)
                        print("[i] Đang tiến hành bấm nút xác nhận đăng ký...")
                        if click_submit_button(page):
                            print("[+] Đã gửi đăng ký thành công lên hệ thống!")
                        else:
                            print("[-] Không tìm thấy nút Xác nhận. Vui lòng bấm thủ công trên trình duyệt.")
                            
                    # Tự động tải lại trang (F5) nếu bật chờ slot trống và có lớp bị hết slot
                    # Chỉ thực hiện tải lại trang khi không có lớp nào có sẵn để tick (AVAILABLE)
                    if not stats["AVAILABLE"] and wait_for_empty_slot and stats["OUT_OF_SLOTS"]:
                        current_time = time.time()
                        if current_time - last_reload_time >= current_reload_interval:
                            print(f"[i] Đang tự động tải lại trang (F5) để quét lại slot trống...")
                            print(f"    (Thời gian F5 tiếp theo ngẫu nhiên: {current_reload_interval:.2f}s)")
                            try:
                                page.reload()
                                last_reload_time = current_time
                                current_reload_interval = random.uniform(20.0, 30.0)
                                page.wait_for_timeout(2000)  # Đợi 2 giây sau F5 để trang bắt đầu hiển thị
                            except Exception as e:
                                print(f"[-] Lỗi khi tải lại trang (F5): {e}")

                    page.wait_for_timeout(scan_interval_ms)
            except KeyboardInterrupt:
                print("\n[i] Đã dừng quét liên tục.")

        else:
            # Chế độ Kích hoạt thủ công qua ENTER
            if not args.test:
                print("\n[i] Vui lòng đăng nhập tài khoản và chuyển tới trang đăng ký môn học.")
            
            # Tự động điều hướng trước khi bắt đầu
            ensure_registration_page(page, target_url)
            
            if args.non_interactive:
                print("[i] Chạy ở chế độ không tương tác, tự động bắt đầu quét sau 5 giây...")
                page.wait_for_timeout(5000)
            else:
                input("\n===> NHẤN [ENTER] TẠI ĐÂY ĐỂ BẮT ĐẦU TỰ ĐỘNG CHỌN LỚP <===")
            
            print("\n[i] Bắt đầu quét mã lớp và tick chọn...")
            ticked_count = 0
            
            for code in class_codes:
                code = code.strip()
                if not code:
                    continue
                    
                print(f" -> Đang tìm lớp: {code}...")
                checkbox = find_checkbox_for_class(page, code)
                
                if checkbox:
                    try:
                        is_checked = checkbox.is_checked()
                        if not is_checked:
                            checkbox.check(force=True)
                            print(f"    [OK] Đã tick chọn thành công lớp: {code}")
                        else:
                            print(f"    [OK] Lớp: {code} đã được chọn từ trước")
                        ticked_count += 1
                    except Exception as e:
                        try:
                            checkbox.click(force=True)
                            print(f"    [OK] Đã click chọn thành công lớp: {code} (click ép buộc)")
                            ticked_count += 1
                        except Exception as click_err:
                            print(f"    [-] Lỗi khi tick lớp {code}: {click_err}")
                else:
                    print(f"    [-] KHÔNG tìm thấy mã lớp: {code} trên giao diện trang web.")

            print(f"\n[+] Kết quả: Đã tick thành công {ticked_count}/{len(class_codes)} mã lớp.")

            if ticked_count > 0 and auto_click_submit:
                print(f"[i] Đợi {submit_delay_ms / 1000} giây trước khi tự động bấm nút đăng ký...")
                page.wait_for_timeout(submit_delay_ms)
                print("[i] Đang tự động bấm nút đăng ký...")
                if click_submit_button(page):
                    page.wait_for_timeout(2000)  # Đợi 2 giây để hệ thống xử lý và trang cập nhật
                    for code in class_codes:
                        if get_class_status(page, code) == "REGISTERED":
                            send_desktop_notification("UIT Auto Registration", f"Đăng ký thành công lớp {code}!")

        if args.non_interactive:
            print("\n[i] Đang giữ trình duyệt mở. Hãy theo dõi tiến trình. Đóng cửa sổ Web UI để dừng.")
            try:
                # Giữ trình duyệt mở tối đa 2 tiếng
                for _ in range(7200):
                    page.wait_for_timeout(1000)
            except (KeyboardInterrupt, SystemExit):
                pass
        else:
            print("\n[i] Trình duyệt sẽ mở cho đến khi bạn nhấn ENTER tại cửa sổ Terminal này để đóng.")
            input("===> Nhấn [ENTER] tại đây để ĐÓNG trình duyệt và kết thúc chương trình <===")
        
        browser.close()
        print("[+] Hoàn tất chương trình.")

if __name__ == "__main__":
    main()
