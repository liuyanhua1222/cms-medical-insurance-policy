# search 模块说明

## 适用场景

本模块用于查询全国各地的异地就医备案政策，重点关注以下场景：

- 用户需要了解异地就医备案的基本流程和要求
- 用户需要查询特定地区的异地就医备案政策
- 用户需要了解异地就医的门诊、住院、报销额度、社康使用等关键信息
- 用户需要获取最新的异地就医备案政策变化

## 输入要求

| 参数名 | 类型 | 必填 | 说明 | 示例 |
|---|---|---|---|---|
| `region` | string | 否 | 地区名称，如省份、城市 | 北京、上海、广东 |
| `policy_type` | string | 否 | 政策类型，如门诊、住院、报销额度等 | 门诊、住院、报销额度 |
| `keyword` | string | 否 | 搜索关键词 | 异地就医备案、直接结算 |
| `time_range` | string | 否 | 时间范围，如近1年、近2年 | 近1年、近2年 |

## 输出说明

| 字段名 | 类型 | 说明 | 示例 |
|---|---|---|---|
| `policy_name` | string | 政策名称 | 关于做好异地就医直接结算工作的通知 |
| `release_date` | string | 发布日期 | 2025-01-01 |
| `region` | string | 适用地区 | 全国、北京市 |
| `outpatient` | object | 门诊使用情况 | `{"available": true, "reimbursement_rate": "50%"}` |
| `inpatient` | object | 住院使用情况 | `{"available": true, "reimbursement_rate": "70%"}` |
| `reimbursement_limit` | object | 报销额度限制 | `{"annual_limit": "100000", "single_limit": "20000"}` |
| `community_health` | boolean | 社康使用情况 | true |
| `filing_process` | object | 备案流程与操作细节 | `{"methods": ["线上", "线下"], "materials": ["身份证", "医保卡"], "validity": "1年", "change_process": "线上申请"}` |
| `special_groups` | object | 特殊人群政策 | `{"retirees": true, "workers": true, "emergency": true, "chronic_patients": true}` |
| `direct_settlement` | object | 直接结算与报销流程 | `{"scope": "定点医疗机构", "steps": ["备案", "就医", "直接结算"], "reimbursement_requirements": ["发票", "费用明细"]}` |
| `drugs_and_treatment` | object | 药品与诊疗项目 | `{"drug_list": "参保地目录", "treatment_scope": "医保范围内", "consumables_reimbursement": "50%"}` |
| `policy_timeliness` | object | 政策时效性与地区差异 | `{"latest_adjustment": "2025-01-01", "cross_regional_differences": "存在", "transition_period": "3个月"}` |
| `common_issues` | object | 常见问题与风险提示 | `{"filing_failure_reasons": ["材料不全", "信息错误"], "unfiled_treatment": "报销比例降低", "duplicate_insurance": "选择一地参保"}` |
| `source` | string | 政策来源 | https://www.nhsa.gov.cn/ |
| `notes` | string | 备注 | 具体以当地最新政策为准 |

## 动作列表

| 动作 | 说明 | 脚本路径 |
|---|---|---|
| 搜索异地就医备案政策 | 查询各地异地就医备案政策信息 | `./scripts/search/search_policy.py` |
| 生成政策报告 | 将查询结果生成为 Markdown 格式报告 | `./scripts/search/search_policy.py --report <文件路径>` |

## 报告生成

查询完成后可以生成易读的 Markdown 报告，包含：

- 政策基本信息（名称、地区、发布日期、来源）
- 门诊使用情况（是否可用、报销比例）
- 住院使用情况（是否可用、报销比例）
- 报销额度（年度限额、单次限额）
- 社区医疗使用情况
- 备案流程（方式、材料、有效期）
- 特殊人群政策（退休、在职、急诊、慢病）
- 直接结算（范围、步骤、要求）
- 药品与诊疗（目录、范围）

**使用示例**：
```bash
python scripts/search/search_policy.py --region 北京 --report reports/beijing.md
```