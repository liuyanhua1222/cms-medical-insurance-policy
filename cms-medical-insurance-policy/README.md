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
pip install playwright

# 安装浏览器驱动
playwright install chromium
```

**就这么简单！** 日志目录会在首次运行时自动创建。

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
# 查询北京市的政策
python scripts/search/search_policy.py --region 北京

# 查询门诊政策
python scripts/search/search_policy.py --policy_type 门诊

# 查询特定关键词
python scripts/search/search_policy.py --keyword 直接结算 --time_range 近1年

# 组合查询
python scripts/search/search_policy.py --region 上海 --policy_type 住院

# 生成报告（Markdown格式）
python scripts/search/search_policy.py --region 北京 --report reports/beijing_policy.md

# 查询并生成报告
python scripts/search/search_policy.py --region 上海 --policy_type 门诊 --report reports/shanghai_outpatient.md
```

## 参数说明

| 参数 | 类型 | 必填 | 说明 | 示例 |
|---|---|---|---|---|
| `--region` | string | 否 | 地区名称 | 北京、上海、广东 |
| `--policy_type` | string | 否 | 政策类型 | 门诊、住院 |
| `--keyword` | string | 否 | 搜索关键词 | 异地就医备案、直接结算 |
| `--time_range` | string | 否 | 时间范围 | 近1年、近2年 |
| `--report` | string | 否 | 生成报告并保存到指定文件（Markdown格式） | reports/policy.md |

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

## 报告生成

查询完成后可以生成易读的 Markdown 报告：

```bash
# 生成报告
python scripts/search/search_policy.py --region 北京 --report reports/beijing.md
```

**报告内容包括**：
- 📊 **汇总对比表** - 多个地区政策一目了然
- 📋 政策基本信息（名称、地区、发布日期、来源）
- 🏥 门诊使用情况（是否可用、报销比例）
- 🛏️ 住院使用情况（是否可用、报销比例）
- 💰 报销额度（年度限额、单次限额）
- 🏘️ 社区医疗使用情况
- 📝 备案流程（方式、材料、有效期）
- 👥 特殊人群政策（退休、在职、急诊、慢病）
- 💳 直接结算（范围、步骤、要求）
- 💊 药品与诊疗（目录、范围）

**报告示例**：

```markdown
# 异地就医备案政策查询报告

**生成时间**: 2026-04-23 22:00:00
**政策数量**: 2 条

---

## 📊 政策汇总对比表

| 地区 | 政策名称 | 门诊报销 | 住院报销 | 年度限额 | 社康 | 备案方式 | 来源类型 |
|---|---|---|---|---|---|---|---|
| 北京 | 北京市异地就医直接结算管理办法 | 50% | 70% | 100,000元 | ✅ | 线上/线下 | 地方医保局 |
| 上海 | 上海市异地就医备案管理规定 | 60% | 75% | 150,000元 | ✅ | 线上/线下/APP | 地方医保局 |

---

## 1. 北京市异地就医直接结算管理办法

### 基本信息

- **地区**: 北京
- **发布日期**: 2025-01-15
- **来源类型**: 地方医保局
- **来源链接**: [http://ybj.beijing.gov.cn/...]

...
```

### 数据来源追溯

### 数据来源追溯

每条政策信息都包含完整的来源追溯：
- **source**: 政策原文 URL
- **source_type**: 来源类型（国家医保局、地方医保局、政府网站、官方媒体）
- **release_date**: 发布日期
- **region**: 适用地区

JSON 输出中包含所有字段，便于 Agent 进一步处理和分析。

## 技术特性

- ✅ **动态搜索**：不限于预定义数据源，自动发现所有官方网站
- ✅ **无状态设计**：每次查询都获取最新数据，无需管理缓存
- ✅ **汇总报告**：自动生成对比表，多地区政策一目了然
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
