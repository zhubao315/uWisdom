---
title: 上下文工程
summary: 优化 LLM 上下文的组织、检索、压缩与管理策略
permalink: /knowledge-base/themes/context-engineering.html
type: principle
identity: architect
field: ai
tags: [ai, llm, context, rag, memory, context-window]
version: v1.0.0
confidence: high
applicability:
  - 构建 RAG 系统时
  - 设计 Agent 记忆系统时
  - 优化长文本处理时
non_applicability:
  - 单次简单调用（上下文极短）
  - 模型本身上下文窗口极小的情况
---

# 上下文工程

所属领域：[人工智能专家]({{ '/knowledge-base/domains/ai-expert.html' | relative_url }})
相关主题：[提示词工程]({{ '/knowledge-base/themes/prompt-engineering.html' | relative_url }}) | [LLM 应用架构]({{ '/knowledge-base/themes/llm-application-architecture.html' | relative_url }})

## 定义

上下文工程（Context Engineering）是优化 LLM 上下文的组织、检索、压缩与管理策略的工程学科，旨在在有限上下文窗口内传递最相关、最有价值的信息。

**核心挑战**：上下文窗口是有限的，但知识是无限的。如何在约束条件下最大化上下文的「信息密度」和「任务相关性」是核心命题。

**与提示词工程的区别**：
- **提示词工程**：关注「如何表达」，即 Prompt 的措辞和结构
- **上下文工程**：关注「传递什么」，即上下文的选取和组织

## 核心概念

### 上下文分层架构

```
┌─────────────────────────────────────────────────────────────┐
│                    上下文窗口 (Context Window)                 │
│                                                            │
│  ┌────────────────────────────────────────────────────┐   │
│  │                  任务上下文 (Task Context)           │   │
│  │  当前任务描述、约束条件、期望输出                      │   │
│  └────────────────────────────────────────────────────┘   │
│                           │                               │
│  ┌────────────────────────────────────────────────────┐   │
│  │                 会话上下文 (Session Context)         │   │
│  │  对话历史、用户偏好、本次会话累积的信息               │   │
│  └────────────────────────────────────────────────────┘   │
│                           │                               │
│  ┌────────────────────────────────────────────────────┐   │
│  │                 检索上下文 (Retrieved Context)      │   │
│  │  RAG 系统检索的相关文档、知识片段                    │   │
│  └────────────────────────────────────────────────────┘   │
│                           │                               │
│  ┌────────────────────────────────────────────────────┐   │
│  │                 记忆上下文 (Memory Context)         │   │
│  │  Agent 的长期记忆、背景知识、角色设定                │   │
│  └────────────────────────────────────────────────────┘   │
│                                                            │
└─────────────────────────────────────────────────────────────┘
```

### 上下文工程核心问题

| 问题 | 描述 | 解决方向 |
|------|------|----------|
| **相关性** | 如何选择最相关的上下文 | 检索优化、重排序 |
| **完整性** | 如何保证关键信息不丢失 | 信息冗余、摘要 |
| **简洁性** | 如何在有限空间内传递更多信息 | 压缩、摘要、提取 |
| **一致性** | 如何避免上下文矛盾 | 版本控制、事实锚定 |
| **时效性** | 如何处理动态变化的信息 | 增量更新、过期机制 |

## 核心要点

### 1. 检索增强生成（RAG）

#### 1.1 RAG 系统架构

```
用户查询
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│                     RAG Pipeline                            │
│                                                              │
│  ┌───────────┐    ┌───────────┐    ┌───────────┐          │
│  │ Query     │───▶│ Retrieval │───▶│   Rerank  │          │
│  │Transform  │    │   Stage   │    │   Stage   │          │
│  └───────────┘    └───────────┘    └───────────┘          │
│                           │               │                 │
│                           ▼               ▼                 │
│                    ┌───────────────────────────┐            │
│                    │      Context Assembly     │            │
│                    │    (上下文组装策略)        │            │
│                    └───────────────────────────┘            │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
                      LLM 生成
```

#### 1.2 查询转换（Query Transform）

