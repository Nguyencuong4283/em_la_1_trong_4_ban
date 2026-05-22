# 🚀 UIT Class Registration Auto-Ticking Tool

Công cụ tự động tick chọn và xác nhận đăng ký lớp học/môn học tại trường **Đại học Công nghệ Thông tin - ĐHQG-HCM (UIT)**. Công cụ được viết bằng **Python** và **Playwright** giúp bạn tăng tốc độ chọn lớp và tối ưu hóa thời gian đăng ký trong các kỳ dkhp căng thẳng.

---

## ✨ Tính năng nổi bật

*   **Tự động mở trình duyệt Chromium:** Tự động điều hướng trực tiếp đến cổng đăng ký học phần UIT.
*   **Bảo mật & Vượt CAPTCHA:** Cho phép đăng nhập thủ công hoặc tự động. Sau đó bạn có thể tự giải CAPTCHA hoặc xác thực đa yếu tố (MFA) một cách an toàn mà không sợ bị lộ hay chặn.
*   **Quét và tick chọn lớp tự động:** Quét liên tục giao diện web để tìm và tự động tick vào hộp checkbox tương ứng với danh sách mã lớp học đã cấu hình sẵn trong `config.json`.
*   **Tự động bấm Xác nhận đăng ký:** Tự động click nút xác nhận sau khi các lớp học mong muốn đã được tick chọn (có tùy chọn bật/tắt hoặc điều chỉnh thời gian chờ trước khi bấm).
*   **Chế độ Thử nghiệm (Test Mode):** Hỗ trợ giả lập quy trình đăng ký trên trang offline cục bộ (`mock_register.html`) giúp bạn kiểm tra độ tin cậy và cấu hình trước giờ G mà không gây ảnh hưởng đến hệ thống thật.
*   **Giao diện Web UI Dashboard Hiện đại:** Cung cấp trang quản trị Web cục bộ cực đẹp để cấu hình mã lớp trực quan, điều chỉnh tham số, bật/tắt tool và **theo dõi lịch sử log trực tiếp (Real-time Live Logs)** qua Console giả lập.

---

## 📁 Cấu trúc thư mục dự án

```text
uit-registration-tool/
├── config.json            # Tệp cấu hình các tham số chạy tool (mã lớp, url, độ trễ...)
├── register.py            # Script Python chính thực hiện automation (Playwright)
├── web_server.py          # Server FastAPI cung cấp giao diện Web UI Dashboard
├── mock_register.html     # Trang HTML giả lập dùng để chạy thử nghiệm (Test Mode)
├── requirements.txt       # Danh sách thư viện Python cần cài đặt
├── run.sh                 # Script chạy nhanh tự động cho macOS/Linux
├── run.bat                # Script chạy nhanh tự động cho Windows
├── templates/
│   └── index.html         # Giao diện Web Dashboard cực kỳ hiện đại
└── README.md              # Tài liệu hướng dẫn sử dụng (tệp này)
```

---

## ⚡ Khởi chạy nhanh bằng Script (Khuyên dùng)

Để đơn giản hóa quá trình thiết lập và khởi chạy tool, bạn không cần gõ nhiều lệnh. Chỉ cần mở Terminal hoặc CMD tại thư mục dự án và chạy script:

*   **Trên macOS / Linux:**
    ```bash
    ./run.sh
    ```
*   **Trên Windows:** Bấm đúp (double-click) vào tệp `run.bat` hoặc chạy lệnh trong CMD:
    ```cmd
    run.bat
    ```

> [!NOTE]
> Trong **lần đầu tiên chạy**, các script trên sẽ tự động khởi tạo môi trường ảo (`venv`), cài đặt toàn bộ thư viện trong `requirements.txt` và cài đặt nhân trình duyệt Chromium cho Playwright. Từ **các lần sau**, script sẽ trực tiếp kích hoạt môi trường ảo và khởi chạy server Web Dashboard tại địa chỉ **`http://localhost:8000`** một cách nhanh chóng.

