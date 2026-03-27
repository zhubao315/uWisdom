---
title: LLM 应用架构
summary: 构建围绕模型、上下文、工具和工作流的 LLM 应用系统架构
permalink: /knowledge-base/themes/llm-application-architecture.html
type: principle
identity: architect
field: ai
tags: [ai, architecture, llm, rag, prompt-engineering]
version: v1.0.0
confidence: high
applicability:
  - 构建新的 LLM 应用系统时
  - 评估和优化现有 LLM 应用时
  - 进行模型选型和架构决策时
non_applicability:
  - 简单的单次 API 调用场景
  - 不需要上下文管理的简单聊天机器人
---

# LLM 应用架构

所属领域：[人工智能专家]({{ '/knowledge-base/domains/ai-expert.html' | relative_url }})

## 定义

构建围绕大语言模型（Large Language Model）、上下文管理、工具调用和工作流编排的 LLM 应用系统架构。覆盖从模型选型、Prompt 设计、RAG 管线到生产部署的全链路能力建设。

**核心挑战**：LLM 应用架构需要在「能力上限」与「工程成本」之间找到平衡点，既要发挥模型的涌现能力，又要保证系统的可靠性、可观测性和成本可控性。

## 核心要点

### 1. 模型层（Model Layer）

#### 1.1 模型选型决策矩阵

| 维度 | 闭源模型（GPT-4、Claude） | 开源模型（Llama、Mistral） |
|------|---------------------------|----------------------------|
| **能力** | 顶级推理能力，多模态支持 | 顶级需要微调，差距在缩小 |
| **成本** | 按 token 计费，规模大时成本高 | 一次性部署成本，推理成本低 |
| **延迟** | 优化良好，本地化部署可降低 | 取决于硬件配置 |
| **数据安全** | 数据上传云端 | 可完全私有化部署 |
| **定制化** | 有限（Prompt engineering） | 完全可控（微调、LoRA） |
| **适用场景** | 快速验证、高质量需求 | 数据敏感、大规模部署 |

**决策框架**：
- 数据敏感 → 开源私有部署
- 追求顶级能力 → 闭源模型
- 大规模、延迟不敏感 → 开源批量推理
- 复杂推理任务 → 闭源顶级模型

#### 1.2 模型网关（Model Gateway）

```python
# 典型的模型网关架构
class ModelGateway:
    def __init__(self):
        self.providers = {
            'openai': OpenAIAdapter(),
            'anthropic': AnthropicAdapter(),
            'ollama': OllamaAdapter(),  # 本地模型
        }
        self.load_balancer = LeastConnectionsBalancer()
        self.fallback_chain = ['openai', 'anthropic']  # 降级链路
    
    async def chat(self, request: ChatRequest) -> ChatResponse:
        # 1. 路由选择
        provider = self.select_provider(request)
        
        # 2. 请求转换
        adapted_request = provider.adapt(request)
        
        # 3. 限流检查
        if not self.rate_limiter.allow(request.user_id):
            raise RateLimitError()
        
        # 4. 执行调用
        try:
            return await provider.execute(adapted_request)
        except ProviderError:
            return await self.try_fallback(request)
```

**关键能力**：
- **统一接口**：屏蔽不同模型 API 差异
- **负载均衡**：轮询、加权、最少连接
- **降级策略**：主模型失败时自动切换备选
- **成本追踪**：按用户、项目、模型维度统计
- **缓存**：基于语义相似度的结果复用

#### 1.3 模型微调策略

| 方案 | 适用场景 | 成本 | 效果 |
|------|----------|------|------|
| **Zero-shot** | 通用任务 | 无 | 依赖模型本身能力 |
| **Few-shot** | 特定格式/风格 | 无 | 中等提升 |
| **LoRA** | 领域适配、风格迁移 | 中等（GPU 小时） | 高 |
| **QLoRA** | 资源受限场景 | 低 | 接近 LoRA |
| **Full Fine-tune** | 任务特定优化 | 高 | 最高 |

**LoRA 最佳实践**：
- Target Modules 选 4-8 层效果最佳
- Rank 从 8 开始，逐步增加观察效果曲线
- 学习率 1e-4 到 1e-3，warmup 很重要
- 评估集要覆盖目标分布，避免过拟合

### 2. 上下文层（Context Layer）

#### 2.1 Prompt 工程体系

**Prompt 层次结构**：
```
系统层（System Prompt）
    │
    ├── 角色定义（Role Definition）
    ├── 能力边界（Capabilities & Constraints）
    ├── 输出格式（Output Schema）
    └── 安全约束（Safety Rules）
    │
V 背景层（Context / Few-shot Examples）
    │
    ├── 任务描述（Task Description）
    ├── 案例示范（Examples）
    └── 参考信息（Reference Data）
    │
└─ 用户层（User Input）
```

**结构化输出技术**：

