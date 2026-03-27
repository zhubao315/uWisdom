---
title: uWisdom Superpowers 工程化分析
summary: 基于 Superpowers 方法论重新工程化 uWisdom 的完整方案
permalink: /uWisdom-SUPERPOWERS.html
type: method
identity: architect
field: engineering
tags: [engineering, superpowers, method]
version: v1.0.0
confidence: high
applicability: [uWisdom 项目改造, 软件工程流程优化]
non_applicability: []
---

# uWisdom Superpowers 工程化分析

**文档版本**: v1.0.0  
**分析日期**: 2026-03-27  
**方法论**: Superpowers 软件工程方法论  
**分析目标**: 用 Superpowers 重新工程化 uWisdom

---

## 一、现状分析

### 1.1 做得好的地方 ✅

| 维度 | 现状 | 评分 |
|------|------|------|
| **知识组织** | Area → Project → Task 三层结构清晰 | 8/10 |
| **元数据规范** | Front Matter 统一，title/summary/tags/version 齐全 | 8/10 |
| **自动化构建** | build_site_data.py 生成搜索索引、图谱、每日精选 | 7/10 |
| **内容校验** | validate_content.py 验证必填字段和死链 | 7/10 |
| **CI/CD** | GitHub Actions 自动构建部署 | 8/10 |
| **双向链接** | 支持 `[[WikiLink]]` 语法 | 7/10 |

### 1.2 需要改进的地方 ⚠️

| 问题 | 严重程度 | 说明 |
|------|----------|------|
| **缺少测试驱动** | 🔴 高 | 没有 TDD，修改可能破坏现有功能 |
| **缺乏计划管理** | 🔴 高 | 任务没有结构化跟踪，PR 无审查流程 |
| **Subagent 能力** | 🔴 高 | 无法并行处理多任务，长时间工作可能偏离 |
| **知识验证不足** | 🟡 中 | validate_content.py 只检查格式，不验证内容逻辑 |
| **没有版本化** | 🟡 中 | PRD 说要 Docusaurus 版本化，实际用 Jekyll 无版本 |
| **Agent 接口简陋** | 🟡 中 | 只是静态 JSON，缺少真正的 API 接口 |
| **缺少 Schema** | 🟡 中 | 没有 JSON Schema 定义，机器可读性不足 |

---

## 二、Superpowers 工程化改造计划

### 2.1 核心改造方向

```
当前状态                    目标状态
─────────────────────────────────────────────
Jekyll 静态站点    →    增强型 Jekyll + 工具链
手动任务管理       →    结构化 Plan + Subagent 执行
无测试             →    TDD 内容校验 + 回归测试
单线程开发         →    Git Worktree 并行开发
无代码审查         →    Plan Review Gate
```

### 2.2 实施计划 (按 Superpowers 工作流)

#### Phase 1: 基础设施工程化 [1-2天]

**TASK-1.1: 添加 TDD 测试框架**
- 文件: `tools/test_content.py`
- 验证: 每个知识条目的 front matter 完整性
- 验证: WikiLink 死链检测
- 验证: 内容长度合理性
- 验证: 标签一致性

**TASK-1.2: 创建 Plan 模板系统**
- 文件: `docs/plans/`
- 模板: `TASK-000-标题.md`
- 结构: 背景 → 目标 → 具体步骤 → 验证标准 → 风险

**TASK-1.3: 建立 Git Worktree 工作流**
- 脚本: `tools/git-worktree.sh`
- 功能: 创建基于 Plan 的独立工作分支

**TASK-1.4: 添加 CI/CD 质量门禁**
- 文件: `.github/workflows/quality-gate.yml`
- 步骤: lint → test → validate → build

#### Phase 2: 知识工程化增强 [2-3天]

**TASK-2.1: 增强元数据 Schema**
```yaml
# 目标 Schema
id: "kw-ai-llm-001"        # 唯一标识
type: "principle"          # principle|method|glossary|decision|area|project|task-pattern
identity: "architect"      # 身份归属
field: "ai"                # 领域
confidence: "high"         # high|medium|low
applicability: []          # 适用场景
non_applicability: []      # 非适用场景
skill_ref: ""              # 关联 uSkills
test_cases: []             # 验证用例
```