**查询扩展**：
```python
def expand_query(original_query: str, llm) -> list[str]:
    """将单个查询扩展为多个相关查询"""
    prompt = f"""
基于以下查询，生成 3 个不同的表述方式：

原始查询：{original_query}

要求：
1. 使用不同的词汇表达相同的意思
2. 可以从不同角度提问
3. 生成多样化的查询

输出格式：
- 查询1：...
- 查询2：...
- 查询3：...
"""
    
    response = llm.chat(prompt)
    return parse_queries(response)


# 使用示例
original = "如何设计高可用的微服务架构"
expanded_queries = expand_query(original, llm)
# ["微服务架构的高可用性设计方法", "设计容错的分布式系统最佳实践", "保证服务可用性的架构模式"]
```

**查询分解**：
```python
def decompose_query(query: str, llm) -> list[dict]:
    """将复杂查询分解为简单子查询"""
    prompt = f"""
将以下复杂查询分解为可以独立检索的简单子查询：

查询：{query}

分解要求：
1. 识别查询中的各个子主题
2. 每个子查询应该可以单独检索
3. 标注各子查询之间的关系（AND/OR）

输出格式：
[
  {{"sub_query": "...", "aspect": "..."}},
  ...
]
"""
    
    response = llm.chat(prompt)
    return json.loads(response)


# 使用示例
query = "比较 Kafka 和 RabbitMQ 在实时数据处理场景下的性能差异"
sub_queries = decompose_query(query, llm)
# [
#   {"sub_query": "Kafka 实时数据处理性能", "aspect": "Kafka"},
#   {"sub_query": "RabbitMQ 实时数据处理性能", "aspect": "RabbitMQ"},
#   {"sub_query": "实时数据处理性能对比", "aspect": "对比"}
# ]
```

**后检索查询重构**：
```python
def refine_query_with_context(
    original_query: str,
    initial_results: list,
    llm
) -> str:
    """基于初始检索结果重构查询"""
    context_summary = summarize_results(initial_results)
    
    prompt = f"""
基于以下检索结果，重新表述用户查询：

原始查询：{original_query}

检索结果摘要：
{context_summary}

请重新表述查询，使其更精确地聚焦于尚未检索到的信息。
"""
    
    return llm.chat(prompt)
```

#### 1.3 检索策略

**向量检索**：
```python
class VectorRetriever:
    def __init__(self, vector_store, embedder):
        self.store = vector_store
        self.embedder = embedder
    
    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filters: dict = None,
        hybrid: bool = True
    ) -> list[Document]:
        # 1. 生成查询向量
        query_vector = self.embedder.embed(query)
        
        # 2. 向量检索
        vector_results = await self.store.search(
            vector=query_vector,
            top_k=top_k * 2,  # 预取更多以便重排序
            filters=filters
        )
        
        if hybrid:
            # 3. 关键词检索
            keyword_results = await self.keyword_search(query, top_k)
            
            # 4. 结果融合
            return self.hybrid_fusion(vector_results, keyword_results)
        
        return vector_results[:top_k]
    
    def hybrid_fusion(
        self,
        vector_results: list,
        keyword_results: list,
        method: str = "rrf"  # Reciprocal Rank Fusion
    ) -> list[Document]:
        if method == "rrf":
            return self.rrf_fusion(vector_results, keyword_results)
        elif method == "distributed":
            return self.distributed_fusion(vector_results, keyword_results)
        else:
            return vector_results
    
    def rrf_fusion(
        self,
        vector_results: list,
        keyword_results: list,
        k: float = 60
    ) -> list[Document]:
        """倒数排名融合"""
        scores = {}
        
        # 向量检索得分
        for rank, doc in enumerate(vector_results):
            doc_id = doc.id
            scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank + 1)
            scores[f"{doc_id}_source"] = "vector"
        
        # 关键词检索得分
        for rank, doc in enumerate(keyword_results):
            doc_id = doc.id
            scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank + 1)
            scores[f"{doc_id}_source"] = "keyword"
        
        # 按得分排序
        sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
        
        # 返回排序后的文档
        all_docs = {doc.id: doc for doc in vector_results + keyword_results}
        return [all_docs[doc_id] for doc_id in sorted_ids if doc_id in all_docs]
```

