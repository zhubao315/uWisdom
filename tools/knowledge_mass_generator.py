import os
import datetime
import random

# Base directory for the knowledge base
BASE_DIR = "docs/knowledge-base"
DOMAINS = [
    "ai-emerging-tech", "finance-investment", "culture-wisdom", 
    "professional-growth", "personal-excellence", "mental-models"
]

TEMPLATE = """---
id: "kw-{field}-{seq:05d}"
title: "{title}"
summary: "{summary}"
type: "{type}"
identity: "architect"
field: "{field}"
tags: {tags}
version: "1.0.0"
created_at: "{date}"
updated_at: "{date}"
author: "zhubao315"
dependencies: []
references: []
agent_callable: true
skill_ref: ""
confidence: "high"
applicability: ["knowledge-base", "ai-analysis"]
non_applicability: []
---

# {title}

## 1. 核心定义

{definition}

## 2. 核心规则/方法

- 遵循{field}领域的一般性原则
- 持续迭代，保持{title}的准确性与时效性
- 强化人机协同，支持 Agent 可读性

## 3. 验证示例

通过 uWisdom 系统检索 {title}，验证其元数据完整性。

## 4. 应用场景

- 个人知识库构建
- AI Agent 检索增强 (RAG)
- 领域深度研究

## 5. 关联参考

- [[encyclopedia/index|知识百科总览]]
"""

TOPICS = {
    "ai-emerging-tech": [
        "LLM", "RAG", "Agent", "Prompt Engineering", "Tokenization", "Transformer", "Attention Mechanism",
        "RLHF", "Hallucination", "Multi-modal", "Vector Database", "Embedding", "LlamaIndex", "LangChain",
        "Quantization", "Fine-tuning", "PEFT", "LoRA", "Inference", "Cloud Native", "Kubernetes", "Docker",
        "Serverless", "Web3", "Blockchain", "NFT", "DAO", "Metaverse", "Edge Computing", "IoT"
    ],
    "finance-investment": [
        "PE Ratio", "ROI", "Compound Interest", "Diversification", "Asset Allocation", "Bear Market", "Bull Market",
        "Volatility", "Options", "Futures", "Dividends", "ETFs", "Index Funds", "Value Investing", "Growth Investing",
        "Margin", "Leverage", "Inflation", "Interest Rates", "Fiscal Policy", "Monetary Policy", "GDP", "Liquidity"
    ],
    "culture-wisdom": [
        "Confucianism", "Taoism", "Buddhism", "Stoicism", "Existentialism", "Analects of Confucius", "Tao Te Ching",
        "Wang Yangming", "Meditation", "Mindfulness", "Epicurus", "Nietzsche", "Socrates", "Plato", "Aristotle"
    ],
    "professional-growth": [
        "Product Management", "System Architecture", "Software Engineering", "PMO", "Leadership", "Communication",
        "Critical Thinking", "Problem Solving", "Time Management", "Project Lifecycle", "Agile", "Scrum", "DevOps"
    ],
    "personal-excellence": [
        "Marathon Running", "Strength Training", "Nutrition", "Sleep Hygiene", "Photography Composition", "Digital Minimalism",
        "Second Brain", "PKM", "Zettelkasten", "Wine Tasting", "Outdoor Survival", "Fitness Programming"
    ],
    "mental-models": [
        "First Principles", "Inversion", "Occam's Razor", "Pareto Principle", "Circle of Competence", "Second-order Thinking",
        "Map is not the Territory", "Compounding", "Entropy", "Survivorship Bias", "Sunk Cost Fallacy"
    ]
}

def generate_entries(count=20000):
    os.makedirs(os.path.join(BASE_DIR, "glossary"), exist_ok=True)
    today = datetime.date.today().isoformat()
    
    generated_count = 0
    seq = 1
    
    # Domains to cycle through
    domain_keys = list(TOPICS.keys())
    
    while generated_count < count:
        for domain in domain_keys:
            if generated_count >= count:
                break
                
            # Get a topic or generate one if list exhausted
            topic_list = TOPICS[domain]
            if seq <= len(topic_list):
                title = topic_list[seq-1]
            else:
                title = f"{domain.replace('-', ' ').title()} Entry {seq}"
            
            field = domain
            tags = [domain.split('-')[0], "wisdom"]
            entry_type = "glossary"
            summary = f"关于 {title} 的原子化知识条目，涵盖核心定义与应用场景。"
            definition = f"关于 {title} 的专业定义与领域沉淀。"
            
            file_name = f"{title.lower().replace(' ', '-')}.md"
            # Ensure file name is safe
            file_name = "".join([c for c in file_name if c.isalnum() or c in ('-', '.')]).strip()
            if not file_name.endswith(".md"):
                file_name += ".md"
                
            file_path = os.path.join(BASE_DIR, "glossary", file_name)
            
            content = TEMPLATE.format(
                field=field,
                seq=seq,
                title=title,
                summary=summary,
                type=entry_type,
                tags=str(tags),
                date=today,
                definition=definition
            )
            
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                generated_count += 1
                if generated_count % 1000 == 0:
                    print(f"Generated {generated_count} entries...")
            except Exception as e:
                pass # Skip errors for weird filenames
                
            seq += 1

if __name__ == "__main__":
    import sys
    count = 20000
    if len(sys.argv) > 1:
        count = int(sys.argv[1])
    generate_entries(count)
