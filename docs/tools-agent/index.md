---
title: 工具 & Agent
summary: uWisdom 的工具链、Agent 接入方式与语义搜索管线
permalink: /tools-agent/
---

<section class="hero">
  <div class="eyebrow">Tools & Agents</div>
  <h1>工具 & Agent</h1>
  <p><strong>打通 AI 能力，让知识被精准调用。</strong></p>
  <p class="meta">API 接入 · 代码示例 · 语义搜索 · Agent 工作流 · 实时 Demo</p>
</section>

## 能力总览

<div class="grid">
  <article class="card feature-card">
    <div class="card-icon">🔗</div>
    <h3>Agent 接入入口</h3>
    <p>每个条目页都提供「复制链接，让你的 Agent 学习这条知识」按钮，便于把稳定 URL 直接作为 Agent 上下文入口。</p>
  </article>
  <article class="card feature-card">
    <div class="card-icon">🔍</div>
    <h3>结构化搜索</h3>
    <p>站点提供按领域、标签、版本、书籍、作者的过滤搜索，适合快速浏览和人工查阅。</p>
  </article>
  <article class="card feature-card">
    <div class="card-icon">🧠</div>
    <h3>语义搜索管线</h3>
    <p>通过 OpenAI embeddings 生成条目向量，再用 FAISS 建立近邻索引，实现「问题 -> 自动匹配笔记」的召回基础。</p>
  </article>
  <article class="card feature-card">
    <div class="card-icon">⚡</div>
    <h3>工作流引擎</h3>
    <p>支持多 Agent 协作、任务分解、工具调用与记忆管理的完整工作流编排系统。</p>
  </article>
</div>

## 快速开始

### 一、语义搜索

```bash
# 1. 构建站点数据
cd /home/zb/uWisdom
python3 tools/build_site_data.py

# 2. 生成语义索引
OPENAI_API_KEY=your_key python3 tools/build_semantic_index.py

# 3. 自然语言查询
OPENAI_API_KEY=your_key python3 tools/semantic_query.py "我想找关于 Agent 工作流和知识调用的笔记"
```

### 二、Agent 调用示例

```python
import requests

# 获取知识条目用于 Agent 上下文
def get_entry_for_agent(url):
    response = requests.get(url + ".json")
    return response.json()

# 示例：获取 Agent 工作流设计的结构化内容
entry = get_entry_for_agent("https://zhubao315.github.io/uWisdom/knowledge-base/themes/agent-workflow-design.html")
print(entry["title"], entry["summary"])
```

### 三、REST API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/.json` | GET | 获取当前条目的完整结构化数据 |
| `/search/` | GET | 全文搜索，支持 `q` 参数 |
| `/knowledge-base/` | GET | 知识库索引，按领域分类 |

## 语义搜索设计

推荐流程：

1. 从站点 Markdown 提取条目元数据与正文摘要
2. 使用 OpenAI embeddings 生成向量
3. 用 FAISS 构建本地索引
4. 查询时把自然语言问题嵌入同一向量空间
5. 召回最相关的知识条目，再交给 Agent 继续整合

## 仓库内置工具

<div class="tool-grid">
  <article class="tool-item">
    <h4><code>tools/build_site_data.py</code></h4>
    <p>生成站点搜索索引、关系图谱数据和每日精选页面</p>
    <div class="tool-tags">
      <span class="tag">索引</span>
      <span class="tag">图谱</span>
      <span class="tag">精选</span>
    </div>
  </article>
  <article class="tool-item">
    <h4><code>tools/build_semantic_index.py</code></h4>
    <p>使用 OpenAI embeddings + FAISS 构建本地语义索引</p>
    <div class="tool-tags">
      <span class="tag">向量</span>
      <span class="tag">语义</span>
      <span class="tag">FAISS</span>
    </div>
  </article>
  <article class="tool-item">
    <h4><code>tools/semantic_query.py</code></h4>
    <p>输入自然语言问题，返回最匹配的知识条目</p>
    <div class="tool-tags">
      <span class="tag">查询</span>
      <span class="tag">RAG</span>
      <span class="tag">召回</span>
    </div>
  </article>
  <article class="tool-item">
    <h4><code>tools/validate_content.py</code></h4>
    <p>校验内容完整性、死链检测、Front Matter 验证</p>
    <div class="tool-tags">
      <span class="tag">校验</span>
      <span class="tag">质量</span>
      <span class="tag">CI</span>
    </div>
  </article>
</div>

## Agent 工作流演示

### 单 Agent 架构

<div class="mermaid-container">
<div class="mermaid">
graph LR
    User[用户] -->|输入| Prompt[Prompt]
    Prompt -->|理解| LLM[LLM]
    LLM -->|推理| Thought[思考]
    Thought -->|决策| Action[行动]
    Action -->|调用工具| Tool[工具]
    Tool -->|结果| LLM
    Action -->|输出| Response[响应]
    
    subgraph 记忆
    Memory[记忆系统]
    end
    
    LLM --> Memory
    Memory --> LLM
</div>
</div>

### 多 Agent 协作模式

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| 导演模式 | 一个 Agent 协调多个专家 Agent | 复杂任务分解 |
| 辩论模式 | 多 Agent 对抗性讨论 | 方案评审 |
| 流水线模式 | Agent 串行处理数据流 | 内容生成 |
| 并行模式 | 多个 Agent 同时处理子任务 | 市场调研 |
| 层级模式 | Agent 嵌套子 Agent | 系统设计 |

## 相关知识

- [Agent 工作流设计](/knowledge-base/themes/agent-workflow-design.html) — 单 Agent 与多 Agent 协作的工作流编排
- [AI 专家](/knowledge-base/domains/ai-expert.html) — AIGC、LLM、Agent、RAG 与 AI 应用落地
- [上下文工程](/knowledge-base/themes/context-engineering.html) — 上下文管理、记忆系统设计

## 说明

- GitHub Pages 是静态托管，适合发布结构化索引与知识内容
- 语义检索在本地工具、CI 或 Agent 服务侧运行更稳妥
- 不建议在前端页面中直接暴露 OpenAI API Key