**TASK-2.2: 添加知识验证用例**
- 每个知识条目添加 `test_cases` 字段
- 示例: "当 X 场景发生时，应产生 Y 结果"
- CI 自动运行用例验证

**TASK-2.3: 增强双向链接系统**
- 自动生成反向链接索引
- 依赖关系图谱可视化
- 循环依赖检测

#### Phase 3: Subagent 开发工作流 [1-2天]

**TASK-3.1: 创建 Subagent 任务分发脚本**
- 文件: `tools/dispatch_task.py`
- 功能: 将 Plan 分解为子任务，分配给不同 agent

**TASK-3.2: 建立两阶段审查 Gate**
- Stage 1: 规格合规性 (是否符合 Plan)
- Stage 2: 代码质量 (是否符合规范)

**TASK-3.3: 编写 Superpowers 技能库**
- 目录: `skills/`
- 技能: `brainstorming`, `writing-plans`, `test-driven-development`, `systematic-debugging`

#### Phase 4: 文档与知识图谱增强 [1天]

**TASK-4.1: 增强搜索索引**
- 添加 semantic chunk 支持
- 支持按 `type` 筛选
- 支持按 `confidence` 筛选

**TASK-4.2: 知识图谱 2.0**
- 全局知识依赖图
- Area → Project → Task 层级可视化
- 知识新鲜度热力图

---

## 三、Superpowers 核心技能集成

### 3.1 必须激活的技能

| 技能 | 用途 | 触发时机 |
|------|------|----------|
| `brainstorming` | 需求澄清、设计讨论 | 任何新功能/条目添加前 |
| `writing-plans` | 任务分解 | 设计确认后 |
| `test-driven-development` | 内容校验 | 添加/修改知识条目时 |
| `systematic-debugging` | 问题排查 | CI 失败、死链检测失败时 |
| `requesting-code-review` | 质量把关 | 提交 PR 前 |

### 3.2 工作流触发规则

```
用户请求 → 检查相关技能 → 执行工作流 → 人工确认 → 继续执行
    ↓
┌─────────────────────────────────────┐
│  brainstorming (如果是新需求)        │
│       ↓ 确认设计                      │
│  writing-plans (分解任务)            │
│       ↓ 确认计划                      │
│  test-driven-development (编写测试)  │
│       ↓ 测试通过                      │
│  编码实现                            │
│       ↓ 完成                          │
│  requesting-code-review (审查)       │
│       ↓ 通过                          │
│  finishing-a-development-branch      │
└─────────────────────────────────────┘
```

---

## 四、具体改造文件清单

### 4.1 新增文件

```
uWisdom/
├── tools/
│   ├── test_content.py              # [NEW] TDD 测试框架
│   ├── dispatch_task.py             # [NEW] Subagent 任务分发
│   ├── check_dependencies.py         # [NEW] 依赖关系检查
│   └── semantic_search.py           # [ENHANCED] 语义搜索增强
├── skills/                          # [NEW] Superpowers 技能库
│   ├── brainstorming.md
│   ├── writing-plans.md
│   ├── test-driven-development.md
│   └── systematic-debugging.md
├── docs/
│   ├── plans/                       # [NEW] 任务计划存储
│   │   └── TEMPLATE.md
│   └── schemas/                      # [NEW] JSON Schema
│       └── knowledge-unit.schema.json
├── .github/workflows/
│   ├── quality-gate.yml             # [NEW] 质量门禁
│   └── pr-review.yml                # [NEW] PR 自动审查
└── CLAUDE.md                        # [NEW] Agent 上下文说明
```

### 4.2 修改文件

| 文件 | 修改内容 |
|------|----------|
| `tools/build_site_data.py` | 添加 chunk 提取、Schema 验证 |
| `tools/validate_content.py` | 增强为 TDD 测试框架 |
| `docs/uWisdom-PRD.md` | 更新技术方案，同步 Superpowers 方法论 |
| `.github/workflows/pages.yml` | 集成质量门禁 |
| `README.md` | 添加 Superpowers 使用说明 |

