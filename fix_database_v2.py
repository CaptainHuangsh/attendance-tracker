#!/usr/bin/env python3
import sqlite3
import datetime

def fix_time_records_correctly():
    """正确修复数据库中的时间错误记录"""
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
            # 但日期可能也需要调整
            if dt.hour == 0:
                # 保存原始日期
                original_date = datetime.datetime.strptime(work_date, "%Y-%m-%d")
                
                # 加8小时
                fixed_dt = dt + datetime.timedelta(hours=8)
                
                # 检查日期是否应该调整
                # 如果fixed_dt的日期与work_date不同，但小时是08，那么日期应该是work_date
                if fixed_dt.date() != original_date.date() and fixed_dt.hour == 8:
                    # 日期应该保持为work_date，只调整时间
                    fixed_dt = datetime.datetime.combine(original_date.date(), 
                                                         datetime.time(fixed_dt.hour, fixed_dt.minute, fixed_dt.second))
                
                fixed_time_str = fixed_dt.strftime("%Y-%m-%d %H:%M:%S")
                
                print(f"修复记录 {id_}: {work_date}")
                print(f"  原上班时间: {work_time}")
                print(f"  修复后时间: {fixed_time_str}")
                
                # 更新数据库
                c.execute("UPDATE attendance SET work_time = ? WHERE id = ?", 
                         (fixed_time_str, id_))
                fixes.append((id_, work_time, fixed_time_str))
    
    conn.commit()
    
    # 现在修复日期不匹配的问题
    c.execute("SELECT id, work_date, work_time FROM attendance WHERE work_time IS NOT NULL")
    records = c.fetchall()
    
    date_fixes = []
    for record in records:
        id_, work_date, work_time = record
        dt = datetime.datetime.strptime(work_time, "%Y-%m-%d %H:%M:%S")
        
        # 如果上班时间的日期与work_date不匹配
        if dt.date().isoformat() != work_date:
            # 调整时间为work_date的日期
            corrected_dt = datetime.datetime.combine(
                datetime.datetime.strptime(work_date, "%Y-%m-%d").date(),
                dt.time()
            )
            corrected_time_str = corrected_dt.strftime("%Y-%m-%d %H:%M:%S")
            
            print(f"修正日期不匹配 {id_}: {work_date}")
            print(f"  原时间: {work_time}")
            print(f"  修正后: {corrected_time_str}")
            
            c.execute("UPDATE attendance SET work_time = ? WHERE id = ?", 
                     (corrected_time_str, id_))
            date_fixes.append((id_, work_time, corrected_time_str))
    
    conn.commit()
    conn.close()
    
    print(f"\n共修复 {len(fixes)} 条时间记录")
    print(f"共修正 {len(date_fixes)} 条日期不匹配记录")
    return fixes + date_fixes

if __name__ == "__main__":
    print("正确修复数据库工具")
    print("=" * 60)
    
    fixes = fix_time_records_correctly()
    
    print("\n" + "=" * 60)
    print("修复完成！")
    
    # 显示修复后的记录
    if fixes:
        conn = sqlite3.connect('data/attendance.db')
        c = conn.cursor()
        c.execute("SELECT work_date, work_time, home_time, remark FROM attendance ORDER BY work_date DESC LIMIT 10")
        records = c.fetchall()
        conn.close()
        
        print("\n修复后的最近10条记录:")
        for record in records:
            work_date, work_time, home_time, remark = record
            print(f"{work_date}: 上班={work_time or '--'}, 下班={home_time or '--'}, 备注={remark or ''}")