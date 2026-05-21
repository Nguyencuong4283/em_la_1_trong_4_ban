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
from playwright.sync_api import sync_playwright

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
        "submit_delay_ms": 1500
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
                
                # Đi lên các phần tử cha để tìm checkbox cùng hàng (tr) hoặc cùng nhóm
                for depth in range(1, 5):
                    ancestor = element.locator(f"xpath=./ancestor::*[position()={depth}]")
                    if ancestor.count() > 0:
                        checkbox = ancestor.locator("input[type='checkbox']")
                        if checkbox.count() > 0:
                            return checkbox.first
                        
                        checkbox_role = ancestor.locator("[role='checkbox']")
                        if checkbox_role.count() > 0:
                            return checkbox_role.first
                            
                # Thử tìm thẻ input/checkbox là anh em (sibling)
                parent = element.locator("xpath=..")
                if parent.count() > 0:
                    checkbox = parent.locator("input[type='checkbox']")
                    if checkbox.count() > 0:
                        return checkbox.first
                    
                    grandparent = parent.locator("xpath=..")
                    if grandparent.count() > 0:
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
            if any(kw in row_text_lower for kw in ["hết chỗ", "hết slot", "đầy", "sĩ số đầy", "hết hạn"]):
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
    submit_delay_ms = config.get("submit_delay_ms", 5000)

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
            print(f"[i] Chương trình đang quét tìm các lớp học mỗi {scan_interval_ms}ms...")
            if not args.non_interactive:
                print("[i] Nhấn Ctrl+C trong Terminal để tắt chương trình.")
            
            total_targets = len(class_codes)
            last_stats_str = ""
            last_print_time = 0
            
            try:
                while True:
                    # Kiểm tra xem có cần tự động đăng nhập lại không (đề phòng phiên đăng nhập hết hạn)
                    if username and password:
                        handle_auto_login(page, username, password)
                        
                    # Tự động điều hướng sang trang đăng ký học phần nếu cần
                    ensure_registration_page(page, target_url)
                    
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
                        
                    # Cơ chế tự ngắt thông minh khi tất cả lớp đã hoàn thành (đăng ký thành công hoặc hết slot)
                    if len(stats["REGISTERED"]) + len(stats["OUT_OF_SLOTS"]) == total_targets:
                        print("\n=================== HOÀN THÀNH QUÉT ===================")
                        print(f"[+] Tất cả lớp học mục tiêu đã được xử lý (Tổng số: {total_targets})")
                        print(f"    - Đã đăng ký thành công: {len(stats['REGISTERED'])} lớp {stats['REGISTERED']}")
                        if stats["OUT_OF_SLOTS"]:
                            print(f"    - Không thể đăng ký (hết slot): {len(stats['OUT_OF_SLOTS'])} lớp {stats['OUT_OF_SLOTS']}")
                        print("[+] Chương trình tự động dừng và đóng trình duyệt.")
                        print("=======================================================")
                        registration_completed = True
                        break
                        
                    found_any_new = False
                    for code in stats["AVAILABLE"]:
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
                click_submit_button(page)

        if args.non_interactive:
            if not registration_completed:
                print("\n[i] Đang giữ trình duyệt mở. Hãy theo dõi tiến trình. Đóng cửa sổ Web UI để dừng.")
                try:
                    # Giữ trình duyệt mở tối đa 2 tiếng
                    for _ in range(7200):
                        page.wait_for_timeout(1000)
                except (KeyboardInterrupt, SystemExit):
                    pass
        else:
            if not registration_completed:
                print("\n[i] Trình duyệt sẽ mở cho đến khi bạn nhấn ENTER tại cửa sổ Terminal này để đóng.")
                input("===> Nhấn [ENTER] tại đây để ĐÓNG trình duyệt và kết thúc chương trình <===")
        
        browser.close()
        print("[+] Hoàn tất chương trình.")

if __name__ == "__main__":
    main()