**混合检索配置**：
```python
# 混合检索权重配置
HYBRID_CONFIGS = {
    "balanced": {
        "vector_weight": 0.5,
        "keyword_weight": 0.5,
        "alpha": 0.5  # BM25 权重
    },
    "semantic_focused": {
        "vector_weight": 0.8,
        "keyword_weight": 0.2,
        "alpha": 0.3
    },
    "keyword_focused": {
        "vector_weight": 0.3,
        "keyword_weight": 0.7,
        "alpha": 0.7
    }
}
```

#### 1.4 重排序（Re-ranking）

```python
class ContextualReranker:
    def __init__(self, reranker_model):
        self.model = reranker_model
    
    async def rerank(
        self,
        query: str,
        documents: list[Document],
        top_k: int = 5
    ) -> list[tuple[Document, float]]:
        """
        使用重排序模型重新排序检索结果
        """
        # 1. 准备输入
        pairs = [(query, doc.content) for doc in documents]
        
        # 2. 批量计算相关性分数
        scores = await self.model.score(pairs)
        
        # 3. 按分数排序
        ranked = sorted(
            zip(documents, scores),
            key=lambda x: x[1],
            reverse=True
        )
        
        return ranked[:top_k]


class DiversityReranker:
    """多样性重排序，避免结果重复"""
    
    def __init__(self, embedder):
        self.embedder = embedder
    
    def rerank_with_diversity(
        self,
        query: str,
        documents: list[Document],
        top_k: int = 5,
        diversity_threshold: float = 0.8
    ) -> list[Document]:
        """
        MMR (Maximal Marginal Relevance) 策略
        """
        results = []
        remaining = documents.copy()
        
        while len(results) < top_k and remaining:
            best_doc = None
            best_score = float('-inf')
            
            for doc in remaining:
                # 相关性分数
                relevance = doc.relevance_score
                
                # 多样性分数（与已选文档的平均相似度）
                if results:
                    similarities = []
                    doc_vec = self.embedder.embed(doc.content)
                    for selected in results:
                        selected_vec = self.embedder.embed(selected.content)
                        sim = cosine_similarity(doc_vec, selected_vec)
                        similarities.append(sim)
                    diversity = 1 - statistics.mean(similarities)
                else:
                    diversity = 1.0
                
                # MMR 分数
                mmr_score = 0.5 * relevance + 0.5 * diversity
                
                if mmr_score > best_score:
                    best_score = mmr_score
                    best_doc = doc
            
            if best_doc:
                results.append(best_doc)
                remaining.remove(best_doc)
            else:
                break
        
        return results
```

### 2. 文档切片策略

#### 2.1 切片方法对比

| 方法 | 原理 | 优点 | 缺点 |
|------|------|------|------|
| **固定长度** | 按字符/Token 切片 | 简单、快速 | 可能切断语义单元 |
| **语义切片** | 按完整句子/段落切片 | 保持语义完整 | 实现复杂 |
| **层次切片** | 按文档结构切片 | 保留层次信息 | 依赖文档格式 |
| **Agent 切片** | LLM 决定切片点 | 最智能 | 成本高 |
| **递归切片** | 迭代细分直到满足条件 | 自适应 | 计算开销大 |

#### 2.2 语义切片实现