```python
# 使用 JSON Schema 约束输出
SYSTEM_PROMPT = """
你是一个专业的知识问答助手。

## 输出格式要求
回答必须严格遵循以下 JSON Schema：
{
    "answer": "string - 直接回答问题",
    "confidence": "high|medium|low - 答案置信度",
    "sources": ["string - 参考来源列表"],
    "reasoning": "string - 推理过程简述"
}

## 回答准则
1. 如果不确定答案，confidence 设为 low，不要编造
2. 只引用你确定存在的信息
3. 推理过程要简洁明了
"""
```

#### 2.2 上下文窗口管理

**切片策略对比**：

| 策略 | 原理 | 优点 | 缺点 |
|------|------|------|------|
| **固定长度** | 按字符/Token 数切片 | 简单、确定性强 | 可能切断语义单元 |
| **语义切片** | 按完整句子/段落切片 | 保持语义完整性 | 实现复杂、切片大小不一 |
| **层次切片** | 文档结构（标题→段落→句子） | 保留层次信息 | 依赖文档格式 |
| **递归切片** | 迭代细分直到满足条件 | 自适应 | 计算开销大 |

**滑动窗口策略**：
```python
def sliding_window_chunk(text: str, chunk_size: int = 1000, overlap: int = 200):
    """保持上下文的滑动窗口切片"""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        
        # 尝试在句子边界截断
        if end < len(text):
            last_period = chunk.rfind('。')
            if last_period > chunk_size * 0.7:
                chunk = chunk[:last_period + 1]
                end = start + len(chunk)
        
        chunks.append({
            'content': chunk,
            'start': start,
            'end': end,
            'overlap': chunks[-1]['content'][-overlap:] if chunks else None
        })
        start = end - overlap
    return chunks
```

**上下文压缩技术**：
- **摘要压缩**：将长对话摘要后保留关键信息
- **重要性筛选**：基于关键词或语义重要性筛选保留内容
- **树形记忆**：分层组织记忆，高层是低层的抽象

### 3. 检索增强层（RAG Layer）

#### 3.1 RAG 架构决策

```
用户问题
    │
    ▼
┌─────────────────┐
│  Query 理解     │ ← 意图识别、关键词提取、问题改写
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐  ┌──────────┐
│ 向量检索 │  │ 关键词检索 │
└───┬───┘  └────┬─────┘
    │           │
    └─────┬─────┘
          ▼
   ┌─────────────┐
   │  结果融合    │ ← RRf、BM25 + Vector 混合
   └──────┬──────┘
          │
    ┌─────┴─────┐
    ▼           ▼
┌────────┐  ┌──────────┐
│重排序   │  │ 去重过滤  │
└────┬────┘  └────┬─────┘
     │            │
     └─────┬──────┘
           ▼
     ┌───────────┐
     │ 上下文组装 │
     └─────┬─────┘
           ▼
      LLM 生成
```

#### 3.2 向量数据库选型

| 数据库 | 适用场景 | 优势 | 劣势 |
|--------|----------|------|------|
| **Pinecone** | 云原生、快速上线 | 全托管、易用性好 | 成本、数据主权 |
| **Weaviate** | 混合搜索需求 | 原生混合检索 | 资源消耗 |
| **Milvus** | 大规模、定制化 | 性能强、可扩展 | 运维复杂 |
| **Qdrant** | Rust 生态 | 性能好、易部署 | 社区较小 |
| **Chroma** | 原型验证 | 轻量、Python 优先 | 不适合生产 |
| **FAISS** | 单机、小规模 | 速度快、无依赖 | 需手动管理 |

#### 3.3 RAG 评估体系

| 指标 | 含义 | 测量方法 |
|------|------|----------|
| **Context Precision** | 检索内容与问题的相关性 | 人工标注 / LLM 评估 |
| **Context Recall** | 相关文档是否被召回 | 人工标注 / 黄金集 |
| **Answer Faithfulness** | 回答是否基于检索内容 | LLM 评估幻觉率 |
| **Answer Relevance** | 回答与问题的相关性 | LLM 评估 |
| **Hit Rate@K** | Top-K 中是否有正确答案 | 精确匹配 |

### 4. 工具与编排层（Tool & Orchestration Layer）

#### 4.1 Function Calling 设计模式

```python
# 结构化工具定义
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description": "在知识库中搜索相关内容",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索查询"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "返回结果数量",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_code",
            "description": "执行 Python 代码",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "要执行的代码"
                    }
                },
                "required": ["code"]
            }
        }
    }
]

# 工具执行循环
async def tool_calling_loop(messages):
    while True:
        response = await llm.chat(messages, tools=tools)
        
        if response.finish_reason == "stop":
            return response.content
        
        if response.finish_reason == "tool_calls":
            for tool_call in response.tool_calls:
                result = await execute_tool(tool_call)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                })
```

#### 4.2 编排框架对比

