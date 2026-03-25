# uWisdom

uWisdom 是一个以"驾驭工程可读性原则"为核心的开源知识工程项目，用于搭建个人专属领域知识百科。

它面向三个目标：

- 让知识持续演进，而不是一次性沉淀
- 让人能读、能查、能维护
- 让 Agent 能读、能检索、能调用，服务真实商业场景

项目基于 GitHub 维护，基于 GitHub Pages 发布。

## 项目定位

uWisdom 不是单纯的笔记库，也不是静态知识堆积区，而是一套可工程化维护的个人知识系统：

- 在内容层，沉淀领域知识、方法论、案例、术语、规则与决策依据
- 在结构层，使用统一模板、元数据、链接关系和版本策略保证可读性
- 在能力层，为搜索、检索增强生成、Agent 调用和业务落地提供稳定知识底座

## 关键原则

- 工程可读性优先：目录、命名、元数据、文档模板必须一致
- 知识持续演进：每条知识要可增量更新、可追溯、可淘汰
- 人机双读：既适合人阅读，也适合 Agent 解析与调用
- 商业落地可控：知识来源、适用范围、时效性和风险边界清晰

## 站点栏目

- **知识百科**：按领域、主题、标签浏览知识条目
- **主题研究**：系统性深度研究某一领域或话题
- **人物志**：聚焦关键人物、思想家、作者与其代表思想
- **工具 & Agent**：管理搜索、索引、Agent 接入与知识图谱能力

## 目录结构

```
uWisdom/
├── docs/                        # Jekyll 站点源文件
│   ├── _config.yml              # Jekyll 配置
│   ├── _layouts/default.html    # 页面布局模板
│   ├── assets/                  # CSS、JS、数据文件
│   │   ├── style.css            # 样式
│   │   ├── app.js               # 搜索、图谱渲染、交互逻辑
│   │   ├── search-index.json    # 搜索索引（构建生成）
│   │   └── graph.json           # 知识图谱数据（构建生成）
│   ├── knowledge-base/
│   │   ├── domains/             # 知识领域条目
│   │   └── themes/              # 知识主题条目
│   ├── figures/                 # 人物志
│   ├── topic-research/          # 主题研究
│   ├── encyclopedia/            # 知识百科总览
│   ├── search/                  # 搜索页
│   └── today/                   # 每日精选（构建生成）
├── tools/
│   ├── build_site_data.py       # 生成搜索索引、图谱、每日精选
│   ├── validate_content.py      # 内容校验（CI 使用）
│   ├── build_semantic_index.py  # OpenAI + FAISS 语义索引
│   └── semantic_query.py        # 语义查询工具
├── .github/workflows/pages.yml  # CI/CD 自动部署
└── README.md
```

## 本地开发

### 前置要求

- Python 3.11+
- Ruby + Bundler（用于 Jekyll，可选）
- Git

### 快速开始

```bash
# 克隆仓库
git clone https://github.com/zhubao315/uWisdom.git
cd uWisdom

# 安装 Python 依赖（用于构建搜索索引）
pip install pyyaml

# 生成站点数据
python3 tools/build_site_data.py

# 校验内容完整性
python3 tools/validate_content.py

# 本地预览（需要 Jekyll）
cd docs
bundle install    # 首次运行
bundle exec jekyll serve --baseurl /uWisdom
# 访问 http://localhost:4000/uWisdom/
```

### 添加新知识条目

在对应目录创建 `.md` 文件，遵循 front matter 模板：

```markdown
---
title: 条目标题
summary: 一句话摘要，描述这个条目是什么
permalink: /knowledge-base/domains/your-entry.html
tags:
  - ai
  - architecture
version: v1.0.0
author: 作者名
book: 相关书籍
---

# 条目标题

## 领域定义
...

## 核心要点
...

## 延伸阅读
- [相关条目]({{ '/knowledge-base/domains/other.html' | relative_url }})
```

### 语义搜索（本地工具）

```bash
pip install openai faiss-cpu numpy

# 构建语义索引
OPENAI_API_KEY=your_key python3 tools/build_semantic_index.py

# 查询
OPENAI_API_KEY=your_key python3 tools/semantic_query.py "你想问的问题"
```

## GitHub Pages

- Repository: `https://github.com/zhubao315/uWisdom`
- Pages: `https://zhubao315.github.io/uWisdom`

## 技术栈

- **静态站点**：Jekyll + GitHub Pages
- **前端**：原生 HTML/CSS/JS，Mermaid.js（知识图谱）
- **搜索**：前端结构化过滤 + JSON 索引
- **语义检索**：OpenAI embeddings + FAISS（离线工具）
- **CI/CD**：GitHub Actions（自动构建、校验、部署）
- **构建工具**：Python（搜索索引、内容校验）

## License

MIT
