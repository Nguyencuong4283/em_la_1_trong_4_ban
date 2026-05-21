import os
import sys

def ensure_venv():
    # Kiểm tra xem có đang chạy trong venv không
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
import asyncio
import subprocess
import threading
from typing import List
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(title="Tứ kỵ sỹ khải huyền")

# Global process tracking
process_lock = threading.Lock()
current_process = None
log_history = []

# Config JSON path
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

class ConfigSchema(BaseModel):
    target_url: str
    username: str
    password: str
    class_codes: List[str]
    headless: bool
    auto_click_submit: bool
    scan_interval_ms: int
    submit_delay_ms: int

def load_config_data():
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
    if not os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
        except Exception:
            pass
        return default_config
        
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default_config


def save_config_data(data: dict):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def read_stdout(proc):
    global log_history
    try:
        for line in proc.stdout:
            log_history.append(line)
        proc.wait()
    except Exception as e:
        log_history.append(f"[web_error] Lỗi đọc log: {e}\n")
    log_history.append(f"\n[web] >>> Tiến trình kết thúc (Exit Code: {proc.returncode}) <<<\n")

@app.get("/", response_class=HTMLResponse)
def read_root():
    template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates", "index.html")
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Không tìm thấy index.html. Vui lòng kiểm tra thư mục templates/</h1>", status_code=404)

@app.get("/api/config")
def get_config():
    return load_config_data()

@app.post("/api/config")
def update_config(config: ConfigSchema):
    try:
        save_config_data(config.model_dump())
        return {"status": "success", "message": "Đã lưu cấu hình thành công!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lưu cấu hình: {str(e)}")

@app.get("/api/status")
def get_status():
    global current_process
    with process_lock:
        is_running = current_process is not None and current_process.poll() is None
    return {"running": is_running}

@app.post("/api/start")
def start_process(params: dict = None):
    global current_process, log_history
    test_mode = False
    if params and params.get("test"):
        test_mode = True

    with process_lock:
        if current_process is not None and current_process.poll() is None:
            return {"status": "error", "message": "Công cụ đăng ký đang chạy rồi!"}
        
        log_history.clear()
        log_history.append(f"[web] Đang khởi động Playwright Browser ({'Chế độ THỬ NGHIỆM' if test_mode else 'Chế độ THẬT'})...\n")
        
        # Đường dẫn python của venv
        venv_python = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv", "bin", "python3")
        if not os.path.exists(venv_python):
            venv_python = "python3" # fallback
            
        cmd = [venv_python, "-u", "register.py", "--mode", "1", "--non-interactive"]
        if test_mode:
            cmd.append("--test")
            
        try:
            current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE,
                text=True,
                bufsize=1,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            
            # Khởi chạy luồng đọc log
            threading.Thread(target=read_stdout, args=(current_process,), daemon=True).start()
            return {"status": "success", "message": "Đã kích hoạt công cụ đăng ký!"}
        except Exception as e:
            log_history.append(f"[web_error] Không thể chạy script register.py: {e}\n")
            raise HTTPException(status_code=500, detail=f"Lỗi khởi động tiến trình: {str(e)}")

@app.post("/api/stop")
def stop_process():
    global current_process
    with process_lock:
        if current_process is None or current_process.poll() is not None:
            return {"status": "error", "message": "Công cụ đăng ký hiện không hoạt động."}
        
        try:
            current_process.terminate()
            current_process.wait(timeout=2)
            log_history.append("[web] >>> Đã dừng tiến trình theo yêu cầu từ Web UI. <<<\n")
            return {"status": "success", "message": "Đã dừng công cụ thành công."}
        except Exception as e:
            try:
                current_process.kill()
                log_history.append("[web] >>> Đã cưỡng chế dừng tiến trình (SIGKILL). <<<\n")
                return {"status": "success", "message": "Đã cưỡng chế dừng công cụ thành công."}
            except Exception as kill_err:
                raise HTTPException(status_code=500, detail=f"Không thể tắt tiến trình: {str(kill_err)}")

@app.get("/api/logs")
async def get_logs(request: Request):
    async def log_generator():
        global log_history
        last_index = 0
        
        # Gửi toàn bộ lịch sử log trước
        while last_index < len(log_history):
            yield f"data: {json.dumps({'log': log_history[last_index]})}\n\n"
            last_index += 1
            
        while True:
            if await request.is_disconnected():
                break
                
            if last_index < len(log_history):
                yield f"data: {json.dumps({'log': log_history[last_index]})}\n\n"
                last_index += 1
            else:
                await asyncio.sleep(0.1)
                
@app.get("/api/update-check")
def check_updates():
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
                return {
                    "has_update": True,
                    "local_version": local_version,
                    "remote_version": remote_version
                }
    except Exception:
        pass
        
    return {
        "has_update": False,
        "local_version": local_version,
        "remote_version": local_version
    }

if __name__ == "__main__":
    import uvicorn
    # Mặc định chạy ở port 8000
    uvicorn.run("web_server:app", host="127.0.0.1", port=8000, reload=True)