---

## 🛠️ Hướng dẫn cài đặt thủ công chi tiết

### 1. Chuẩn bị môi trường Python

Yêu cầu máy tính của bạn đã cài đặt sẵn **Python 3.8** trở lên.


Mở ứng dụng **Terminal** (trên macOS/Linux) hoặc **Command Prompt/PowerShell** (trên Windows) và di chuyển vào thư mục dự án `uit-registration-tool`:

```bash
# Di chuyển vào thư mục dự án (ví dụ)
cd uit-registration-tool
```

#### Bước A: Tạo và kích hoạt môi trường ảo (Virtual Environment)
Việc sử dụng môi trường ảo giúp tránh xung đột thư viện giữa các dự án.

*   **Trên macOS / Linux:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
*   **Trên Windows (PowerShell):**
    ```powershell
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    ```
*   **Trên Windows (CMD):**
    ```cmd
    python -m venv venv
    .\venv\Scripts\activate.bat
    ```

#### Bước B: Cài đặt các thư viện cần thiết
```bash
# Nâng cấp pip lên bản mới nhất
pip install --upgrade pip

# Cài đặt các thư viện từ requirements.txt
pip install -r requirements.txt
```

#### Bước C: Cài đặt nhân duyệt Web Playwright
```bash
# Tải trình duyệt Chromium cho Playwright
playwright install chromium
```

---

## ⚙️ Hướng dẫn cấu hình (`config.json`)

Mở tệp `config.json` bằng một phần mềm soạn thảo văn bản (như VS Code, Notepad, Sublime Text...) để thiết lập thông tin đăng ký của bạn:

```json
{
  "target_url": "https://dkhp.uit.edu.vn",
  "username": "2152xxxx",
  "password": "your_password",
  "class_codes": [
    "ENG02.Q33",
    "MA004.O23",
    "SE104.O21"
  ],
  "headless": false,
  "auto_click_submit": true,
  "scan_interval_ms": 200,
  "submit_delay_ms": 1500
}
```

### Chi tiết các tham số cấu hình:

| Tham số | Ý nghĩa | Khuyên dùng |
| :--- | :--- | :--- |
| `target_url` | Địa chỉ trang đăng ký môn học của trường. | Giữ nguyên `https://dkhp.uit.edu.vn` |
| `username` | Mã số sinh viên (tùy chọn tự điền form đăng nhập). | Nhập MSSV của bạn (hoặc bỏ trống để điền tay) |
| `password` | Mật khẩu tài khoản đăng ký (tùy chọn). | Nhập mật khẩu của bạn (hoặc bỏ trống để điền tay) |
| `class_codes` | Danh sách mảng các mã lớp học bạn muốn đăng ký. | Nhập chính xác mã lớp học (Ví dụ: `["SE104.O21", "MA004.O23"]`) |
| `headless` | Chế độ ẩn trình duyệt. | Luôn đặt `false` để thấy giao diện Chrome tự động tương tác |
| `auto_click_submit` | Tự động bấm nút "Xác nhận đăng ký" sau khi tick thành công. | Đặt `true` nếu muốn tool tự gửi đăng ký; `false` nếu muốn tự kiểm tra lại rồi tự click bằng tay |
| `scan_interval_ms` | Tần suất (khoảng thời gian) quét tìm mã lớp trên trang (ms). | `200` đến `500` ms (tương đương 0.2s - 0.5s quét một lần) |
| `submit_delay_ms` | Thời gian chờ từ lúc tick xong lớp học cuối cùng đến khi bấm nút xác nhận (ms). **Tối thiểu là 1500ms**. | `1500` đến `3000` ms để tránh gửi request quá nhanh hoặc bị lỗi hệ thống |

---

## 🖥️ Cách chạy và sử dụng công cụ

