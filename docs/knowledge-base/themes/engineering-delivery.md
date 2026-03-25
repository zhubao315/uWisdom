---
title: 工程交付
summary: 从需求到上线的完整工程交付流程与最佳实践
permalink: /knowledge-base/themes/engineering-delivery.html
tags:
  - architecture
---

# 工程交付

所属领域：[全栈工程师]({{ '/knowledge-base/domains/full-stack-engineer.html' | relative_url }})

## 定义

从需求分析、设计、开发、测试到上线的完整工程交付流程，覆盖 CI/CD、代码质量、发布策略和运维保障。

## 核心要点

### 交付流程

- 需求评审 → 技术方案 → 任务拆分 → 迭代开发 → 代码审查 → 测试 → 发布 → 监控
- 每个环节有明确的交付物和验收标准

### CI/CD

- 持续集成：自动化构建、单元测试、代码检查
- 持续部署：环境管理、灰度发布、回滚机制
- Git 工作流：GitFlow / Trunk-based / Feature Branch

### 质量保障

- 代码审查：每次合并至少一人审查
- 自动化测试：单元测试、集成测试、E2E 测试
- 静态分析：Lint、类型检查、安全扫描

### 发布策略

- 蓝绿部署 / 金丝雀发布 / 滚动更新
- Feature Flag 控制功能灰度
- 发布检查清单（Release Checklist）

## 延伸阅读

- [平台治理]({{ '/knowledge-base/themes/platform-governance.html' | relative_url }})
- [全栈工程师]({{ '/knowledge-base/domains/full-stack-engineer.html' | relative_url }})
