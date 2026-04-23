# search 脚本索引

## 脚本清单

| 脚本名 | 说明 | 路径 |
|---|---|---|
| search_policy.py | 查询各地异地就医备案政策信息（支持缓存） | `./scripts/search/search_policy.py` |
| batch_crawl.py | 批量爬取多个来源的政策信息 | `./scripts/search/batch_crawl.py` |
| database.py | 数据库管理模块 | `./scripts/search/database.py` |
| data_sources.py | 数据源配置模块 | `./scripts/search/data_sources.py` |

## 运行方式

### 1. search_policy.py - 单次查询

#### 命令行运行

```bash
python ./scripts/search/search_policy.py --region <地区> --policy_type <政策类型> --keyword <关键词> --time_range <时间范围>
```

#### 参数说明

| 参数 | 类型 | 必填 | 说明 | 示例 |
|---|---|---|---|---|
| `--region` | string | 否 | 地区名称，如省份、城市 | 北京、上海、广东 |
| `--policy_type` | string | 否 | 政策类型，如门诊、住院、报销额度等 | 门诊、住院、报销额度 |
| `--keyword` | string | 否 | 搜索关键词 | 异地就医备案、直接结算 |
| `--time_range` | string | 否 | 时间范围，如近1年、近2年 | 近1年、近2年 |
| `--no-cache` | flag | 否 | 不使用缓存，强制重新抓取 | - |
| `--stats` | flag | 否 | 显示数据库统计信息 | - |

#### 示例

```bash
# 查询北京市的异地就医备案政策（优先从缓存读取）
python ./scripts/search/search_policy.py --region 北京

# 查询全国范围内的门诊异地就医政策
python ./scripts/search/search_policy.py --policy_type 门诊

# 查询近1年的异地就医直接结算政策
python ./scripts/search/search_policy.py --keyword 直接结算 --time_range 近1年

# 强制重新抓取（不使用缓存）
python ./scripts/search/search_policy.py --region 北京 --no-cache

# 查看数据库统计信息
python ./scripts/search/search_policy.py --stats
```

### 2. batch_crawl.py - 批量爬取

#### 命令行运行

```bash
python ./scripts/search/batch_crawl.py --scope <爬取范围> --workers <并发数>
```

#### 参数说明

| 参数 | 类型 | 必填 | 说明 | 示例 |
|---|---|---|---|---|
| `--scope` | string | 否 | 爬取范围 | national, provincial, media, all（默认：all） |
| `--workers` | int | 否 | 并发线程数 | 3（默认）, 5, 10 |

#### 示例

```bash
# 批量爬取所有来源的政策
python ./scripts/search/batch_crawl.py --scope all

# 只爬取省级政策
python ./scripts/search/batch_crawl.py --scope provincial

# 只爬取国家级政策
python ./scripts/search/batch_crawl.py --scope national

# 只爬取官方媒体报道
python ./scripts/search/batch_crawl.py --scope media

# 设置并发线程数为5
python ./scripts/search/batch_crawl.py --scope all --workers 5
```

## 鉴权前置条件

- 本脚本为 `nologin` 动作，不依赖额外鉴权获取流程
- 直接访问公开的官方网站获取政策信息

## 返回说明

### search_policy.py 成功返回

返回结构化 JSON 数据，包含政策名称、发布日期、适用地区、门诊使用情况、住院使用情况、报销额度限制、社康使用情况等信息。

示例：

```json
{
  "status": "success",
  "count": 2,
  "from_cache": true,
  "data": [
    {
      "policy_name": "关于做好异地就医直接结算工作的通知",
      "release_date": "2025-01-15",
      "region": "北京",
      "source_type": "地方政府",
      "outpatient": {
        "available": true,
        "reimbursement_rate": "50%"
      },
      "inpatient": {
        "available": true,
        "reimbursement_rate": "70%"
      },
      "reimbursement_limit": {
        "annual_limit": "100000",
        "single_limit": "20000"
      },
      "community_health": true,
      "source": "http://ybj.beijing.gov.cn/art/2025/art_123.html",
      "created_at": "2026-04-23T10:30:00",
      "updated_at": "2026-04-23T10:30:00"
    }
  ]
}
```

### batch_crawl.py 成功返回

返回批量爬取的统计信息。

示例：

```json
{
  "start_time": "2026-04-23 10:00:00",
  "end_time": "2026-04-23 10:30:00",
  "scope": "all",
  "results": {
    "national": {
      "status": "success",
      "count": 5
    },
    "provincial": [
      {
        "region": "北京市医保局",
        "status": "success",
        "count": 3
      },
      {
        "region": "上海市医保局",
        "status": "success",
        "count": 4
      }
    ],
    "media": {
      "status": "success",
      "count": 8
    }
  },
  "statistics": {
    "total_policies": 50,
    "total_regions": 12,
    "last_updated": "2026-04-23T10:30:00"
  }
}
```

### 失败返回

返回包含错误原因的 JSON 数据。

示例：

```json
{
  "status": "error",
  "message": "搜索失败，请检查网络连接或参数是否正确"
}
```

## 数据存储

### 数据库位置

- 数据库文件：`.cms-data/policies.db`
- 日志文件：`.cms-log/search.log`

### 数据库表结构

`policies` 表包含以下字段：

- `id`: 主键
- `policy_name`: 政策名称
- `release_date`: 发布日期
- `region`: 适用地区
- `source`: 来源URL（唯一索引）
- `source_type`: 来源类型（国家医保局、地方政府、官方媒体等）
- `outpatient_available`: 门诊是否可用
- `outpatient_rate`: 门诊报销比例
- `inpatient_available`: 住院是否可用
- `inpatient_rate`: 住院报销比例
- `annual_limit`: 年度报销限额
- `single_limit`: 单次报销限额
- `community_health`: 社康是否可用
- `filing_process`: 备案流程（JSON）
- `special_groups`: 特殊人群（JSON）
- `direct_settlement`: 直接结算（JSON）
- `drugs_and_treatment`: 药品与诊疗（JSON）
- `policy_timeliness`: 政策时效性（JSON）
- `common_issues`: 常见问题（JSON）
- `full_content`: 完整内容（JSON）
- `notes`: 备注
- `created_at`: 创建时间
- `updated_at`: 更新时间

## 工作流程建议

1. **首次使用**：运行批量爬取建立数据库
   ```bash
   python ./scripts/search/batch_crawl.py --scope all
   ```

2. **日常查询**：使用缓存快速查询
   ```bash
   python ./scripts/search/search_policy.py --region 北京
   ```

3. **定期更新**：定期重新爬取更新数据（建议每周或每月）
   ```bash
   python ./scripts/search/batch_crawl.py --scope all
   ```

4. **查看统计**：了解数据库状态
   ```bash
   python ./scripts/search/search_policy.py --stats
   ```
