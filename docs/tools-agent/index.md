---
title: 工具 & Agent
summary: uWisdom 的工具链、Agent 接入方式与语义搜索管线
permalink: /tools-agent/
---

# 工具 & Agent

uWisdom 不只是文档站，还要成为 Agent 可读、可调用、可扩展的知识底座。

## 能力总览

<div class="grid">
  <article class="card">
    <h2>Agent 接入入口</h2>
    <p>每个条目页都提供“复制链接，让你的 Agent 学习这条知识”按钮，便于把稳定 URL 直接作为 Agent 上下文入口。</p>
  </article>
  <article class="card">
    <h2>结构化搜索</h2>
    <p>站点提供按领域、标签、版本、书籍、作者的过滤搜索，适合快速浏览和人工查阅。</p>
  </article>
  <article class="card">
    <h2>语义搜索管线</h2>
    <p>通过 OpenAI embeddings 生成条目向量，再用 FAISS 建立近邻索引，实现“问题 -> 自动匹配笔记”的召回基础。</p>
  </article>
</div>

## 语义搜索设计

推荐流程：

1. 从站点 Markdown 提取条目元数据与正文摘要
2. 使用 OpenAI embeddings 生成向量
3. 用 FAISS 构建本地索引
4. 查询时把自然语言问题嵌入同一向量空间
5. 召回最相关的知识条目，再交给 Agent 继续整合

## 仓库内置工具

- `tools/build_site_data.py`：生成站点搜索索引、关系图谱数据和每日精选页面
- `tools/build_semantic_index.py`：使用 OpenAI embeddings + FAISS 构建本地语义索引
- `tools/semantic_query.py`：输入自然语言问题，返回最匹配的知识条目

## 使用说明

```bash
cd /root/uWisdom
python3 tools/build_site_data.py
OPENAI_API_KEY=your_key python3 tools/build_semantic_index.py
OPENAI_API_KEY=your_key python3 tools/semantic_query.py "我想找关于 Agent 工作流和知识调用的笔记"
```

## 说明

- GitHub Pages 是静态托管，适合发布结构化索引与知识内容
- 语义检索在本地工具、CI 或 Agent 服务侧运行更稳妥
- 不建议在前端页面中直接暴露 OpenAI API Key

