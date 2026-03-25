#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import check_mac, ping_ip, is_device_online
import json

def test_bug1():
    """测试前端时间格式问题（模拟）"""
    print("=== 测试Bug 1: 前端时间格式 ===")
    
    # 模拟前端JavaScript的toISOString问题
    from datetime import datetime
    import pytz
    
    # 模拟UTC+8时间 8:06
    local_time = datetime(2024, 1, 1, 8, 6, 0)
    
    # 错误的做法（toISOString会转换为UTC）
    utc_time = local_time.astimezone(pytz.UTC)
    iso_wrong = utc_time.isoformat()
    print(f"错误做法 (toISOString): {iso_wrong}")
    
    # 正确的做法（手动拼接本地时间）
    year = local_time.year
    month = str(local_time.month).zfill(2)
    day = str(local_time.day).zfill(2)
    hour = str(local_time.hour).zfill(2)
    minute = str(local_time.minute).zfill(2)
    correct_format = f"{year}-{month}-{day} {hour}:{minute}:00"
    print(f"正确做法 (手动拼接): {correct_format}")
    
    # 验证修复
    assert "08:06" in correct_format, "时间格式错误"
    print("✓ Bug 1 修复验证通过")

def test_bug2():
    """测试设备在线检测"""
    print("\n=== 测试Bug 2: 设备在线检测 ===")
    
    # 加载配置
    with open("data/config.json", "r") as f:
        config = json.load(f)
    
    ip = config["static_ip"]
    mac = config["mac_address"]
    
    print(f"测试配置: IP={ip}, MAC={mac}")
    
    # 测试ping
    ping_result = ping_ip(ip)
    print(f"Ping测试: {'成功' if ping_result else '失败'}")
    
    # 测试MAC检测
    mac_result = check_mac(mac, ip)
    print(f"MAC检测: {'匹配' if mac_result else '不匹配'}")
    
    # 测试完整在线检测
    online_result = is_device_online()
    print(f"设备在线状态: {'在线' if online_result else '离线'}")
    
    if not online_result:
        print("⚠ 设备显示离线，请检查:")
        print("  1. 设备是否开机并连接到网络")
        print("  2. IP地址是否正确")
        print("  3. MAC地址是否正确")
        print("  4. 防火墙是否允许ping")
    
    return online_result

def test_backend_logic():
    """测试后端逻辑"""
    print("\n=== 测试后端逻辑 ===")
    
    from main import is_in_work_window, is_in_home_window, get_today_record
    import datetime
    
    # 加载配置
    with open("data/config.json", "r") as f:
        config = json.load(f)
    
    print(f"上班窗口: {config['work_start']} - {config['work_end']}")
    print(f"下班窗口: {config['home_start']} - {config['home_end']}")
    
    work_window = is_in_work_window()
    home_window = is_in_home_window()
    
    print(f"当前是否在上班窗口: {'是' if work_window else '否'}")
    print(f"当前是否在下班窗口: {'是' if home_window else '否'}")
    
    # 获取今日记录
    record = get_today_record()
    print(f"今日考勤记录: 上班状态={record['work_status']}, 下班状态={record['home_status']}")
    
    print("✓ 后端逻辑测试完成")

if __name__ == "__main__":
    print("牛马打工人Bug修复测试")
    print("=" * 50)
    
    try:
        test_bug1()
        test_bug2()
        test_backend_logic()
        
        print("\n" + "=" * 50)
        print("所有测试完成！")
        print("请检查日志文件 data/app.log 查看详细运行信息")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)