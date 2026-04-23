# CMS Medical Insurance Policy Skill

**OpenClaw AI Agent Skill** - 查询各地异地就医备案政策，提供门诊、住院、报销额度等关键信息。

## 🎯 核心定位

这是一个 **OpenClaw Skill**，用于让 AI Agent 能够：
- 理解用户关于异地就医政策的查询
- 动态搜索并获取官方政策信息
- 以结构化方式返回政策数据
- 不限于预定义数据源，自动发现所有相关官方网站

## 📚 文档

- **[SKILL.md](SKILL.md)** - OpenClaw Skill 索引（Agent 入口）
- **[README.md](README.md)** - 本文档（使用说明）

## 快速安装

```bash
# 安装依赖
pip install playwright sqlalchemy

# 安装浏览器驱动
playwright install chromium
```

**就这么简单！** 数据库和日志目录会在首次运行时自动创建。

## OpenClaw Agent 使用

### 基本调用

```bash
# Agent 直接调用
python scripts/search/search_policy.py --region 北京 --policy_type 门诊
```

### 返回格式

**成功返回**：
```json
{
  "status": "success",
  "count": 2,
  "data": [
    {
      "policy_name": "北京市异地就医直接结算管理办法",
      "region": "北京",
      "source_type": "地方医保局",
      "outpatient": {
        "available": true,
        "reimbursement_rate": "50%"
      },
      "inpatient": {
        "available": true,
        "reimbursement_rate": "70%"
      },
      "source": "http://ybj.beijing.gov.cn/..."
    }
  ]
}
```

**错误返回**：
```json
{
  "status": "error",
  "message": "搜索失败: 网络连接超时"
}
```

**无结果返回**：
```json
{
  "status": "success",
  "count": 0,
  "data": []
}
```

### Agent 工作流程

```
用户问："北京市的异地就医门诊报销比例是多少？"
    ↓
Agent 提取：region=北京, policy_type=门诊
    ↓
Agent 调用：python scripts/search/search_policy.py --region 北京 --policy_type 门诊
    ↓
Agent 解析 JSON：outpatient.reimbursement_rate = "50%"
    ↓
Agent 回答："根据最新政策，北京市异地就医门诊报销比例为 50%"
```

## 核心功能使用

```bash
# 查询北京市的政策（优先从缓存读取）
python scripts/search/search_policy.py --region 北京

# 查询门诊政策
python scripts/search/search_policy.py --policy_type 门诊

# 查询特定关键词
python scripts/search/search_policy.py --keyword 直接结算 --time_range 近1年

# 组合查询
python scripts/search/search_policy.py --region 上海 --policy_type 住院

# 强制重新抓取（不使用缓存）
python scripts/search/search_policy.py --region 北京 --no-cache

# 查看数据库统计信息
python scripts/search/search_policy.py --stats
```

## 参数说明

| 参数 | 类型 | 必填 | 说明 | 示例 |
|---|---|---|---|---|
| `--region` | string | 否 | 地区名称 | 北京、上海、广东 |
| `--policy_type` | string | 否 | 政策类型 | 门诊、住院 |
| `--keyword` | string | 否 | 搜索关键词 | 异地就医备案、直接结算 |
| `--time_range` | string | 否 | 时间范围 | 近1年、近2年 |
| `--no-cache` | flag | 否 | 不使用缓存，强制重新抓取 | - |
| `--stats` | flag | 否 | 显示数据库统计信息 | - |

## 数据源

### 搜索策略

**动态发现**：通过搜索引擎自动发现所有相关官方网站，不限于预定义列表

**识别规则**：
- 优先选择 `.gov.cn` 域名
- 识别医保局相关域名（`ybj.*`）
- 包含官方媒体报道
- 使用正则模式匹配，不限制白名单

### 参考数据源（示例）

**国家级**：
- 国家医保局 (nhsa.gov.cn)
- 中国政府网 (gov.cn)
- 人社部 (mohrss.gov.cn)

**省级**：
- 各省市医保局 (ybj.*.gov.cn)
- 各省市政府网站 (*.gov.cn)

**官方媒体**：
- 新华网 (xinhuanet.com)
- 人民网 (people.com.cn)
- 央视网 (cctv.com)

**注意**：实际搜索不限于以上列表，会动态发现所有相关官方网站。

## 数据存储

### 自动保存机制

每次搜索到的政策**自动保存**到本地数据库：
- 位置：`.cms-data/policies.db`（SQLite）
- 首次运行自动创建
- 根据来源 URL 自动去重

### 智能缓存

```bash
# 第一次查询 - 从网络搜索并保存
python scripts/search/search_policy.py --region 北京
# → 搜索 → 提取 → 保存到数据库 → 返回结果

# 第二次查询 - 从数据库读取（秒级响应）
python scripts/search/search_policy.py --region 北京
# → 直接从数据库读取 → 返回结果

# 强制重新搜索
python scripts/search/search_policy.py --region 北京 --no-cache
# → 忽略缓存 → 重新搜索 → 更新数据库
```

### 存储字段

政策信息存储在 SQLite 数据库中（`.cms-data/policies.db`），包含以下字段：

- **基本信息**：政策名称、发布日期、地区、来源类型
- **来源追溯**：来源 URL（唯一索引）、来源类型
- **门诊信息**：是否可用、报销比例
- **住院信息**：是否可用、报销比例
- **报销额度**：年度限额、单次限额
- **备案流程**：备案方式、所需材料、有效期（JSON）
- **特殊人群**：退休人员、在职职工、急诊、慢性病患者（JSON）
- **直接结算**：结算范围、步骤、报销要求（JSON）
- **药品诊疗**：药品目录、诊疗范围（JSON）
- **元数据**：创建时间、更新时间

### 查看统计

```bash
python scripts/search/search_policy.py --stats
```

返回：
```json
{
  "status": "success",
  "statistics": {
    "total_policies": 50,
    "total_regions": 12,
    "last_updated": "2026-04-23T10:30:00"
  }
}
```

## 技术特性

- ✅ **动态搜索**：不限于预定义数据源，自动发现所有官方网站
- ✅ **自动保存**：搜索结果自动保存到本地数据库，记录来源
- ✅ **智能缓存**：优先从数据库读取，提高查询速度
- ✅ **自动去重**：根据来源 URL 自动去重，更新时覆盖
- ✅ **真实内容解析**：从官方网站提取实际政策信息
- ✅ **智能信息提取**：使用正则表达式提取关键数据
- ✅ **重试机制**：网络失败自动重试（最多3次）
- ✅ **日志管理**：完整的日志记录和错误追踪
- ✅ **反爬虫处理**：隐藏自动化特征，处理 Cloudflare 挑战
- ✅ **官方源过滤**：只返回政府官方网站的信息
- ✅ **单元测试**：覆盖核心功能的测试用例

## 环境变量

- `HEADLESS`: 是否使用无头模式运行浏览器（默认：true）
  ```bash
  # 显示浏览器窗口（用于调试）
  HEADLESS=false python scripts/search/search_policy.py --region 北京
  ```

## 日志

日志文件保存在 `.cms-log/search.log`，包含详细的执行信息和错误日志。

## 注意事项

1. 首次运行需要安装 Playwright 浏览器驱动
2. 网络连接需要稳定，建议在良好的网络环境下使用
3. 部分政府网站可能有访问限制，建议合理控制请求频率
4. 提取的信息仅供参考，具体以当地最新政策为准

## 版本

当前版本：0.2.0

## 许可

MIT License
