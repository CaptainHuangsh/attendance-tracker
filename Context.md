# Context.md - 牛马打工人项目上下文

## 当前状态 (2026-03-27)

### 项目位置
`/home/ivo/.openclaw/workspace/projects/attendance-tracker`

### 最新数据记录 (修复后)
```
2026-03-27: 上班=未检测, 下班=未检测  (今日)
2026-03-26: 上班=未检测, 下班=20:50:21
2026-03-25: 上班=未检测, 下班=20:50:48
2026-03-24: 上班=未检测, 下班=20:50:36
2026-03-23: 上班=未检测, 下班=20:50:57
2026-03-22: 上班=未检测, 下班=未检测  (周六)
2026-03-20: 上班=未检测, 下班=20:51:31
2026-03-19: 上班=未检测, 下班=20:50:20
2026-03-18: 上班=未检测, 下班=22:51:28  (手动补录)
```

### 核心问题 → 已修复

1. **上班打卡永远不触发** ✅ 已修复
2. **下班打卡时间不准确** ✅ 已修复
3. **上班时间异常 08:06:00** ✅ 已修复
4. **MAC地址配置错误** ✅ 已修复

## Bug 修复详情

### Bug 1: 上班检测逻辑 (main.py)

**原问题**: 
```python
else:
    # 设备在线，重置计数器（用户还在家）
    if work_lost_counter > 0:
        work_lost_counter = 0  # ← BUG: 在线就重置
```

**修复后**:
```python
else:
    # BUG修复: 设备在线时不重置计数器
    logger.debug(f"上班检测: 设备在线，计数器保持={work_lost_counter}")
```

### Bug 2: 下班检测逻辑 (main.py)

**原问题**: 
```python
if online:
    update_home_time()  # ← 首次检测到在线就记录
```

**修复后**:
```python
if online:
    if first_online_time is None:
        # 首次检测到在线，记录时间
        save_home_first_online(now.strftime("%Y-%m-%d %H:%M:%S"))
    else:
        # 持续在线，用首次时间打卡
        update_home_time_with_time(first_online_time)
```

新增文件: `data/home_first_online.txt` - 存储首次检测到在线的时间

### Bug 3: MAC地址错误

**原配置**: `64:BD:6D:B3:79:32`
**实际MAC**: `78:0f:77:e1:6f:f6`

已更新 `data/config.json`

### Bug 4: 数据库异常记录

- 03-18, 03-19 的上班时间 `08:06:00` → 已清空，标记为未检测

## 当前配置 (已修复)

```json
{
  "mac_address": "78:0f:77:e1:6f:f6",
  "static_ip": "192.168.1.16",
  "work_start": "07:40",
  "work_end": "08:40",
  "home_start": "20:50",
  "home_end": "00:30",
  "scan_interval": 60,
  "work_lost_count": 2
}
```

## 持久化文件

| 文件 | 说明 |
|------|------|
| `data/work_counter.txt` | 上班离线计数器 |
| `data/home_first_online.txt` | 下班首次在线时间 |

## 日志位置

- 文件: `attendance-tracker/data/app.log`
- 关键日志关键词: `上班检测`, `下班检测`, `设备检测`