```python
class SemanticChunker:
    def __init__(self, embedder, llm):
        self.embedder = embedder
        self.llm = llm
    
    def chunk(self, document: str, max_tokens: int = 500) -> list[dict]:
        """语义感知的文档切片"""
        
        # 1. 句子边界识别
        sentences = self.split_sentences(document)
        
        # 2. 识别主题边界
        topic_boundaries = self.identify_topic_boundaries(sentences)
        
        # 3. 按主题分组
        chunks = self.group_by_topics(sentences, topic_boundaries)
        
        # 4. 合并过小的块，拆分过大的块
        optimized_chunks = self.optimize_chunks(chunks, max_tokens)
        
        # 5. 添加元信息
        return self.enrich_chunks(optimized_chunks)
    
    def identify_topic_boundaries(self, sentences: list[str]) -> list[int]:
        """识别主题边界"""
        if len(sentences) <= 3:
            return []
        
        # 计算相邻句子的语义相似度
        boundaries = []
        embeddings = self.embedder.embed_batch(sentences)
        
        for i in range(1, len(embeddings)):
            similarity = cosine_similarity(embeddings[i-1], embeddings[i])
            
            # 相似度突然下降表示主题边界
            if similarity < 0.5:  # 阈值可调
                boundaries.append(i)
        
        return boundaries
    
    def group_by_topics(
        self,
        sentences: list[str],
        boundaries: list[int]
    ) -> list[list[str]]:
        """按主题边界分组"""
        chunks = []
        start = 0
        
        for boundary in boundaries:
            chunks.append(sentences[start:boundary])
            start = boundary
        
        if start < len(sentences):
            chunks.append(sentences[start:])
        
        return chunks
    
    def optimize_chunks(
        self,
        chunks: list[list[str]],
        max_tokens: int
    ) -> list[list[str]]:
        """合并小块，拆分大块"""
        optimized = []
        
        for chunk in chunks:
            chunk_text = "".join(chunk)
            chunk_tokens = count_tokens(chunk_text)
            
            if chunk_tokens < max_tokens * 0.5 and optimized:
                # 合并到上一个块
                optimized[-1].extend(chunk)
            elif chunk_tokens > max_tokens:
                # 递归拆分
                sub_chunks = self.recursive_split(chunk, max_tokens)
                optimized.extend(sub_chunks)
            else:
                optimized.append(chunk)
        
        return optimized
```

#### 2.3 智能切片（LLM 驱动）

```python
class LLMDrivenChunker:
    def __init__(self, llm):
        self.llm = llm
    
    async def chunk_document(self, document: str) -> list[dict]:
        """使用 LLM 智能切片"""
        prompt = f"""
请分析以下文档的结构，并将其切分为语义连贯的片段。

文档：
{document}

切片要求：
1. 每个片段应该是一个完整的语义单元
2. 片段长度建议在 300-800 tokens 之间
3. 标记每个片段的主题
4. 识别片段之间的关系

输出格式（JSON数组）：
[
  {{
    "content": "片段内容...",
    "topic": "主题标签",
    "start_line": 1,
    "importance": "high/medium/low"
  }}
]
"""
        
        response = await self.llm.chat(prompt)
        return json.loads(extract_json(response))
```

### 3. 上下文压缩

#### 3.1 摘要压缩

```python
class ContextCompressor:
    def __init__(self, llm):
        self.llm = llm
    
    async def summarize_for_context(
        self,
        document: str,
        query: str,
        max_tokens: int = 500
    ) -> str:
        """
        针对特定查询压缩文档
        """
        prompt = f"""
基于以下查询，从文档中提取最相关的信息：

查询：{query}

文档：
{document}

要求：
1. 只保留与查询相关的内容
2. 保持关键细节和具体信息
3. 尽量使用原文表述
4. 压缩后的内容不超过 {max_tokens} tokens
"""
        
        return await self.llm.chat(prompt)
    
    async def progressive_summarize(
        self,
        context: list[str],
        max_context_tokens: int
    ) -> list[str]:
        """
        渐进式摘要：先摘要再拼接
        """
        compressed = []
        current_tokens = 0
        
        for chunk in context:
            chunk_tokens = count_tokens(chunk)
            
            if current_tokens + chunk_tokens > max_context_tokens:
                # 需要压缩已累积的内容
                if compressed:
                    compressed[-1] = await self.summarize_chunk(compressed[-1])
                    current_tokens = count_tokens(compressed[-1])
            
            compressed.append(chunk)
            current_tokens += chunk_tokens
        
        # 如果仍然超限，继续摘要
        while count_tokens("".join(compressed)) > max_context_tokens and len(compressed) > 1:
            # 合并前两个块并摘要
            merged = compressed[0] + compressed[1]
            summarized = await self.summarize_chunk(merged)
            compressed = [summarized] + compressed[2:]
        
        return compressed
```

#### 3.2 信息提取

