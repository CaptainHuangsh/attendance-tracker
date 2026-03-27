#!/usr/bin/env python3
"""
修复考勤数据库中的异常记录
"""
import sqlite3
import datetime
import os

DB_PATH = "data/attendance.db"

def fix_database():
    print("=" * 60)
    print("考勤数据库修复工具")
    print("=" * 60)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 1. 修复上班时间为 08:06:00 的异常记录
    print("\n[1] 检查上班时间异常的记录...")
    c.execute("SELECT id, work_date, work_time, remark FROM attendance WHERE work_time LIKE '%08:06:00'")
    bad_records = c.fetchall()
    
    if bad_records:
        print(f"    发现 {len(bad_records)} 条异常记录:")
        for record in bad_records:
            print(f"    - ID={record[0]}, 日期={record[1]}, 时间={record[2]}")
        print("\n    这些记录可能是之前bug产生的，将标记为未检测...")
        for record in bad_records:
            c.execute("UPDATE attendance SET work_time = NULL, work_status = 0 WHERE id = ?", (record[0],))
        print("    已将异常上班时间清空")
    else:
        print("    未发现 08:06:00 的异常记录")
    
    # 2. 检查日期与上班时间不匹配的情况
    print("\n[2] 检查日期与时间不匹配...")
    c.execute("SELECT id, work_date, work_time FROM attendance WHERE work_time IS NOT NULL")
    records = c.fetchall()
    
    date_mismatches = []
    for record in records:
        work_date, work_time = record[1], record[2]
        time_date = work_time.split(' ')[0]
        if work_date != time_date:
            date_mismatches.append(record)
            print(f"    - ID={record[0]}: 日期={work_date}, 时间日期={time_date}")
    
    if date_mismatches:
        print(f"\n    发现 {len(date_mismatches)} 条日期不匹配记录")
        print("    将修正时间日期使其与work_date匹配...")
        for record in date_mismatches:
            work_date = record[1]
            time_only = record[2].split(' ')[1]
            fixed_time = f"{work_date} {time_only}"
            c.execute("UPDATE attendance SET work_time = ? WHERE id = ?", (fixed_time, record[0]))
            print(f"    已修正 ID={record[0]}: {record[2]} -> {fixed_time}")
    else:
        print("    未发现日期不匹配")
    
    # 3. 检查下班时间是否合理
    print("\n[3] 检查下班时间合理性...")
    c.execute("SELECT id, work_date, home_time FROM attendance WHERE home_time IS NOT NULL")
    home_records = c.fetchall()
    
    unreasonable = []
    for record in home_records:
        work_date, home_time = record[1], record[2]
        time_only = home_time.split(' ')[1]
        hour = int(time_only.split(':')[0])
        # 下班时间应该在 18:00 - 01:00 之间
        if hour < 18 and hour >= 0:
            unreasonable.append(record)
            print(f"    - ID={record[0]}, 日期={work_date}, 下班时间={home_time}")
    
    if unreasonable:
        print(f"\n    发现 {len(unreasonable)} 条下班时间可能异常的记录")
        print("    这些可能是跨天检测或手动补录，请人工核实")
    else:
        print("    未发现明显异常的下班时间")
    
    conn.commit()
    
    # 4. 显示修复后的记录
    print("\n" + "=" * 60)
    print("修复后的记录:")
    c.execute("SELECT work_date, work_time, home_time, work_status, home_status, remark FROM attendance ORDER BY work_date DESC LIMIT 15")
    records = c.fetchall()
    print(f"{'日期':<12} {'上班时间':<22} {'下班时间':<22} {'上班':<4} {'下班':<4} {'备注'}")
    print("-" * 90)
    for r in records:
        work_time = r[1].split(' ')[1] if r[1] else '--:--:--'
        home_time = r[2].split(' ')[1] if r[2] else '--:--:--'
        print(f"{r[0]:<12} {work_time:<22} {home_time:<22} {r[3]:<4} {r[4]:<4} {r[5] or ''}")
    
    conn.close()
    print("\n" + "=" * 60)
    print("修复完成!")

if __name__ == "__main__":
    fix_database()
