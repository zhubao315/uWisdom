---
title: Schema 定义索引
summary: uWisdom 知识单元 Schema 标准定义
permalink: /schemas/
---

# Schema 定义索引

本目录存放 uWisdom 项目的 JSON Schema 定义，用于规范知识单元结构，确保机器可读性。

## 可用 Schema

| Schema | 版本 | 说明 |
|--------|------|------|
| [knowledge-unit.schema.json](../schemas/knowledge-unit.schema.json) | v1.0.0 | 知识单元标准 Schema |

## 知识单元 Schema

### 必填字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `title` | string | 条目标题，≤50 字符 |
| `summary` | string | 一句话摘要，10-200 字符 |
| `type` | enum | 知识类型 |
| `version` | string | 语义化版本号 |

### 可选字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 唯一标识，格式 `kw-{field}-{name}` |
| `identity` | enum | 身份归属 |
| `field` | string | 领域标签 |
| `tags` | array | 标签数组 |
| `confidence` | enum | 可信度 high/medium/low |
| `applicability` | array | 适用场景 |
| `non_applicability` | array | 非适用场景 |
| `skill_ref` | string | 关联的 uSkills 技能 ID |
| `test_cases` | array | 验证用例 |

### 知识类型 (type)

| 值 | 说明 |
|------|------|
| `principle` | 原则 |
| `method` | 方法 |
| `glossary` | 术语 |
| `decision` | 决策 |
| `area` | 领域 |
| `project` | 项目 |
| `task-pattern` | 任务模式 |
| `case` | 案例 |
| `opportunity` | 机会 |
| `agent-card` | Agent 调用卡 |

### 身份类型 (identity)

| 值 | 说明 |
|------|------|
| `architect` | 架构师 |
| `investor` | 投资人 |
| `lifelong-learner` | 终身学习者 |
| `life-artist` | 生活艺术家 |

## 验证工具

```bash
# 安装验证工具
pip install jsonschema

# 验证知识单元
python3 -c "
import json
import jsonschema

schema = json.load(open('docs/schemas/knowledge-unit.schema.json'))
data = {'title': 'Test', 'summary': 'Test summary', 'type': 'principle', 'version': '1.0.0'}
jsonschema.validate(data, schema)
print('Schema validation passed!')
"
```

## 示例

```yaml
---
id: "kw-ai-llm-001"
title: "LLM 应用架构"
summary: "大型语言模型应用的核心架构模式和设计原则"
permalink: /knowledge-base/themes/llm-application-architecture.html
type: "principle"
identity: "architect"
field: "ai"
tags: ["ai", "architecture", "llm"]
version: "v1.0.0"
confidence: "high"
applicability:
  - "构建 LLM 应用时"
  - "设计 AI 系统架构时"
non_applicability:
  - "简单的规则引擎场景"
skill_ref: "uskill-architecture-001"
test_cases:
  - input: "需要构建 RAG 系统"
    expected: "应考虑向量数据库、检索策略、上下文窗口管理"
---
```