```python
class InformationExtractor:
    def __init__(self, llm):
        self.llm = llm
    
    async def extract_for_query(
        self,
        query: str,
        documents: list[str]
    ) -> str:
        """
        从文档中提取回答查询所需的最小信息集
        """
        prompt = f"""
基于以下查询，从提供的文档中提取回答问题所需的最小信息集。

查询：{query}

文档列表：
{[f"[文档{i+1}] {doc}" for i, doc in enumerate(documents)]}

要求：
1. 只提取回答查询所必需的信息
2. 跳过无关的背景信息
3. 保留关键事实、数据、引用
4. 按相关性排序
5. 标注信息来源
"""
        
        return await self.llm.chat(prompt)
```

### 4. 记忆系统设计

#### 4.1 分层记忆架构

```python
class HierarchicalMemory:
    """
    分层记忆系统：
    - 感知记忆：当前对话的原始输入
    - 工作记忆：当前任务的中间状态
    - 情景记忆：相关历史交互
    - 语义记忆：结构化的知识
    """
    
    def __init__(self, vector_store, llm):
        self.vector_store = vector_store
        self.llm = llm
        self.working_memory = []
        self.episodic_memory = []
        self.semantic_memory = {}
    
    async def add(self, content: str, memory_type: str = "perceptual"):
        """添加记忆"""
        if memory_type == "perceptual":
            self.working_memory.append(content)
        elif memory_type == "episodic":
            self.episodic_memory.append({
                "content": content,
                "timestamp": datetime.now()
            })
            # 异步索引到向量存储
            await self.vector_store.add({
                "content": content,
                "type": "episodic"
            })
    
    async def retrieve(self, query: str, memory_types: list = None) -> str:
        """检索相关记忆"""
        types = memory_types or ["episodic"]
        results = []
        
        if "perceptual" in types:
            results.append(self.get_recent_working_memory(query))
        
        if "episodic" in types:
            episodic = await self.vector_store.search(query, top_k=3)
            results.extend([r["content"] for r in episodic])
        
        if "semantic" in types:
            results.extend(self.get_semantic_memory(query))
        
        return "\n".join(results)
    
    def get_recent_working_memory(self, query: str) -> str:
        """从工作记忆中提取相关内容"""
        if not self.working_memory:
            return ""
        
        # 简单策略：返回最近的记忆
        # 复杂策略：可以用 LLM 判断相关性
        recent = self.working_memory[-3:]
        return "\n".join(recent)
```

#### 4.2 记忆压缩与遗忘

```python
class MemoryConsolidation:
    """
    记忆整合：定期压缩和优化记忆
    """
    
    def __init__(self, llm):
        self.llm = llm
        self.access_counts = defaultdict(int)
        self.last_access = {}
    
    async def consolidate(
        self,
        memory_items: list[dict],
        threshold: int = 5
    ) -> list[dict]:
        """
        整合记忆：
        1. 增加访问计数
        2. 合并相关记忆
        3. 遗忘低价值记忆
        """
        consolidated = []
        
        for item in memory_items:
            # 更新访问信息
            self.access_counts[item["id"]] += 1
            self.last_access[item["id"]] = datetime.now()
            
            # 检查是否应该遗忘
            if self.should_forget(item):
                continue
            
            # 检查是否可以合并
            mergeable = self.find_mergeable(item, consolidated)
            if mergeable:
                merged = await self.merge_memories(item, mergeable)
                consolidated.append(merged)
            else:
                consolidated.append(item)
        
        return consolidated
    
    def should_forget(self, item: dict) -> bool:
        """判断是否应该遗忘"""
        # 长时间未访问
        if item["id"] in self.last_access:
            days_since_access = (
                datetime.now() - self.last_access[item["id"]]
            ).days
            if days_since_access > 30:
                return True
        
        # 访问频率过低
        if self.access_counts[item["id"]] < 2:
            return True
        
        return False
    
    async def merge_memories(
        self,
        item1: dict,
        item2: dict
    ) -> dict:
        """合并两条相关记忆"""
        prompt = f"""
请整合以下两条相关记忆为一条：

记忆1：{item1["content"]}
记忆2：{item2["content"]}

要求：
1. 去重，保留独特信息
2. 按时间顺序组织
3. 保留关键细节
"""
        
        merged_content = await self.llm.chat(prompt)
        
        return {
            "id": item1["id"],
            "content": merged_content,
            "created_at": min(item1["created_at"], item2["created_at"]),
            "last_access": datetime.now()
        }
```