Bạn có thể chạy công cụ này qua **Dòng lệnh (CLI Terminal)** hoặc qua **Giao diện Web Dashboard (Web UI)**.

### Cách 1: Sử dụng qua Giao diện Web UI (Khuyên dùng 👍)

Trang quản trị trực quan giúp bạn dễ dàng theo dõi trạng thái, cấu hình mã lớp trực tiếp và xem log chạy thời gian thực.

1.  Trong Terminal đã kích hoạt môi trường ảo (`venv`), khởi chạy Web Server:
    ```bash
    python3 web_server.py
    ```
2.  Mở trình duyệt web bất kỳ và truy cập địa chỉ: **[http://localhost:8000](http://localhost:8000)**
3.  **Cách sử dụng trên giao diện:**
    *   **Cấu hình thông số:** Nhập MSSV, Mật khẩu, danh sách mã lớp (mỗi lớp 1 dòng) và chỉnh thời gian quét.
    *   Nhấn **Lưu cấu hình** để lưu trữ thiết lập.
    *   Nhấn **Bắt đầu (Chạy thử)** để kiểm tra thử nghiệm trên trang giả lập, hoặc nhấn **Bắt đầu chạy** để mở trang dkhp UIT chính thức.
    *   Theo dõi tiến trình chạy và thông tin phản hồi ngay trong khung **Màn hình Console (Live Log)** ở bên phải.
    *   Nhấn **Dừng lại** bất kỳ lúc nào để đóng trình duyệt tự động và dừng tool.

---

### Cách 2: Sử dụng qua Dòng lệnh Terminal (CLI)

#### Bước A: Kiểm tra và chạy thử nghiệm (Test Mode)
Bạn nên luôn luôn chạy chế độ này trước kỳ đăng ký để đảm bảo Playwright và cấu hình hoạt động trơn tru.

```bash
# macOS/Linux
python3 register.py --test

# Windows
python register.py --test
```
1.  Trình duyệt giả lập Chromium sẽ mở trang `mock_register.html`.
2.  Công cụ sẽ tự động điền tài khoản giả lập và bấm đăng nhập.
3.  Quay lại cửa sổ Terminal, nhấn **[ENTER]** (nếu ở chế độ kích hoạt bằng tay) hoặc tool sẽ tự chạy (nếu bật Auto-pilot).
4.  Bạn sẽ thấy trình duyệt tự động tìm và tick chính xác vào các mã lớp đã cấu hình trong `config.json`, sau đó tự bấm nút đăng ký.

#### Bước B: Chạy thực tế trong kỳ đăng ký chính thức
Khi hệ thống dkhp mở cửa đăng ký:

```bash
# macOS/Linux
python3 register.py

# Windows
python register.py
```
1.  Trình duyệt Chrome mở ra và tải trang `https://dkhp.uit.edu.vn`.
2.  Bạn tiến hành **Đăng nhập bằng tài khoản sinh viên** và hoàn thành captcha (nếu có).
3.  Di chuyển đến trang chọn lớp học chính thức.
4.  Tại màn hình Terminal, chọn chế độ hoạt động:
    *   **Phím `1` (Auto-pilot - Khuyên dùng):** Tool sẽ liên tục quét trang web mỗi `200ms` để tìm mã lớp, tự động tick ngay khi lớp xuất hiện và tự động bấm nút đăng ký.
    *   **Phím `2` (Manual-trigger):** Đợi bạn ổn định trang web, nhấn **[ENTER]** trên Terminal để tool thực hiện quét và tick chọn tất cả lớp học trong danh sách 1 lần duy nhất.

---

## ⚙️ Cơ chế hoạt động chi tiết của công cụ

Công cụ được thiết kế dựa trên sự kết hợp đồng bộ giữa **Bộ tự động hóa trình duyệt (Playwright)** và **Giao diện quản trị Web UI (FastAPI Server)**:

---

### 1. Bộ tự động hóa trình duyệt (Playwright - [register.py](file:///Users/nguyencuong/uit-registration-tool/em_la_1_trong_4_ban/register.py))

#### A. Khởi chạy & Tự động Đăng nhập ([handle_auto_login](file:///Users/nguyencuong/uit-registration-tool/em_la_1_trong_4_ban/register.py#L128-L178))
*   Khi chạy, script khởi động nhân duyệt Chromium ở chế độ hiện giao diện (`"headless": false`) để người dùng có thể trực tiếp giải quyết Cloudflare, CAPTCHA đăng nhập hoặc xác thực đa yếu tố (MFA).
*   Nếu phát hiện biểu mẫu đăng nhập (thông qua sự hiện diện của ô password `input[type='password']`), chương trình sẽ tự động điền `username` (MSSV) và `password` từ cấu hình, sau đó nhấn nút Đăng nhập.

#### B. Định hướng trang đích ([ensure_registration_page](file:///Users/nguyencuong/uit-registration-tool/em_la_1_trong_4_ban/register.py#L280-L324))
*   Nếu trình duyệt chưa di chuyển tới trang chọn lớp, hàm sẽ liên tục quét các phần tử liên kết thẻ `<a>` hoặc nút `<button>` có chứa các từ khóa như *"Đăng ký học phần"*, *"Đăng ký môn học"*, hoặc đường dẫn URL chứa `registration`/`dang-ky` để tự động click điều hướng bạn vào đúng trang đăng ký.

#### C. Thuật toán tìm kiếm Checkbox tương ứng ([find_checkbox_for_class](file:///Users/nguyencuong/uit-registration-tool/em_la_1_trong_4_ban/register.py#L51-L97))
Do cấu trúc bảng đăng ký của UIT phức tạp và checkbox nằm ở cột khác so với văn bản chứa mã lớp:
1.  **Bước 1**: Tool sử dụng Text selectors và XPath để tìm kiếm chính xác phần tử chứa mã lớp (ví dụ: `SE104.O21`).
2.  **Bước 2**: Từ phần tử văn bản đó, tool duyệt ngược cây DOM (DOM Traversal) lên các thẻ cha (ancestor) từ 1 đến 4 cấp (thường là thẻ hàng `<tr>` chứa toàn bộ thông tin môn học).
3.  **Bước 3**: Tại thẻ cha này, tool tìm kiếm phần tử con `<input type="checkbox">` hoặc phần tử có `role="checkbox"`. Đây chính là checkbox của riêng lớp học đó.
4.  **Dự phòng (Fallback)**: Nếu duyệt ngược thất bại, tool tìm kiếm checkbox nằm trong các thẻ anh em (siblings) kế cận thông qua nút cha trực tiếp.

#### D. Đánh giá trạng thái lớp học ([get_class_status](file:///Users/nguyencuong/uit-registration-tool/em_la_1_trong_4_ban/register.py#L208-L249))
Trong mỗi chu kỳ quét, trạng thái từng lớp học mục tiêu được phân loại:
*   `REGISTERED`: Checkbox đã được tick hoặc bị khóa (`disabled`) ở trạng thái đã chọn (đã đăng ký thành công).
*   `OUT_OF_SLOTS`: Checkbox bị khóa (`disabled`) nhưng chưa được chọn, hoặc dòng thông tin lớp học chứa các từ khóa *"hết chỗ"*, *"đầy"*, *"sĩ số đầy"*.
*   `AVAILABLE`: Lớp học có sẵn trên trang, checkbox hoạt động bình thường (`enabled`) và chưa được chọn.
*   `NOT_FOUND`: Mã lớp học chưa xuất hiện trên trang web.

#### E. Cơ chế tự động Tick chọn & Xác nhận ([click_submit_button](file:///Users/nguyencuong/uit-registration-tool/em_la_1_trong_4_ban/register.py#L99-L126))
*   Khi quét thấy lớp ở trạng thái `AVAILABLE`, tool lập tức kích hoạt hành động tick thông qua phương thức `.check(force=True)` hoặc `.click(force=True)`.
*   Sau khi tick lớp học mới, tool đợi một khoảng trễ `submit_delay_ms` (tối thiểu là 1500ms để tránh spam request quá nhanh gây lỗi server) rồi tự động quét tìm nút gửi (ví dụ: `#btn-submit-registration`, nút có chữ *"Xác nhận đăng ký"*) để thực hiện click xác nhận gửi yêu cầu lên hệ thống.
*   **Tự ngắt thông minh**: Vòng lặp quét sẽ tự động kết thúc khi toàn bộ lớp học mục tiêu đạt trạng thái hoàn thành (`REGISTERED` hoặc `OUT_OF_SLOTS`).

---

### 2. Giao diện quản lý Web UI (FastAPI - [web_server.py](file:///Users/nguyencuong/uit-registration-tool/em_la_1_trong_4_ban/web_server.py))

#### A. Quản lý tiến trình ngầm ([start_process](file:///Users/nguyencuong/uit-registration-tool/em_la_1_trong_4_ban/web_server.py#L116-L156))
*   Khi nhấn nút bắt đầu trên Dashboard, FastAPI sẽ gọi `subprocess.Popen` để chạy script `register.py` trong môi trường ảo `venv` ở chế độ Auto-pilot không tương tác (`--mode 1 --non-interactive`).
*   Tiến trình được quản lý tập trung và bảo vệ bằng khóa luồng `threading.Lock` để tránh việc chạy đè nhiều tiến trình trình duyệt cùng một lúc.

#### B. Streaming Live Logs thời gian thực ([get_logs](file:///Users/nguyencuong/uit-registration-tool/em_la_1_trong_4_ban/web_server.py#L177-L198))
*   Một luồng phụ (`threading.Thread`) được khởi tạo để liên tục đọc đầu ra chuẩn `stdout` của tiến trình Playwright và lưu vào danh sách lịch sử log.
*   Server sử dụng cơ chế **Server-Sent Events (SSE)** thông qua FastAPI `StreamingResponse` để truyền tải liên tục dữ liệu log mới về trình duyệt. Client chỉ cần dùng đối tượng `EventSource` để nhận log liên tục và hiển thị lên console giả lập của Web UI mà không cần reload lại trang.

---

## ⚠️ Lưu ý quan trọng để đăng ký thành công

1.  **Về CAPTCHA & Đăng nhập:** Hệ thống đăng ký của UIT thường tích hợp mã CAPTCHA hoặc Cloudflare bảo vệ. Chạy công cụ ở chế độ hiển thị màn hình (`"headless": false`) cho phép bạn tự giải CAPTCHA bằng tay ở bước đăng nhập ban đầu một cách an toàn. Khi đã vào được trang chọn môn học, hãy để tool làm nhiệm vụ tự động quét và tick chọn với tốc độ cao.
2.  **Thông số quét (`scan_interval_ms`):** Không nên đặt tần suất quét quá nhanh (dưới `100ms`) vì có thể gây đơ trình duyệt hoặc bị hệ thống máy chủ UIT chặn tạm thời (rate limit). Khuyến nghị tối ưu nhất là `200ms` đến `500ms`.
3.  **Thử nghiệm trước:** Hãy chắc chắn đã chạy thử chế độ `--test` (hoặc nhấn nút Chạy thử trên Web Dashboard) ít nhất một lần để đảm bảo Playwright Chromium hoạt động ổn định trên hệ điều hành của bạn.
4.  **Bảo mật:** Không chia sẻ tệp `config.json` chứa mật khẩu tài khoản cá nhân của bạn cho người khác.

---

Chúc các bạn UITers đăng ký được đầy đủ các lớp học mong muốn! 🎓🎉
