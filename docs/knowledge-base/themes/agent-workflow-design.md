---
title: Agent 工作流设计
summary: 设计单 Agent 与多 Agent 协作的工作流编排系统
permalink: /knowledge-base/themes/agent-workflow-design.html
tags:
  - ai
  - agent
---

# Agent 工作流设计

所属领域：[人工智能专家]({{ '/knowledge-base/domains/ai-expert.html' | relative_url }})

## 定义

设计 AI Agent 的任务拆解、工具调用、记忆管理、多步推理和多 Agent 协作的工作流编排系统。

## 核心要点

### 单 Agent 设计

- 角色定义：系统提示设定 Agent 的能力边界和行为准则
- 工具集：为 Agent 配置可调用的外部工具（搜索、代码执行、数据库查询）
- 记忆管理：短期（对话上下文）+ 长期（向量记忆库）
- 推理链路：ReAct、Plan-and-Execute、Reflection 模式

### 多 Agent 协作

- 角色分工：规划者、执行者、审核者、总结者
- 通信协议：消息格式、状态同步、错误传播
- 编排模式：顺序执行、并行执行、投票聚合、辩论式

### 工程实践

- 状态管理：持久化 Agent 状态，支持断点续跑
- 超时与重试：防止 Agent 陷入死循环
- 人机协作：在关键节点引入人工审批

## 延伸阅读

- [LLM 应用架构]({{ '/knowledge-base/themes/llm-application-architecture.html' | relative_url }})
- [工程交付]({{ '/knowledge-base/themes/engineering-delivery.html' | relative_url }})
