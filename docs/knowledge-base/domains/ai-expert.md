---
title: 人工智能专家
summary: 围绕 AIGC、LLM、Agent、RAG 与 AI 应用落地进行研究和实践
permalink: /knowledge-base/domains/ai-expert.html
type: area
identity: architect
field: ai
tags: [ai, agent, llm, rag, aigc, architecture]
version: v1.0.0
confidence: high
applicability:
  - 构建 AI 驱动的应用系统时
  - 评估和选型 AI 解决方案时
  - 设计企业级 AI 平台架构时
non_applicability:
  - 不涉及 AI 的传统软件系统
  - 硬件设备、嵌入式系统（非 AI 相关）
---

# 人工智能专家

## 领域定义

围绕 AIGC（AI Generated Content）、LLM（Large Language Model）、Agent（智能体）、提示工程、RAG（Retrieval-Augmented Generation）与 AI 应用落地进行研究和实践。

这是当前技术变革的核心驱动力，也是 uWisdom 未来 Agent 化的技术底座。核心目标是将 AI 能力系统化、工程化、产品化，而非停留在 POC 层面。

## 对你的价值

### 战略价值

1. **职业主航道**（2024 至今）：AI 能力已成为架构设计的核心考量
2. **知识架构升级**：从"系统架构"走向"知识架构 + 智能架构"双轨并行
3. **效率杠杆**：AI 辅助可以 10x 提升知识产出和工程交付效率

### 能力构建

- 理解 LLM 的能力边界和工程约束
- 掌握 RAG、Agent、Prompt Engineering 等核心技能
- 建立 AI 应用的全栈架构能力
- 形成 AI 落地的方法论和最佳实践

## 核心关注方向

### 1. LLM 应用架构

这是 AI 落地的核心技术栈，覆盖从模型选型到生产部署的全链路。

#### 核心能力矩阵

| 层级 | 关键问题 | 核心技能 | 评估标准 |
|------|----------|----------|----------|
| **模型层** | 如何选型、如何调用、如何降级 | 模型网关设计、成本优化 | 成本/质量比 |
| **上下文层** | 如何管理上下文、如何切片 | Prompt 工程、窗口管理 | 上下文利用率 |
| **RAG 层** | 如何检索、如何融合 | 向量检索、混合搜索 | 召回率、准确率 |
| **工具层** | 如何扩展能力、如何编排 | Function Calling、工作流 | 任务完成率 |
| **生产层** | 如何监控、如何安全 | 可观测性、安全合规 | SLA 达成率 |

#### 深入学习路径

```
入门阶段：
├── 掌握 OpenAI/Claude API 调用
├── 理解 Prompt Engineering 基础
└── 完成第一个 RAG 原型

进阶阶段：
├── 模型选型和成本优化
├── 多模型网关设计
├── RAG 性能调优
└── Function Calling 实践

专家阶段：
├── Multi-Agent 架构设计
├── 微调和 RLHF
├── AI 安全与对齐
└── 企业级 AI 平台建设
```

#### 推荐资源

**书籍**：
- 《Building LLM Applications》- 构建生产级 LLM 应用
- 《Hands-On LLM》- 实践导向的 LLM 开发指南

**课程**：
- Andrej Karpathy 的 LLM 视频
- Full Stack LLM Bootcamp

**论文**：
- RAG 系列：Naive RAG → Sophisticated RAG → RAG vs Fine-tuning
- Agent 系列：ReAct、Plan-and-Execute、Reflexion

**开源项目**：
- LangChain/LangGraph
- LlamaIndex
- AutoGen
- CrewAI

→ [LLM 应用架构]({{ '/knowledge-base/themes/llm-application-architecture.html' | relative_url }})

### 2. Agent 工作流设计

Agent 是 AI 从"工具"进化到"助手"的关键形态。

#### Agent 成熟度模型

| 级别 | 特征 | 能力 | 典型场景 |
|------|------|------|----------|
| **L1** | 响应式 | 被动响应用户请求 | 问答机器人 |
| **L2** | 工具调用 | 可调用外部工具 | 助手类应用 |
| **L3** | 任务执行 | 多步推理和执行 | 代码助手 |
| **L4** | 协作式 | 多 Agent 协作 | 复杂工作流 |
| **L5** | 自主式 | 长期目标追求 | 研究 Agent |

#### 核心设计模式

1. **ReAct**：推理 + 行动的循环模式
2. **Plan-and-Execute**：规划与执行分离
3. **Reflexion**：自我反思和纠错
4. **Memory**：分层记忆系统

#### 工程化要点

- **状态管理**：持久化、checkpoint、回滚
- **超时处理**：防止 Agent 陷入死循环
- **人机协作**：关键决策点人工确认
- **可观测性**：全链路追踪和问题诊断

→ [Agent 工作流设计]({{ '/knowledge-base/themes/agent-workflow-design.html' | relative_url }})

### 3. RAG 与知识系统

RAG 是将私有知识与 LLM 结合的核心范式。

#### RAG 架构演进

```
Phase 1: Naive RAG
  用户问题 → 向量检索 → 组装上下文 → LLM 生成
  
Phase 2: Sophisticated RAG
  用户问题 → Query 改写 → 混合检索 → 重排序 → LLM 生成
  
Phase 3: RAG Pipeline
  用户问题 → 意图识别 → Router → 多路检索 → 融合 → LLM 生成
```