---

## 五、TDD 测试框架设计

### 5.1 测试用例示例

```python
# tools/test_content.py

class TestKnowledgeUnit:
    """知识单元测试基类"""
    
    def test_front_matter_required_fields(self):
        """必须包含: title, summary, type, version"""
        assert front.get("title")
        assert front.get("summary")
        assert front.get("type") in VALID_TYPES
        
    def test_wiki_links_valid(self):
        """所有 WikiLink 必须指向存在的条目"""
        for link in wiki_links:
            assert resolve_link(link) in all_urls
            
    def test_self_contained_examples(self):
        """示例必须可独立验证"""
        # 检查示例是否有明确的输入输出
        pass

class TestKnowledgeGraph:
    """知识图谱测试"""
    
    def test_no_circular_dependencies(self):
        """不允许循环依赖"""
        pass
        
    def test_dangling_references(self):
        """不允许悬空引用"""
        pass
```

### 5.2 CI 集成

```yaml
# .github/workflows/quality-gate.yml
- name: Run TDD Tests
  run: python3 tools/test_content.py --tdd

- name: Validate Content
  run: python3 tools/validate_content.py

- name: Check Dependencies
  run: python3 tools/check_dependencies.py
```

---

## 六、Superpowers 上下文配置

### 6.1 CLAUDE.md 内容

```markdown
# uWisdom 开发上下文

## 项目性质
个人知识操作系统，基于"驾驭工程可读性原则"

## 核心工作流 (Superpowers)
1. brainstorming → 需求澄清
2. writing-plans → 任务分解 (2-5分钟粒度)
3. test-driven-development → 测试先行
4. executing-plans → 执行 + 两阶段审查
5. requesting-code-review → 人工确认

## 关键原则
- 工程可读性优先
- 测试必须先于代码
- 计划必须具体可执行
- 质量门禁不可绕过

## 目录约定
- `docs/knowledge-base/` - 核心知识库
- `docs/identities/` - 身份地图
- `tools/` - 构建和验证工具
- `skills/` - Superpowers 技能库

## 触发规则
- 添加知识条目 → 必须先 brainstorming
- 修改现有条目 → 必须先写测试
- 提交 PR → 必须经过 requesting-code-review
```

---

## 七、风险评估与应对

| 风险 | 概率 | 影响 | 应对方案 |
|------|------|------|----------|
| Superpowers 插件安装失败 | 低 | 中 | 提供手动安装指南 |
| TDD 测试覆盖率不足 | 中 | 中 | 渐进式添加，从核心条目开始 |
| Agent 执行偏离 Plan | 中 | 高 | 强制人工 checkpoint |
| Jekyll 迁移到 Docusaurus 成本高 | 高 | 中 | 保持 Jekyll，渐进增强工具链 |

---

## 八、行动优先级

### P0 (立即执行)
1. ✅ 安装 Superpowers 插件
2. ✅ 创建 CLAUDE.md 上下文文件
3. ✅ 添加 TDD 测试框架 `test_content.py`
4. ✅ 更新 CI 质量门禁

### P1 (本周内)
5. 创建 Plan 模板系统
6. 增强元数据 Schema
7. 添加 Superpowers 技能库
8. 建立 Git Worktree 工作流

### P2 (下阶段)
9. 实现 Subagent 任务分发
10. 知识图谱 2.0
11. 语义搜索增强
12. Agent 接口标准化

---

## 九、验证标准

### 工程化成功的标志
- [ ] `python3 tools/test_content.py` 可运行，覆盖率 > 80%
- [ ] 每个知识条目有完整的 front matter
- [ ] WikiLink 死链率 = 0
- [ ] CI 包含 lint → test → validate → build 完整流程
- [ ] Agent 执行新任务前自动触发 brainstorming
- [ ] 提交前自动触发 requesting-code-review
