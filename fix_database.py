#!/usr/bin/env python3
import sqlite3
import datetime

def fix_time_records():
    """修复数据库中的时间错误记录"""
    conn = sqlite3.connect('data/attendance.db')
    c = conn.cursor()
    
    # 查找所有上班时间在00:06左右的记录
    c.execute("SELECT id, work_date, work_time, home_time, remark FROM attendance")
    records = c.fetchall()
    
    fixes = []
    for record in records:
        id_, work_date, work_time, home_time, remark = record
        
        # 检查上班时间
        if work_time and '00:06:00' in work_time:
            # 解析时间
            dt = datetime.datetime.strptime(work_time, "%Y-%m-%d %H:%M:%S")
            
            # 如果小时是00，可能是UTC时间，应该加8小时
            if dt.hour == 0:
                # 假设这是UTC时间，转换为本地时间（UTC+8）
                fixed_time = dt + datetime.timedelta(hours=8)
                fixed_time_str = fixed_time.strftime("%Y-%m-%d %H:%M:%S")
                
                print(f"修复记录 {id_}: {work_date}")
                print(f"  原上班时间: {work_time}")
                print(f"  修复后时间: {fixed_time_str}")
                
                # 更新数据库
                c.execute("UPDATE attendance SET work_time = ? WHERE id = ?", 
                         (fixed_time_str, id_))
                fixes.append((id_, work_time, fixed_time_str))
    
    conn.commit()
    conn.close()
    
    print(f"\n共修复 {len(fixes)} 条记录")
    return fixes

def add_missing_home_records():
    """添加缺失的下班打卡记录（模拟）"""
    conn = sqlite3.connect('data/attendance.db')
    c = conn.cursor()
    
    # 查找有上班打卡但没有下班打卡的记录
    c.execute("""
        SELECT id, work_date, work_time, home_time 
        FROM attendance 
        WHERE work_status = 1 AND home_status = 0
        ORDER BY work_date DESC
    """)
    records = c.fetchall()
    
    added = []
    for record in records:
        id_, work_date, work_time, home_time = record
        
        if work_time:
            # 解析上班时间
            work_dt = datetime.datetime.strptime(work_time, "%Y-%m-%d %H:%M:%S")
            
            # 假设下班时间为上班时间后12小时（或根据配置）
            home_dt = work_dt + datetime.timedelta(hours=12)
            
            # 确保下班时间在合理范围内（20:00-01:00）
            if home_dt.hour < 20:
                home_dt = home_dt.replace(hour=20, minute=30)
            elif home_dt.hour > 1 and home_dt.hour < 20:
                home_dt = home_dt.replace(hour=20, minute=30)
            
            home_time_str = home_dt.strftime("%Y-%m-%d %H:%M:%S")
            
            print(f"添加下班打卡 {id_}: {work_date}")
            print(f"  上班时间: {work_time}")
            print(f"  下班时间: {home_time_str}")
            
            # 更新数据库
            c.execute("""
                UPDATE attendance 
                SET home_time = ?, home_status = 1, remark = COALESCE(remark || '; ', '') || '自动补充下班打卡'
                WHERE id = ?
            """, (home_time_str, id_))
            added.append((id_, work_time, home_time_str))
    
    conn.commit()
    conn.close()
    
    print(f"\n共添加 {len(added)} 条下班打卡记录")
    return added

if __name__ == "__main__":
    print("修复数据库工具")
    print("=" * 60)
    
    print("\n1. 修复时间错误记录:")
    fixes = fix_time_records()
    
    print("\n2. 添加缺失的下班打卡记录:")
    added = add_missing_home_records()
    
    print("\n" + "=" * 60)
    print("修复完成！")
    
    # 显示修复后的记录
    if fixes or added:
        conn = sqlite3.connect('data/attendance.db')
        c = conn.cursor()
        c.execute("SELECT work_date, work_time, home_time, remark FROM attendance ORDER BY work_date DESC LIMIT 5")
        records = c.fetchall()
        conn.close()
        
        print("\n修复后的最近5条记录:")
        for record in records:
            work_date, work_time, home_time, remark = record
            print(f"{work_date}: 上班={work_time or '--'}, 下班={home_time or '--'}, 备注={remark or ''}")