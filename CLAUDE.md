# uWisdom Agent 上下文

## 项目性质

个人知识操作系统，基于"驾驭工程可读性原则"。不是笔记库，是可工程化维护的知识系统。

## 核心定位

- 让知识持续演进，而不是一次性沉淀
- 让人能读、能查、能维护
- 让 Agent 能读、能检索、能调用

## 关键原则

1. **工程可读性优先** - 目录、命名、元数据、文档模板必须一致
2. **知识持续演进** - 每条知识要可增量更新、可追溯、可淘汰
3. **人机双读** - 既适合人阅读，也适合 Agent 解析与调用
4. **机会导向** - 围绕长期价值发现组织知识

## 目录结构

```
uWisdom/
├── docs/                          # Jekyll 站点源文件
│   ├── knowledge-base/            # 核心知识库
│   │   ├── domains/              # 领域 (14个)
│   │   └── themes/               # 主题 (32个)
│   ├── figures/                  # 人物志 (20+)
│   ├── identities/               # 身份地图 (4个)
│   ├── topic-research/           # 主题研究
│   └── today/                   # 每日精选 (自动生成)
├── tools/                        # 构建和验证工具
│   ├── build_site_data.py        # 生成搜索索引、图谱、每日精选
│   ├── validate_content.py       # 内容校验
│   ├── test_content.py          # TDD 测试框架
│   └── semantic_search.py        # 语义搜索
├── .github/workflows/            # CI/CD
└── skills/                       # Superpowers 技能库
```

## Superpowers 工作流

### 标准开发流程

```
1. brainstorming      → 需求澄清，设计讨论
   ↓ 用户确认设计
2. writing-plans      → 任务分解 (2-5分钟粒度)
   ↓ 用户确认计划
3. TDD                → 先写测试，验证失败
   ↓ 测试通过
4. 执行实现           → 编写代码
   ↓ 完成
5. requesting-code-review → 提交前审查
   ↓ 审查通过
6. 提交代码
```

### 触发规则

- **添加知识条目** → 必须先 brainstorming
- **修改现有条目** → 必须先写/更新测试
- **提交 PR** → 必须经过 requesting-code-review
- **长时间任务** → 每 30 分钟强制 checkpoint
- **调试问题** → 使用 systematic-debugging 技能

## 知识单元规范

### Front Matter 必填字段

```yaml
---
title: 条目标题                    # 必填，≤50字符
summary: 一句话摘要                  # 必填
permalink: /path/to/entry.html     # 必填
type: principle                    # principle|method|glossary|decision|area|project
identity: architect                # architect|investor|lifelong-learner|life-artist
field: ai                         # 领域标签
tags: [ai, architecture]          # 标签数组
version: v1.0.0                   # 版本号
author: 作者名                     # 作者
confidence: high                  # high|medium|low
applicability: []                  # 适用场景
non_applicability: []              # 非适用场景
---
```

### 知识类型

| type | 说明 |
|------|------|
| `principle` | 原则 |
| `method` | 方法 |
| `glossary` | 术语 |
| `decision` | 决策 |
| `area` | 领域 |
| `project` | 项目 |
| `task-pattern` | 任务模式 |

## 测试要求

### 必须运行的测试

```bash
# TDD 测试 (先运行，确保新增功能不会破坏现有功能)
python3 tools/test_content.py

# 内容校验
python3 tools/validate_content.py

# 依赖检查
python3 tools/check_dependencies.py
```

### 测试失败处理

1. **RED** - 写一个会失败的测试
2. **GREEN** - 写最小代码让测试通过
3. **REFACTOR** - 重构代码
4. **COMMIT** - 提交代码

## CI/CD 流程

```
PR 创建
   ↓
lint (代码风格检查)
   ↓
test (TDD 测试)
   ↓
validate (内容校验)
   ↓
build (构建站点)
   ↓
review (人工审查)
   ↓
merge (合并)
```

## Git 工作流

### 创建新任务分支

```bash
# 使用 worktree 创建独立工作分支
git worktree add ../uwisdom-TASK-xxx feature/TASK-xxx
```

### 提交规范

```
feat: 添加新的知识条目
fix: 修复内容校验问题
test: 添加单元测试
refactor: 重构代码结构
docs: 更新文档
```

## 常用命令

```bash
# 构建站点数据
python3 tools/build_site_data.py

# 运行测试
python3 tools/test_content.py

# 校验内容
python3 tools/validate_content.py

# 本地预览
cd docs && bundle exec jekyll serve --baseurl /uWisdom
```

## 质量标准

- Front Matter 必填字段完整率 = 100%
- WikiLink 死链率 = 0%
- 测试覆盖率 > 80%
- CI 通过率 = 100%