| 框架 | 适用场景 | 复杂度 | 学习曲线 |
|------|----------|--------|----------|
| **LangChain** | 快速原型、全功能 | 高 | 陡峭 |
| **LangGraph** | 复杂工作流、状态管理 | 高 | 中等 |
| **LlamaIndex** | RAG 场景优先 | 中 | 平缓 |
| **AutoGen** | 多 Agent 协作 | 中 | 中等 |
| **CrewAI** | 多 Agent 任务分解 | 低 | 平缓 |
| **自研** | 特殊需求、性能优化 | 高 | N/A |

**自研建议**：对于简单场景，直接调用 API 更可控；对于复杂生产系统，自研核心编排逻辑 + 选用开源组件更可靠。

#### 4.3 多 Agent 架构模式

**模式一：导演-演员（Director-Actor）**
```
用户请求 → 导演 Agent（规划） → 分发给演员 Agents → 汇总结果
```

**模式二：辩论式（Debate）**
```
问题 → Agent A（正方） → Agent B（反方） → 辩论 N 轮 → 裁判 Agent 裁决
```

**模式三：流水线（Pipeline）**
```
输入 → 预处理 Agent → 核心处理 Agent → 后处理 Agent → 输出
```

### 5. 生产化层（Production Layer）

#### 5.1 评估体系设计

**LLM 应用四维评估框架**：

| 维度 | 指标 | 测量方式 |
|------|------|----------|
| **正确性** | 准确率、幻觉率、引用准确率 | 黄金集评估 |
| **相关性** | 回答与问题的匹配度 | LLM 评估、用户反馈 |
| **延迟** | P50/P95/P99 响应时间 | APM 监控 |
| **成本** | 每千次请求成本 | 计费系统 |

**Golden Dataset 构建**：
```python
golden_dataset = [
    {
        "query": "如何设计一个高可用的微服务架构？",
        "context": ["相关知识库片段..."],
        "expected_answer": "应该包含：服务注册发现、负载均衡、熔断降级...",
        "expected_aspects": ["可用性", "扩展性", "可维护性"],
        "metadata": {
            "difficulty": "medium",
            "category": "architecture",
            "source": "面试题库"
        }
    }
]
```

#### 5.2 安全与合规

**PII 处理流程**：
```
原始输入 → PII 检测 → [匿名化/拒绝/脱敏] → LLM 处理
              │
              ▼
        PII 日志（合规保留）
```

**幻觉检测策略**：
1. **引用验证**：要求模型引用具体来源
2. **置信度输出**：让模型输出置信度，低置信度触发人工复核
3. **事实核查**：LLM 输出后接事实核查 Agent
4. **边界约束**：Prompt 中明确禁止编造信息

#### 5.3 可观测性架构

```python
# 全链路追踪
class LLMObserver:
    def __init__(self):
        self.tracer = Tracer()
        self.metrics = MetricsCollector()
    
    async def trace(self, request: Request, response: Response):
        span = self.tracer.start_span("llm_call")
        
        # 记录请求
        span.set_attribute("model", request.model)
        span.set_attribute("prompt_tokens", response.usage.prompt_tokens)
        span.set_attribute("completion_tokens", response.usage.completion_tokens)
        
        # 性能指标
        self.metrics.histogram(
            "llm_latency_seconds",
            response.latency,
            tags={"model": request.model}
        )
        
        # 质量指标
        self.metrics.gauge(
            "llm_quality_score",
            self.evaluate_quality(response),
            tags={"model": request.model}
        )
        
        span.end()
```

## 常见陷阱与应对

### 陷阱 1：过度依赖 Prompt 工程

**症状**：Prompt 越来越长，越来越复杂，但仍不能稳定解决边界情况。

**应对**：
- Prompt 复杂度 > 2000 tokens 时，考虑用微调
- 定期评估 Prompt 的投入产出比
- 建立 Prompt 版本管理和 A/B 测试机制

### 陷阱 2：RAG 检索质量低

**症状**：LLM 回答总是"根据提供的上下文..."

**应对**：
- 分析检索失败的根因（查询理解？向量质量？切片策略？）
- 建立检索质量的持续监控
- 考虑混合检索 + 重排序

### 陷阱 3：忽视成本

**症状**：月底账单超出预期。

**应对**：
- 从架构层面考虑成本：缓存、模型降级、批量处理
- 建立成本预警机制
- 定期分析 token 消耗分布

## 最佳实践清单

- [ ] 建立模型网关，支持多模型切换和降级
- [ ] Prompt 模板版本化管理
- [ ] RAG 管道可观测：检索质量 + 生成质量
- [ ] 结构化输出，降低解析成本
- [ ] 实现级联降级：复杂推理用强模型，简单任务用弱模型
- [ ] 缓存高频相似查询
- [ ] 全链路追踪：请求 → 检索 → 生成 → 输出
- [ ] 定期用黄金集评估系统质量

## 延伸阅读

- [Agent 工作流设计]({{ '/knowledge-base/themes/agent-workflow-design.html' | relative_url }})
- [人工智能专家]({{ '/knowledge-base/domains/ai-expert.html' | relative_url }})
- [工程交付闭环]({{ '/knowledge-base/themes/engineering-delivery.html' | relative_url }})
