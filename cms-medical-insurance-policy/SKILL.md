---
name: cms-medical-insurance-policy
description: 查询各地异地就医备案政策，提供门诊、住院、报销额度等关键信息。通过搜索引擎动态发现官方政策，不限于预定义数据源。
skillcode: cms-medical-insurance-policy
github: https://github.com/liuyanhua1222/cms-medical-insurance-policy
---

# cms-medical-insurance-policy — 索引

本文件提供能力边界、路由规则与使用约束。详细说明见 `references/`，实际执行见 `scripts/`。

**当前版本**: 0.2.0
**接口版本**: v1
**适用场景**: OpenClaw AI Agent Skill

**能力概览（1 块核心能力）**：
- `search`：查询各地异地就医备案政策，获取门诊使用、住院使用、报销额度、社康使用等关键信息

**数据获取方式**：
- 通过搜索引擎动态发现所有相关官方网站
- 自动识别 .gov.cn 等政府域名
- 不限于预定义数据源白名单
- 优先展示官方权威信息

**依赖要求**：
- Python 3.8+
- playwright（自动安装浏览器驱动）

**安装依赖**：
```bash
pip install playwright
playwright install chromium
```

**运行环境**：
- 鉴权模式：`nologin`（直接访问公开的官方网站）
- 运行日志：`.cms-log/`（自动创建）

**OpenClaw Agent 使用流程**：
1. 理解用户查询意图（地区、政策类型、关键词）
2. 调用 `python scripts/search/search_policy.py [参数]`
3. 解析返回的 JSON 数据
4. 以自然语言向用户呈现结果

**参数说明**：
- `--region <地区>`: 查询特定地区（如：北京、上海）
- `--policy_type <类型>`: 政策类型（如：门诊、住院）
- `--keyword <关键词>`: 搜索关键词（如：报销比例、备案流程）
- `--time_range <范围>`: 时间范围（如：近1年、近2年）
- `--report <文件路径>`: 生成 Markdown 格式报告

模块路由与能力索引：
| 用户意图 | 模块 | 能力摘要 | 模块说明 | 脚本 |
|---|---|---|---|---|
| 查询异地就医备案政策 | `search` | 动态搜索并获取各地异地就医备案政策信息 | `./references/search/README.md` | `./scripts/search/search_policy.py` |

能力树：

```text
cms-medical-insurance-policy/
├── SKILL.md                          # Skill 索引（OpenClaw 入口）
├── README.md                         # 使用说明
├── requirements.txt                  # Python 依赖
├── .gitignore                        # Git 配置
├── references/
│   └── search/
│       └── README.md                 # 核心能力说明
├── scripts/
│   └── search/
│       ├── search_policy.py          # 核心脚本（Agent 调用）
│       └── data_sources.py           # 数据源配置（动态搜索）
└── tests/
    └── test_search_policy.py         # 单元测试
```