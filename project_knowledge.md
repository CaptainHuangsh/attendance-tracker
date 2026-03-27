# 牛马打工人 - 项目知识库

## 项目概述

**项目名称**: 牛马打工人 (attendance-tracker)
**功能**: 局域网设备扫描自动统计上下班时间
**部署**: Docker 容器化，7×24h 运行

## 技术栈

- **后端**: FastAPI + uvicorn
- **数据库**: SQLite
- **前端**: HTML + TailwindCSS + Vanilla JS
- **扫描**: ping + ip neigh (MAC校验)

## 目录结构

```
attendance-tracker/
├── main.py              # 核心逻辑 (540行)
├── Dockerfile            # 容器定义
├── docker-compose.yml   # 编排配置
├── requirements.txt     # Python依赖
├── static/
│   └── index.html       # Web界面
├── data/
│   ├── attendance.db    # SQLite数据库
│   ├── config.json      # 配置文件
│   ├── app.log          # 日志文件
│   └── work_counter.txt # 计数器持久化
└── test_*.py           # 测试脚本
```

## 核心配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| mac_address | 64:BD:6D:B3:79:32 | 目标设备MAC |
| static_ip | 192.168.1.16 | 目标设备IP |
| work_start | 07:40 | 上班检测开始 |
| work_end | 08:40 | 上班检测结束 |
| home_start | 20:50 | 下班检测开始 |
| home_end | 00:30 | 下班检测结束(跨天) |
| scan_interval | 60 | 扫描间隔(秒) |
| work_lost_count | 2 | 连续离线次数阈值 |

## 检测逻辑

### 上班检测 (07:40~08:40)
1. 每分钟扫描设备
2. 设备离线 → 计数器+1
3. **连续2次离线** → 记录上班时间
4. 计数器持久化到文件，重启不丢失

### 下班检测 (20:50~00:30 跨天)
1. 每分钟扫描设备
2. 设备在线 → 立即记录下班时间

### 关键函数

| 函数 | 位置 | 说明 |
|------|------|------|
| `is_device_online()` | main.py:129 | 双校验设备状态 |
| `is_in_work_window()` | main.py:192 | 检查上班窗口 |
| `is_in_home_window()` | main.py:204 | 检查下班窗口(含跨天) |
| `get_work_date()` | main.py:184 | 获取工作日期(00:00~00:30归前一天) |
| `scan_loop()` | main.py:299 | 后台扫描主循环 |

## 数据库结构

### attendance 表
```sql
CREATE TABLE attendance (
    id INTEGER PRIMARY KEY,
    work_date DATE UNIQUE,    -- 日期(唯一约束)
    work_time DATETIME,      -- 上班时间
    home_time DATETIME,      -- 下班时间
    work_status INTEGER,      -- 上班状态(0未检测/1正常)
    home_status INTEGER,      -- 下班状态
    remark TEXT,              -- 备注
    create_time DATETIME,
    update_time DATETIME
);
```

### system_config 表
```sql
CREATE TABLE system_config (
    id INTEGER PRIMARY KEY,
    config_key VARCHAR(50) UNIQUE,
    config_value TEXT,
    update_time DATETIME
);
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/config | 获取配置 |
| POST | /api/config | 更新配置 |
| GET | /api/attendance | 获取考勤记录 |
| GET | /api/attendance/month/{year}/{month} | 月度统计 |
| POST | /api/attendance/fix | 手动补卡 |
| GET | /api/export/csv | 导出CSV |
| GET | /api/status | 系统状态 |

## 已知问题/修复历史

### BUG-001: 上班打卡不触发
**症状**: 上班时间全为 NULL，只有手动补录
**原因**: `scan_loop()` 中设备在线时重置计数器，导致无法累积到阈值
**状态**: 已修复

### BUG-002: 下班打卡时间偏早
**症状**: 下班时间显示 20:50，但实际可能是其他时间
**原因**: 首次检测到在线就记录，记录时间非真实到家时间
**状态**: 已修复

### BUG-003: 跨天日期处理
**症状**: 00:00~00:30 期间打卡日期错乱
**原因**: `get_work_date()` 逻辑正确，但多处调用需统一
**状态**: 已修复

## 部署命令

```bash
# 启动服务
cd attendance-tracker
docker-compose up -d

# 查看日志
docker logs attendance-tracker -f

# 进入容器
docker exec -it attendance-tracker /bin/bash
```

## 访问地址

- 本地: http://localhost:8000
- Docker: http://容器IP:8000

## 工作日规则

- 默认: 周一至周五 (workdays: [0,1,2,3,4])
- 周末不扫描、不记录
- 节假日/调班需手动配置 workdays
