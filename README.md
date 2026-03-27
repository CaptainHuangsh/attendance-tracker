# 上下班自动统计系统 + 人生日历

全自动统计上下班时间 + 人生格子可视化。

## 功能特性
- ✅ 零手动操作，全自动检测离家/到家
- ✅ 静态IP + MAC地址双校验，准确率高
- ✅ 人生日历可视化（按周/按天，横排/竖排）
- ✅ Docker容器化部署，7×24h稳定运行
- ✅ 网页配置界面，修改配置即时生效
- ✅ 数据持久化存储在SQLite

## 部署方法
```bash
cd attendance-tracker
docker-compose up -d
```

## 访问地址
http://你的服务器IP:10170

---

## 人生日历配置说明

### 配置入口
点击「编辑阶段」按钮进入配置弹窗

### 人生阶段（Phase）

用于可视化人生不同时期（如童年、求学、工作、退休）

```json
[
  {
    "name": "童年",
    "startAge": 0,
    "endAge": 7,
    "color": "#fbbf24",
    "text": "童"
  },
  {
    "name": "求学",
    "startAge": 7,
    "endAge": 22,
    "color": "#10b981",
    "text": "学"
  },
  {
    "name": "工作",
    "startAge": 22,
    "endAge": 60,
    "color": "#3b82f6",
    "text": "工"
  },
  {
    "name": "退休",
    "startAge": 60,
    "endAge": 90,
    "color": "#8b5cf6",
    "text": "休"
  }
]
```

**字段说明：**
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 阶段名称 |
| startAge | number | 是 | 开始年龄（岁） |
| endAge | number | 是 | 结束年龄（岁） |
| color | string | 是 | 颜色（HEX格式，如 #fbbf24） |
| text | string | 否 | 格子内显示的文字 |

**示例：**
```json
{"name": "大学", "startAge": 18, "endAge": 22, "color": "#3b82f6", "text": "大"}
```

### 重要事件（Event）

用于标记人生中的重要时间点（如毕业、结婚、买房）

```json
[
  {
    "name": "大学毕业",
    "date": "2017-06-01",
    "color": "#f59e0b"
  },
  {
    "name": "入职",
    "date": "2017-07-01",
    "color": "#10b981"
  }
]
```

**字段说明：**
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 事件名称 |
| date | string | 是 | 日期（YYYY-MM-DD格式） |
| color | string | 是 | 颜色（HEX格式） |

### 快捷颜色参考
- 黄色：`#fbbf24` - 童年
- 绿色：`#10b981` - 求学/成长
- 蓝色：`#3b82f6` - 工作
- 紫色：`#8b5cf6` - 退休
- 橙色：`#f59e0b` - 纪念/重要事件
- 红色：`#ef4444` - 特别纪念
- 粉色：`#ec4899` - 情感相关
- 青色：`#06b6d4` - 旅行/里程碑

---

## 考勤检测配置

### 时间窗口
- 上班窗口：07:40 ~ 08:40（连续2次离线判定为已出门）
- 下班窗口：20:50 ~ 00:30（检测到在线判定为已到家）

### 手机设置要求
- 设置静态IP
- 固定MAC地址
- WiFi休眠时保持连接

### 路由器要求
- 关闭AP隔离/客户端隔离

---

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/config | 获取配置 |
| POST | /api/config | 更新配置 |
| GET | /api/attendance | 获取考勤记录 |
| POST | /api/attendance/fix | 手动补录 |
| GET | /api/export/csv | 导出CSV |
| GET | /api/status | 系统状态 |