### 5. 上下文组装策略

#### 5.1 动态上下文分配

```python
class DynamicContextAllocator:
    """
    根据任务动态分配上下文空间
    """
    
    def __init__(self):
        self.budget_pcts = {
            "task_description": 10,      # 任务描述
            "system_instructions": 15,   # 系统指令
            "retrieved_context": 50,     # 检索上下文
            "conversation_history": 15,   # 对话历史
            "examples": 10               # Few-shot 示例
        }
    
    def allocate(self, total_tokens: int, task_type: str) -> dict:
        """根据任务类型分配上下文空间"""
        if task_type == "simple_qa":
            budget = {
                "task_description": 0.1,
                "retrieved_context": 0.8,
                "examples": 0.1
            }
        elif task_type == "complex_reasoning":
            budget = {
                "task_description": 0.15,
                "retrieved_context": 0.45,
                "conversation_history": 0.25,
                "examples": 0.15
            }
        elif task_type == "creative":
            budget = {
                "task_description": 0.2,
                "retrieved_context": 0.3,
                "conversation_history": 0.2,
                "examples": 0.3
            }
        else:
            budget = self.budget_pcts
        
        return {k: int(total_tokens * v) for k, v in budget.items()}


class ContextAssembler:
    def __init__(self, allocator: DynamicContextAllocator):
        self.allocator = allocator
    
    async def assemble(
        self,
        task: dict,
        context_sources: dict
    ) -> str:
        """
        组装最终上下文
        """
        task_type = task.get("type", "general")
        total_budget = task.get("max_tokens", 8000)
        
        allocation = self.allocator.allocate(total_budget, task_type)
        
        parts = []
        remaining_budget = total_budget
        
        # 1. 系统指令（优先）
        system = context_sources.get("system", "")
        system_tokens = min(len(system), allocation["system_instructions"])
        parts.append(system[:system_tokens])
        remaining_budget -= count_tokens(system[:system_tokens])
        
        # 2. 任务描述
        task_desc = context_sources.get("task_description", "")
        task_tokens = min(
            len(task_desc),
            allocation["task_description"]
        )
        parts.append(task_desc[:task_tokens])
        remaining_budget -= count_tokens(task_desc[:task_tokens])
        
        # 3. 检索上下文（核心）
        retrieved = context_sources.get("retrieved_context", [])
        retrieved = self.fit_to_budget(retrieved, allocation["retrieved_context"])
        parts.append(retrieved)
        remaining_budget -= count_tokens(retrieved)
        
        # 4. 对话历史
        history = context_sources.get("conversation_history", [])
        history = self.fit_to_budget(history, allocation["conversation_history"])
        parts.append(history)
        remaining_budget -= count_tokens(history)
        
        # 5. 示例
        examples = context_sources.get("examples", [])
        examples = self.fit_to_budget(examples, allocation["examples"])
        parts.append(examples)
        
        return "\n\n".join(parts)
    
    def fit_to_budget(self, items: list[str], token_budget: int) -> str:
        """将项目列表压缩到 token 预算内"""
        result = []
        current_tokens = 0
        
        for item in items:
            item_tokens = count_tokens(item)
            if current_tokens + item_tokens <= token_budget:
                result.append(item)
                current_tokens += item_tokens
            else:
                # 尝试摘要后加入
                summarized = self.summarize(item, token_budget - current_tokens)
                if summarized:
                    result.append(summarized)
                break
        
        return "\n---\n".join(result)
```

### 6. 评估与优化

#### 6.1 上下文质量评估

