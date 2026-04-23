---
name: cms-medical-insurance-policy
description: 查询各地异地就医备案政策，提供门诊、住院、报销额度等关键信息
skillcode: cms-medical-insurance-policy
github: https://github.com/liuyanhua/cms-medical-insurance-policy
---

# cms-medical-insurance-policy — 索引

本文件提供能力边界、路由规则与使用约束。详细说明见 `references/`，实际执行见 `scripts/`。

**当前版本**: 0.1.0
**接口版本**: v1

**能力概览（1 块能力）**：
- `search`：查询各地异地就医备案政策，获取门诊使用、住院使用、报销额度、社康使用等关键信息

统一规范：
- 鉴权模式：`nologin`（直接访问公开的官方网站获取政策信息）
- 运行日志：`.cms-log/`

授权依赖：
- 本技能为 `nologin` 动作，不依赖额外鉴权获取流程

建议工作流（简版）：
1. 先读取 `SKILL.md`，确认能力边界和限制
2. 根据用户意图定位模块
3. 读取对应模块说明
4. 补齐必要输入
5. 执行对应脚本

模块路由与能力索引：
| 用户意图 | 模块 | 能力摘要 | 模块说明 | 脚本 |
|---|---|---|---|---|
| 查询异地就医备案政策 | `search` | 获取各地异地就医备案政策信息 | `./references/search/README.md` | `./scripts/search/search_policy.py` |

能力树：

```text
cms-medical-insurance-policy/
├── SKILL.md
├── references/
│   └── search/
│       └── README.md
└── scripts/
    └── search/
        ├── README.md
        └── search_policy.py
```