#### 知识库建设生命周期

1. **规划**：确定知识边界、来源、更新策略
2. **采集**：文档解析、结构化、清洗
3. **索引**：切片策略、向量化的选择
4. **检索**：查询理解、检索优化
5. **生成**：上下文组装、答案生成
6. **评估**：质量监控、持续优化
7. **迭代**：知识更新、版本管理

#### 质量评估框架

| 维度 | 指标 | 测量方法 |
|------|------|----------|
| **检索质量** | 召回率、精确率 | 黄金集评估 |
| **生成质量** | 准确性、相关性 | LLM 评估、人工评估 |
| **用户体验** | 响应时间、满意度 | 用户反馈 |

### 4. 企业级 AI 落地

从 POC 到生产的跨越是 AI 落地的最大挑战。

#### AI 平台架构参考

```
┌─────────────────────────────────────────────────────────┐
│                    AI 应用层                             │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │
│  │ 客服    │  │ 文档问答 │  │ 代码助手 │  │ 分析师  │   │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘   │
└───────┼────────────┼────────────┼────────────┼──────────┘
        └────────────┴─────┬──────┴────────────┘
                           ▼
┌─────────────────────────────────────────────────────────┐
│                   AI 能力平台                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   LLM 网关   │  │   RAG 引擎   │  │  Agent 编排  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Prompt 管理 │  │   评估系统   │  │   监控系统   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────┐
│                   模型服务层                             │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │
│  │ GPT-4   │  │ Claude  │  │ Llama   │  │ Embedding│   │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘   │
└─────────────────────────────────────────────────────────┘
```

#### 从 POC 到生产的 checklist

**基础设施**：
- [ ] 高可用部署，多区域容灾
- [ ] 自动扩缩容，应对流量峰值
- [ ] 成本监控和预警机制
- [ ] 数据安全和隐私保护

**质量保障**：
- [ ] 黄金集测试，覆盖核心场景
- [ ] A/B 测试，持续优化效果
- [ ] 质量监控，实时发现问题
- [ ] 反馈闭环，持续改进

**运营保障**：
- [ ] 运维手册和 SOP
- [ ] 故障应急响应机制
- [ ] 定期评估和优化
- [ ] 知识库更新流程

## 典型 Project

### Project 1：LLM 应用架构设计

**目标**：为新项目设计 LLM 应用架构方案

**关键交付物**：
- 模型选型报告
- 技术架构图
- 成本估算
- POC 实现

**验收标准**：
- 支持多模型切换
- RAG 召回率 > 80%
- 端到端延迟 < 3s

### Project 2：Agent 工作流搭建

**目标**：构建支持多步骤推理的 AI Agent

**关键交付物**：
- Agent 角色定义
- 工具集设计
- 工作流编排代码
- 测试用例

**验收标准**：
- 支持断点续跑
- 人机协作机制可用
- 全链路可观测

### Project 3：企业级 AI 落地方案

**目标**：推动 AI 在企业场景的规模化落地

**关键交付物**：
- AI 平台架构设计
- POC 演示
- 落地路线图
- ROI 分析

**验收标准**：
- 通过评审并立项
- 覆盖至少 3 个核心场景
- ROI 可量化

### Project 4：个人知识系统 Agent 化（uWisdom）

**目标**：让 uWisdom 成为真正的 AI-Native 知识操作系统

**关键方向**：
- 智能知识推荐
- 自动知识关联发现
- Agent 辅助知识创作
- 语义搜索增强

**愿景**：
> uWisdom 不只是存储知识的仓库，而是能够主动发现知识关联、辅助知识创作、促进知识演进的智能伙伴。

## 标杆人物

### 技术领域

- **Andrej Karpathy**：LLM 和计算机视觉领域的思想领袖，OpenAI 创始成员
- **Andrew Ng**：AI 教育先驱，Coursera 创始人
- **Jim Fan**（NVIDIA）：AI Agent 和具身智能专家

### 工程实践

- **Harrison Chase**（LangChain）：LLM 应用框架的布道者
- **Jerry Liu**（LlamaIndex）：RAG 领域的实践者
- **Sam Altman**（OpenAI）：AGI 愿景的推动者

### 中国力量

- **李沐**（Amazon）：MLSys 领域的实践者，动手学深度学习系列作者
- **唐杰**（清华大学）：知识图谱和大模型专家
- **刘知远**（清华大学）：NLP 和大模型专家

## 延伸阅读

### 内部链接

- [LLM 应用架构]({{ '/knowledge-base/themes/llm-application-architecture.html' | relative_url }})
- [Agent 工作流设计]({{ '/knowledge-base/themes/agent-workflow-design.html' | relative_url }})
- [云计算与云原生]({{ '/knowledge-base/domains/cloud-native.html' | relative_url }})
- [工程交付闭环]({{ '/knowledge-base/themes/engineering-delivery.html' | relative_url }})

### 外部资源

**Newsletter**：
- The Batch (Andrew Ng)
- Last Week in AI
- Import AI

**技术社区**：
- Hacker News
- Reddit r/MachineLearning
- V2EX AI 节点

**会议**：
- NeurIPS、ICML、ACL（学术）
- Google I/O、Microsoft Build、AWS re:Invent（工业）
