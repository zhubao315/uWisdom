---
title: 全栈原型开发
summary: 快速构建端到端功能原型的方法与工具链
permalink: /knowledge-base/themes/full-stack-prototyping.html
tags:
  - architecture
  - ai
---

# 全栈原型开发

所属领域：[全栈工程师]({{ '/knowledge-base/domains/full-stack-engineer.html' | relative_url }})

## 定义

快速构建端到端功能原型的方法、工具链和最佳实践，用于验证想法、展示效果和迭代设计。

## 核心要点

### 技术选型

- 前端：Vite + React/Vue、Tailwind CSS、shadcn/ui
- 后端：Next.js API Routes、FastAPI、Express
- 数据库：SQLite（原型）→ PostgreSQL（生产）
- 部署：Vercel / Netlify / Fly.io 一键部署

### AI 辅助原型

- 用 AI 生成初始代码框架
- Cursor / Copilot 加速开发
- 用 LLM 生成测试数据和示例内容

### 原型原则

- 先跑通核心流程，再优化边界条件
- 用 mock 数据替代未就绪的外部依赖
- 可演示 > 可扩展（原型阶段）

## 延伸阅读

- [全栈工程师]({{ '/knowledge-base/domains/full-stack-engineer.html' | relative_url }})
- [LLM 应用架构]({{ '/knowledge-base/themes/llm-application-architecture.html' | relative_url }})
