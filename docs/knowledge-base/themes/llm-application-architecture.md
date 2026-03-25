---
title: LLM 应用架构
summary: 构建围绕模型、上下文、工具和工作流的 LLM 应用系统架构
permalink: /knowledge-base/themes/llm-application-architecture.html
tags:
  - ai
  - architecture
---

# LLM 应用架构

所属领域：[人工智能专家]({{ '/knowledge-base/domains/ai-expert.html' | relative_url }})

## 定义

构建围绕大语言模型、上下文管理、工具调用和工作流编排的 LLM 应用系统架构。覆盖从模型选型、Prompt 设计、RAG 管线到生产部署的全链路。

## 核心要点

### 模型层

- 模型选型：开源 vs 闭源、能力 vs 成本 vs 延迟的三角取舍
- 模型网关：统一接口、负载均衡、降级策略
- 微调与适配：LoRA、QLoRA、RLHF 在特定场景的应用

### 上下文层

- Prompt 工程：系统提示、Few-shot、CoT、结构化输出
- 上下文窗口管理：长文档切片、摘要压缩、滑动窗口
- 记忆系统：短期对话记忆 vs 长期知识记忆

### 检索增强（RAG）

- 文档切片策略：按段落、按语义、按标题层级
- 向量数据库：FAISS、Milvus、Pinecone 选型对比
- 混合检索：向量检索 + 关键词检索 + 重排序

### 工具与编排

- Function Calling：让模型调用外部 API 和工具
- 工作流编排：LangChain、LlamaIndex、自研框架
- 多 Agent 协作：角色分工、通信协议、结果聚合

### 生产化

- 评估体系：准确性、相关性、延迟、成本
- 安全与合规：内容过滤、PII 脱敏、幻觉检测
- 可观测性：日志、追踪、指标监控

## 延伸阅读

- [Agent 工作流设计]({{ '/knowledge-base/themes/agent-workflow-design.html' | relative_url }})
- [人工智能专家]({{ '/knowledge-base/domains/ai-expert.html' | relative_url }})