```python
class ContextQualityEvaluator:
    """
    评估上下文质量
    """
    
    def __init__(self, llm):
        self.llm = llm
    
    async def evaluate(
        self,
        query: str,
        context: str,
        answer: str
    ) -> dict:
        """
        多维度评估上下文质量
        """
        prompt = f"""
请评估以下上下文的有效性：

查询：{query}

上下文：
{context}

LLM 回答：
{answer}

请从以下维度评估（1-5分）：
1. 相关性：上下文与查询的相关程度
2. 充分性：上下文是否提供了足够的信息来回答查询
3. 简洁性：上下文是否简洁，没有冗余信息
4. 准确性：上下文中的信息是否准确可靠
5. 完整性：回答是否完整，没有遗漏关键点

输出格式（JSON）：
{{
  "relevance": 4,
  "sufficiency": 3,
  "conciseness": 4,
  "accuracy": 5,
  "completeness": 4,
  "overall": 4.0,
  "issues": ["上下文缺少某方面的信息"],
  "suggestions": ["建议补充..."]
}}
"""
        
        response = await self.llm.chat(prompt)
        return json.loads(extract_json(response))
```

#### 6.2 上下文优化循环

```python
class ContextOptimizationLoop:
    """
    上下文优化闭环
    """
    
    def __init__(self, evaluator: ContextQualityEvaluator):
        self.evaluator = evaluator
        self.metrics_history = []
    
    async def optimize(
        self,
        query: str,
        rag_pipeline,
        max_iterations: int = 3
    ) -> tuple[str, list[dict]]:
        """
        迭代优化上下文
        """
        best_context = None
        best_score = 0
        history = []
        
        for iteration in range(max_iterations):
            # 1. 检索上下文
            context = await rag_pipeline.retrieve(query)
            
            # 2. 生成回答
            answer = await self.llm.generate(query, context)
            
            # 3. 评估质量
            metrics = await self.evaluator.evaluate(query, context, answer)
            
            history.append({
                "iteration": iteration + 1,
                "context_length": count_tokens(context),
                "metrics": metrics
            })
            
            if metrics["overall"] > best_score:
                best_score = metrics["overall"]
                best_context = context
            
            # 4. 如果质量达标，停止
            if metrics["overall"] >= 4.5:
                break
            
            # 5. 根据问题调整检索策略
            if metrics["sufficiency"] < 3:
                # 增加检索数量
                rag_pipeline.top_k += 2
            if metrics["completeness"] < 3:
                # 调整查询或重排序策略
                rag_pipeline.use_diversity_rerank = True
        
        return best_context, history
```

## 常见问题与解决方案

### 问题 1：检索结果不相关

**症状**：RAG 返回的内容与查询无关。

**解决方案**：
```python
# 1. 优化查询转换
# 2. 使用混合检索
# 3. 调整重排序策略
# 4. 增加相关性过滤
```

### 问题 2：上下文超出窗口

**症状**：组装后的上下文超过模型限制。

**解决方案**：
```python
# 1. 优先保留高相关性内容
# 2. 摘要压缩低相关性内容
# 3. 分解任务，减少单次上下文需求
# 4. 使用更大的上下文窗口模型
```

### 问题 3：信息冲突

**症状**：上下文中存在矛盾的信息。

**解决方案**：
```python
# 1. 事实核查：在上下文中标注可信度
# 2. 时效性标记：区分新旧信息
# 3. 来源标注：明确信息出处
# 4. 冲突检测：识别并处理矛盾
```

### 问题 4：核心信息丢失

**症状**：关键信息在切片或压缩时丢失。

**解决方案**：
```python
# 1. 重要信息标记：在切片时标注重要性
# 2. 冗余保留：关键信息多出保留
# 3. 增量检索：先检索，再根据回答缺失补充
```

## 最佳实践清单

- [ ] 根据任务类型选择合适的切片策略
- [ ] 使用混合检索提升召回率
- [ ] 重排序后进行多样性检查
- [ ] 实施上下文质量评估闭环
- [ ] 建立记忆系统，支持长期上下文
- [ ] 监控上下文利用率和生成质量
- [ ] 持续优化检索和压缩策略

## 延伸阅读

- [提示词工程]({{ '/knowledge-base/themes/prompt-engineering.html' | relative_url }})
- [LLM 应用架构]({{ '/knowledge-base/themes/llm-application-architecture.html' | relative_url }})
- [Agent 工作流设计]({{ '/knowledge-base/themes/agent-workflow-design.html' | relative_url }})
- [驾驭工程可读性原则]({{ '/knowledge-base/themes/readability-principles.html' | relative_url }})
