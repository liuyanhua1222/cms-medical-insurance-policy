# search 脚本索引

## 脚本清单

| 脚本名 | 说明 | 路径 |
|---|---|---|
| search_policy.py | 查询各地异地就医备案政策信息 | `./scripts/search/search_policy.py` |

## 运行方式

### 命令行运行

```bash
python ./scripts/search/search_policy.py --region <地区> --policy_type <政策类型> --keyword <关键词> --time_range <时间范围>
```

### 参数说明

| 参数 | 类型 | 必填 | 说明 | 示例 |
|---|---|---|---|---|
| `--region` | string | 否 | 地区名称，如省份、城市 | 北京、上海、广东 |
| `--policy_type` | string | 否 | 政策类型，如门诊、住院、报销额度等 | 门诊、住院、报销额度 |
| `--keyword` | string | 否 | 搜索关键词 | 异地就医备案、直接结算 |
| `--time_range` | string | 否 | 时间范围，如近1年、近2年 | 近1年、近2年 |

### 示例

```bash
# 查询北京市的异地就医备案政策
python ./scripts/search/search_policy.py --region 北京

# 查询全国范围内的门诊异地就医政策
python ./scripts/search/search_policy.py --policy_type 门诊

# 查询近1年的异地就医直接结算政策
python ./scripts/search/search_policy.py --keyword 直接结算 --time_range 近1年
```

## 鉴权前置条件

- 本脚本为 `nologin` 动作，不依赖额外鉴权获取流程
- 直接访问公开的官方网站获取政策信息

## 返回说明

### 成功返回

返回结构化 JSON 数据，包含政策名称、发布日期、适用地区、门诊使用情况、住院使用情况、报销额度限制、社康使用情况等信息。

示例：

```json
{
  "status": "success",
  "data": [
    {
      "policy_name": "关于做好异地就医直接结算工作的通知",
      "release_date": "2025-01-01",
      "region": "全国",
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
      "source": "https://www.nhsa.gov.cn/"
    }
  ]
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