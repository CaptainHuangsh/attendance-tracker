#!/usr/bin/env python3
import sys
import os
import datetime
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import is_in_home_window, get_work_date, get_today_record, is_device_online, is_in_work_window

def test_time_fix():
    """测试时间修复"""
    print("=== 测试时间修复 ===")
    
    # 测试前端时间格式修复
    test_cases = [
        ("2026-03-19T08:06", "2026-03-19 08:06:00"),
        ("2026-03-19T20:50", "2026-03-19 20:50:00"),
        ("2026-03-20T00:10", "2026-03-20 00:10:00"),
    ]
    
    for input_str, expected in test_cases:
        # 模拟前端修复后的处理
        if 'T' in input_str:
            date_part, time_part = input_str.split('T')
            year, month, day = date_part.split('-')
            hours, minutes = time_part.split(':')
            result = f"{year}-{month}-{day} {hours}:{minutes}:00"
        else:
            result = input_str + ":00"
        
        print(f"输入: {input_str}")
        print(f"期望: {expected}")
        print(f"结果: {result}")
        print(f"匹配: {'✓' if result == expected else '✗'}")
        print()

def test_home_window_logic():
    """测试下班窗口逻辑"""
    print("=== 测试下班窗口逻辑 ===")
    
    # 加载配置
    with open("data/config.json", "r") as f:
        config = json.load(f)
    
    print(f"下班窗口: {config['home_start']} - {config['home_end']}")
    
    # 测试不同时间点
    test_times = [
        ("20:49", False, "下班窗口前"),
        ("20:50", True, "下班窗口开始"),
        ("21:30", True, "下班窗口中"),
        ("23:59", True, "下班窗口中"),
        ("00:00", True, "下班窗口中（跨天）"),
        ("00:30", True, "下班窗口结束"),
        ("00:31", False, "下班窗口后"),
    ]
    
    for time_str, expected, desc in test_times:
        # 模拟当前时间
        now = datetime.datetime.now()
        test_time = datetime.datetime.strptime(time_str, "%H:%M").time()
        test_datetime = datetime.datetime.combine(now.date(), test_time)
        
        # 如果测试时间在今天但已经过了当前时间，就用昨天
        if test_datetime > now:
            test_datetime = test_datetime - datetime.timedelta(days=1)
        
        # 临时替换datetime.datetime.now
        import main
        original_now = datetime.datetime.now
        datetime.datetime.now = lambda: test_datetime
        main.datetime.datetime.now = lambda: test_datetime
        
        try:
            in_window = is_in_home_window()
            work_date = get_work_date()
            status = "✓" if in_window == expected else "✗"
            print(f"{time_str} ({desc}): {'在窗口内' if in_window else '不在窗口内'} | 工作日期: {work_date} {status}")
        finally:
            datetime.datetime.now = original_now
            main.datetime.datetime.now = original_now
    
    print()

def test_work_date_logic():
    """测试工作日期逻辑"""
    print("=== 测试工作日期逻辑 ===")
    
    test_cases = [
        ("2026-03-19 23:59", "2026-03-19"),
        ("2026-03-20 00:00", "2026-03-19"),  # 00:00~00:30 归属前一天
        ("2026-03-20 00:15", "2026-03-19"),  # 00:00~00:30 归属前一天
        ("2026-03-20 00:30", "2026-03-19"),  # 00:00~00:30 归属前一天
        ("2026-03-20 00:31", "2026-03-20"),  # 00:31 之后归属当天
        ("2026-03-20 08:00", "2026-03-20"),
    ]
    
    for time_str, expected in test_cases:
        test_datetime = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M")
        
        # 临时替换datetime.datetime.now
        import main
        original_now = datetime.datetime.now
        datetime.datetime.now = lambda: test_datetime
        main.datetime.datetime.now = lambda: test_datetime
        
        try:
            work_date = get_work_date()
            status = "✓" if work_date == expected else "✗"
            print(f"{time_str} -> {work_date} {status}")
        finally:
            datetime.datetime.now = original_now
            main.datetime.datetime.now = original_now
    
    print()

def test_current_status():
    """测试当前状态"""
    print("=== 测试当前状态 ===")
    
    print(f"当前时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"工作日期: {get_work_date()}")
    print(f"在上班窗口: {'是' if is_in_work_window() else '否'}")
    print(f"在下班窗口: {'是' if is_in_home_window() else '否'}")
    
    record = get_today_record()
    print(f"今日记录: 上班状态={record['work_status']}, 下班状态={record['home_status']}")
    
    online = is_device_online()
    print(f"设备在线: {'是' if online else '否'}")
    
    # 分析
    print(f"\n=== 分析 ===")
    if is_in_home_window() and record['home_status'] == 0 and online:
        print("状态: 应该触发下班打卡但未触发")
        print("可能原因: scan_loop可能没有运行或出错")
    elif is_in_home_window() and record['home_status'] == 0 and not online:
        print("状态: 在下班窗口但设备离线")
        print("动作: 设备上线后将自动打卡")
    elif is_in_home_window() and record['home_status'] == 1:
        print("状态: 今日已下班打卡")
    elif not is_in_home_window():
        print("状态: 不在下班窗口")
    else:
        print("状态: 正常")

if __name__ == "__main__":
    print("牛马打工人最终修复测试")
    print("=" * 60)
    
    try:
        test_time_fix()
        test_home_window_logic()
        test_work_date_logic()
        test_current_status()
        
        print("=" * 60)
        print("所有测试完成！")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)