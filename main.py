import os
import json
import time
import datetime
import logging
import logging.handlers
import subprocess
import csv
from io import StringIO
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
import sqlite3
from contextlib import asynccontextmanager

# 数据库路径
DB_PATH = "data/attendance.db"
CONFIG_PATH = "data/config.json"
LOG_PATH = "data/app.log"

# 默认配置
DEFAULT_CONFIG = {
    "mac_address": "64:BD:6D:B3:79:32",
    "static_ip": "192.168.1.16",
    "work_start": "07:40",
    "work_end": "08:40",
    "home_start": "20:50",
    "home_end": "00:30",
    "scan_interval": 60,
    "work_lost_count": 2,
    "workdays": [0, 1, 2, 3, 4]
}

# 初始化数据库
def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 考勤表
    c.execute('''CREATE TABLE IF NOT EXISTS attendance
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  work_date DATE UNIQUE NOT NULL,
                  work_time DATETIME,
                  home_time DATETIME,
                  work_status INTEGER DEFAULT 0,
                  home_status INTEGER DEFAULT 0,
                  remark TEXT,
                  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                  update_time DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    # 配置表
    c.execute('''CREATE TABLE IF NOT EXISTS system_config
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  config_key VARCHAR(50) UNIQUE NOT NULL,
                  config_value TEXT NOT NULL,
                  update_time DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    conn.commit()
    conn.close()
    
    # 初始化配置文件
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'w') as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)

# 加载配置
def load_config():
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

# 保存配置
def save_config(config):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)

# Ping IP检测
def ping_ip(ip: str) -> bool:
    try:
        output = subprocess.run(
            ["ping", "-c", "1", "-W", "2", ip],
            capture_output=True,
            text=True
        )
        return output.returncode == 0
    except:
        return False

# MAC地址检测
def check_mac(mac: str, ip: str) -> bool:
    try:
        # 尝试ARP查询
        output = subprocess.run(
            ["arp", "-n", ip],
            capture_output=True,
            text=True
        )
        if mac.lower() in output.stdout.lower():
            return True
        
        # 尝试扫描邻居表
        output = subprocess.run(
            ["ip", "neigh"],
            capture_output=True,
            text=True
        )
        return mac.lower() in output.stdout.lower()
    except:
        return False

# 双校验设备是否在线
def is_device_online() -> bool:
    config = load_config()
    if not config["static_ip"] or not config["mac_address"]:
        return False
    
    ip_ok = ping_ip(config["static_ip"])
    mac_ok = check_mac(config["mac_address"], config["static_ip"])
    return ip_ok or mac_ok

# 判断是否为工作日（排除周末，后续可扩展法定节假日）
def is_workday() -> bool:
    now = datetime.datetime.now()
    # 0=周一，4=周五，5=周六，6=周日
    if now.weekday() >= 5:
        return False
    # 法定节假日判断可在此处扩展
    return True

# 获取今天的日期（处理跨天情况）
def get_work_date() -> str:
    now = datetime.datetime.now()
    # 00:00~00:30 归属前一天
    if now.hour == 0 and now.minute <= 30:
        return (now - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    return now.strftime("%Y-%m-%d")

# 检查是否在上班检测窗口
def is_in_work_window() -> bool:
    config = load_config()
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M")
    
    work_start = datetime.datetime.strptime(config["work_start"], "%H:%M").time()
    work_end = datetime.datetime.strptime(config["work_end"], "%H:%M").time()
    current = now.time()
    
    return work_start <= current <= work_end

# 检查是否在下班检测窗口
def is_in_home_window() -> bool:
    config = load_config()
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M")
    
    home_start = datetime.datetime.strptime(config["home_start"], "%H:%M").time()
    home_end = datetime.datetime.strptime(config["home_end"], "%H:%M").time()
    current = now.time()
    
    # 处理跨天情况（比如20:50到次日00:30）
    if home_start < home_end:
        return home_start <= current <= home_end
    else:
        return current >= home_start or current <= home_end

# 获取当天考勤记录
def get_today_record():
    work_date = get_work_date()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM attendance WHERE work_date = ?", (work_date,))
    record = c.fetchone()
    conn.close()
    
    if not record:
        # 创建新记录
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO attendance (work_date) VALUES (?)", (work_date,))
        conn.commit()
        conn.close()
        return get_today_record()
    
    return {
        "id": record[0],
        "work_date": record[1],
        "work_time": record[2],
        "home_time": record[3],
        "work_status": record[4],
        "home_status": record[5],
        "remark": record[6]
    }

# 更新上班记录
def update_work_time():
    record = get_today_record()
    if record["work_status"] == 1:
        return  # 已经记录过了
    
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""UPDATE attendance 
                 SET work_time = ?, work_status = 1, update_time = CURRENT_TIMESTAMP
                 WHERE work_date = ?""", (now, get_work_date()))
    conn.commit()
    conn.close()

# 更新下班记录
def update_home_time():
    record = get_today_record()
    if record["home_status"] == 1:
        return  # 已经记录过了
    
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""UPDATE attendance 
                 SET home_time = ?, home_status = 1, update_time = CURRENT_TIMESTAMP
                 WHERE work_date = ?""", (now, get_work_date()))
    conn.commit()
    conn.close()

# 后台扫描任务
def scan_loop():
    config = load_config()
    
    while True:
        try:
            # 周末/节假日不检测
            if not is_workday():
                time.sleep(config["scan_interval"])
                continue
                
            config = load_config()
            today_record = get_today_record()
            work_lost_counter = 0
            
            # 上班检测逻辑：如果已经打卡，跳过计数
            if is_in_work_window() and today_record["work_status"] == 0:
                online = is_device_online()
                if not online:
                    work_lost_counter += 1
                    if work_lost_counter >= config["work_lost_count"]:
                        update_work_time()
                # 无需重置，每次循环都重新开始计数，避免重启服务漏检
            
            # 下班检测逻辑
            if is_in_home_window() and today_record["home_status"] == 0:
                online = is_device_online()
                if online:
                    update_home_time()
            
            time.sleep(config["scan_interval"])
        except Exception as e:
            print(f"Scan error: {e}")
            time.sleep(10)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 初始化
    init_db()
    
    # 启动后台扫描线程
    import threading
    scan_thread = threading.Thread(target=scan_loop, daemon=True)
    scan_thread.start()
    
    yield
    # 关闭时的清理（无）

app = FastAPI(lifespan=lifespan)

# 配置模型
class Config(BaseModel):
    mac_address: str
    static_ip: str
    work_start: str
    work_end: str
    home_start: str
    home_end: str
    scan_interval: int
    work_lost_count: int

# API接口
@app.get("/api/config")
def get_config():
    return load_config()

@app.post("/api/config")
def update_config(config: Config):
    save_config(config.dict())
    return {"status": "success"}

@app.get("/api/attendance")
def get_attendance(limit: int = 30):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""SELECT * FROM attendance 
                 ORDER BY work_date DESC 
                 LIMIT ?""", (limit,))
    records = c.fetchall()
    conn.close()
    
    result = []
    for record in records:
        result.append({
            "id": record[0],
            "work_date": record[1],
            "work_time": record[2],
            "home_time": record[3],
            "work_status": record[4],
            "home_status": record[5],
            "remark": record[6]
        })
    return result

@app.get("/api/status")
def get_status():
    return {
        "device_online": is_device_online(),
        "in_work_window": is_in_work_window(),
        "in_home_window": is_in_home_window(),
        "today_record": get_today_record()
    }

# 前端页面
@app.get("/", response_class=HTMLResponse)
def index():
    with open("static/index.html", "r") as f:
        return f.read()

# 静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
