#!/usr/bin/env python3
import datetime

# 模拟前端JavaScript的时间处理
def simulate_frontend_bug():
    print("=== 模拟前端时间处理Bug ===")
    
    # 用户选择 2026-03-19 08:06
    date_str = "2026-03-19"
    time_str = "08:06"
    
    # 前端JavaScript代码（有bug的版本）
    print(f"用户选择: {date_str} {time_str}")
    
    # 错误的做法：使用toISOString()
    # 在JavaScript中：
    # const dt = new Date('2026-03-19T08:06:00');
    # const isoString = dt.toISOString(); // 转换为UTC: 2026-03-19T00:06:00.000Z
    
    # 正确的做法：手动拼接本地时间
    # const year = dt.getFullYear();
    # const month = String(dt.getMonth() + 1).padStart(2, '0');
    # const day = String(dt.getDate()).padStart(2, '0');
    # const hours = String(dt.getHours()).padStart(2, '0');
    # const minutes = String(dt.getMinutes()).padStart(2, '0');
    # const formattedTime = `${year}-${month}-${day} ${hours}:${minutes}:00`;
    
    # 模拟错误情况
    dt_local = datetime.datetime(2026, 3, 19, 8, 6, 0)
    dt_utc = dt_local.astimezone(datetime.timezone.utc)
    iso_wrong = dt_utc.isoformat().replace('+00:00', 'Z').split('.')[0]
    print(f"错误 (toISOString): {iso_wrong}")  # 2026-03-19T00:06:00Z
    
    # 模拟正确情况
    correct_format = f"2026-03-19 08:06:00"
    print(f"正确 (手动拼接): {correct_format}")
    
    return correct_format

def test_backend_storage():
    print("\n=== 测试后端存储 ===")
    
    # 模拟后端接收的时间字符串
    time_strings = [
        "2026-03-19 08:06:00",  # 正确格式
        "2026-03-19T00:06:00",  # UTC格式（错误）
        "2026-03-19 00:06:00",  # 错误的本地时间
    ]
    
    for ts in time_strings:
        print(f"时间字符串: {ts}")
        try:
            # 后端解析
            if 'T' in ts:
                dt = datetime.datetime.fromisoformat(ts.replace('Z', '+00:00'))
            else:
                dt = datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
            print(f"  解析为: {dt}")
            print(f"  存储到数据库: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception as e:
            print(f"  解析错误: {e}")

def check_database_records():
    print("\n=== 检查数据库记录 ===")
    
    import sqlite3
    conn = sqlite3.connect('data/attendance.db')
    c = conn.cursor()
    c.execute('SELECT work_date, work_time, home_time FROM attendance ORDER BY work_date DESC LIMIT 5')
    rows = c.fetchall()
    conn.close()
    
    for row in rows:
        work_date, work_time, home_time = row
        print(f"日期: {work_date}")
        if work_time:
            # 检查时间是否正确
            dt = datetime.datetime.strptime(work_time, "%Y-%m-%d %H:%M:%S")
            hour = dt.hour
            if hour < 7 or hour > 9:  # 上班时间应该在7-9点之间
                print(f"  上班时间异常: {work_time} (小时: {hour})")
            else:
                print(f"  上班时间正常: {work_time}")
        if home_time:
            dt = datetime.datetime.strptime(home_time, "%Y-%m-%d %H:%M:%S")
            hour = dt.hour
            if hour >= 20 or hour <= 1:  # 下班时间应该在20-1点之间
                print(f"  下班时间正常: {home_time}")
            else:
                print(f"  下班时间异常: {home_time} (小时: {hour})")

if __name__ == "__main__":
    simulate_frontend_bug()
    test_backend_storage()
    check_database_records()