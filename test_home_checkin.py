#!/usr/bin/env python3
import sys
import os
import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import is_in_home_window, get_today_record, is_device_online
import json

def test_home_window_logic():
    """测试下班窗口逻辑"""
    print("=== 测试下班打卡逻辑 ===")
    
    # 加载配置
    with open("data/config.json", "r") as f:
        config = json.load(f)
    
    print(f"下班窗口配置: {config['home_start']} - {config['home_end']}")
    
    # 测试不同时间点
    test_times = [
        ("20:00", "下班窗口前"),
        ("20:50", "下班窗口开始"),
        ("21:30", "下班窗口中"),
        ("23:59", "下班窗口中"),
        ("00:00", "下班窗口中（跨天）"),
        ("00:30", "下班窗口结束"),
        ("01:00", "下班窗口后"),
    ]
    
    for time_str, desc in test_times:
        # 模拟当前时间
        now = datetime.datetime.now()
        test_time = datetime.datetime.strptime(time_str, "%H:%M").time()
        test_datetime = datetime.datetime.combine(now.date(), test_time)
        
        # 如果测试时间在今天但已经过了当前时间，就用昨天
        if test_datetime > now:
            test_datetime = test_datetime - datetime.timedelta(days=1)
        
        # 临时替换datetime.datetime.now
        original_now = datetime.datetime.now
        datetime.datetime.now = lambda: test_datetime
        
        try:
            in_window = is_in_home_window()
            print(f"{time_str} ({desc}): {'在窗口内' if in_window else '不在窗口内'}")
        finally:
            datetime.datetime.now = original_now
    
    # 检查当前状态
    print(f"\n当前实际时间: {datetime.datetime.now().strftime('%H:%M')}")
    print(f"当前是否在下班窗口: {'是' if is_in_home_window() else '否'}")
    
    # 检查设备状态
    online = is_device_online()
    print(f"设备在线状态: {'在线' if online else '离线'}")
    
    # 检查今日记录
    record = get_today_record()
    print(f"今日下班打卡状态: {'已打卡' if record['home_status'] == 1 else '未打卡'}")
    if record['home_time']:
        print(f"下班打卡时间: {record['home_time']}")
    
    # 分析可能的问题
    print(f"\n=== 问题分析 ===")
    if is_in_home_window() and record['home_status'] == 0 and online:
        print("❌ 问题: 在下班窗口内，设备在线，但未打卡")
        print("   可能原因: scan_loop函数可能没有运行或出错")
    elif not is_in_home_window():
        print("ℹ️ 当前不在下班窗口内")
        print(f"   下班窗口: {config['home_start']} - {config['home_end']}")
    elif record['home_status'] == 1:
        print("✅ 今日已打卡下班")
    elif not online:
        print("ℹ️ 设备离线，不触发下班打卡")
    else:
        print("✅ 所有条件正常，等待打卡触发")

if __name__ == "__main__":
    test_home_window_logic()