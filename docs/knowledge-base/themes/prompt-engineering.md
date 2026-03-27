---
title: 提示词工程
summary: 设计、优化和管理 LLM 提示的系统性方法论与最佳实践
permalink: /knowledge-base/themes/prompt-engineering.html
type: principle
identity: architect
field: ai
tags: [ai, llm, prompt, engineering, zero-shot, few-shot]
version: v1.0.0
confidence: high
applicability:
  - 设计新的 LLM 应用时
  - 优化现有提示效果时
  - 构建提示管理系统时
non_applicability:
  - 不涉及 LLM 调用的场景
  - 简单的固定模板场景
---

# 提示词工程

所属领域：[人工智能专家]({{ '/knowledge-base/domains/ai-expert.html' | relative_url }})
相关主题：[LLM 应用架构]({{ '/knowledge-base/themes/llm-application-architecture.html' | relative_url }}) | [上下文工程]({{ '/knowledge-base/themes/context-engineering.html' | relative_url }})

## 定义

提示词工程（Prompt Engineering）是设计、优化和管理 LLM 提示的系统性方法论，旨在最大化模型输出的质量、可靠性和一致性。

**核心命题**：提示词是人与 LLM 之间的「接口协议」，好的提示词是精确的需求规格说明书。

**与上下文工程的区别**：
- **提示词工程**：关注「如何提问」，即 Prompt 的结构和表达方式
- **上下文工程**：关注「传递什么信息」，即上下文的组织和管理

## 核心要点

### 1. 提示词基础理论

#### 1.1 LLM 的本质

LLM 是「下一个词预测器」，但这个看似简单的机制涌现出了惊人的能力：

**涌现能力（Emergent Capabilities）**：
- 思维链（Chain-of-Thought）：复杂推理能力
- 上下文学习（In-Context Learning）：从示例中学习
- 指令遵循（Instruction Following）：理解并执行指令
- 思维框架（Framework Generation）：生成结构化内容

**能力边界**：
```
能力上限：受模型规模、训练数据、指令微调的制约
稳定性：相同提示词可能产生不同输出
幻觉：可能生成看似合理但实际错误的内容
上下文窗口：受限于 Token 数量
```

#### 1.2 提示词设计原则

**ICOOP 原则**：

| 原则 | 说明 | 示例 |
|------|------|------|
| **Intent（意图）** | 明确告知模型你希望它做什么 | "分析以下文本的情感倾向" |
| **Context（上下文）** | 提供足够的背景信息 | "这是一篇电商产品的用户评论" |
| **Output Format（输出格式）** | 明确期望的输出形式 | "以 JSON 格式返回，包含 sentiment 和 confidence 字段" |
| **Options（选项）** | 限定可选范围（如适用） | "情感分类为 positive/negative/neutral 之一" |
| **Prevention（预防）** | 预防常见错误 | "不要编造信息，只基于提供的文本分析" |

#### 1.3 提示词结构范式

```python
# 完整提示词结构
PROMPT_TEMPLATE = """
# 角色定义
你是一个 [角色]，具有以下特征：
- [专业背景]
- [核心能力]
- [行为准则]

# 任务背景
[提供任务的背景信息、约束条件、相关上下文]

# 具体任务
请完成以下任务：
[task_description]

# 输出要求
1. [具体要求1]
2. [具体要求2]
3. [具体要求3]

# 约束条件
- [约束1]
- [约束2]

# 示例（Few-shot）
示例输入：[example_input]
示例输出：[example_output]

# 开始执行
"""

# 精简版提示词结构
SIMPLE_PROMPT = """
任务：{task}
背景：{context}
格式：{format}
约束：{constraints}
"""
```

### 2. 核心提示技术

#### 2.1 Zero-Shot Prompting

无需示例，直接给出指令。

**适用场景**：
- 简单、明确的任务
- 模型在该任务上表现良好
- 需要快速验证可行性

**最佳实践**：
```python
# ❌ 不好的 Zero-Shot 提示
"翻译这段话"

# ✅ 好的 Zero-Shot 提示
"""
请将以下中文文本翻译为英文。

要求：
1. 保持原文的专业语气
2. 技术术语使用标准翻译
3. 人名按拼音处理

原文：
{text}
"""
```

**Zero-Shot 进阶技巧**：

| 技巧 | 描述 | 效果 |
|------|------|------|
| **角色代入** | "你是一位资深软件架构师" | 提升专业性 |
| **链式思考** | "请一步步思考" | 提升推理质量 |
| **格式指定** | "以 JSON 格式输出" | 减少格式错误 |
| **否定指令** | "不要使用专业术语" | 避免特定输出 |

#### 2.2 Few-Shot Prompting

通过示例教会模型模式和格式。

**示例数量选择**：
```python
def select_shot_count(task_complexity: str) -> int:
    """根据任务复杂度选择示例数量"""
    shot_guide = {
        "简单任务": 1,      # 格式转换、简单分类
        "中等任务": 2-3,    # 需要模式学习
        "复杂任务": 3-5,   # 需要多种模式
        "高度复杂": 5-10,  # 需要全面的示例覆盖
    }
    return shot_guide.get(task_complexity, 2)
```

**示例设计原则**：

```python
# ❌ 不好的 Few-Shot 示例
# 示例之间没有一致性
示例1输入：苹果
示例1输出：水果

示例2输入：汽车
示例2输出：交通工具

# ✅ 好的 Few-Shot 示例
# 示例覆盖典型情况和边界情况
示例1输入：苹果 -> 输出：水果（甜味、脆口）
示例2输入：柠檬 -> 输出：水果（酸味、多汁）
示例3输入：土豆 -> 输出：蔬菜（淀粉类）

# 关键：示例之间要有可比性和规律性
```

**示例选择策略**：

| 策略 | 说明 | 适用场景 |
|------|------|----------|
| **代表性** | 覆盖任务的主要变体 | 通用 |
| **边界案例** | 包含特殊情况 | 精确分类 |
| **多样性** | 不同风格、格式的示例 | 格式灵活任务 |
| **对抗性** | 包含易错样本 | 鲁棒性要求高 |

#### 2.3 Chain-of-Thought（CoT）

引导模型展示推理过程。

**标准 CoT**：
```python
# 在提示词末尾添加
"请逐步思考，并在最后给出答案。"

# 或更明确的引导
"""
请按以下步骤分析：
1. 首先，理解问题的核心是什么
2. 其次，识别关键信息和条件
3. 然后，进行逻辑推理
4. 最后，给出结论
"""
```

**Self-Consistency（自洽性）**：
```python
# 生成多个推理路径，选择最一致的答案
def self_consistency_prompt(question: str, n_paths: int = 3) -> str:
    return f"""
问题：{question}

请从不同角度思考这个问题，生成 {n_paths} 种不同的推理路径，
然后比较这些推理，选择最合理的结论。

步骤：
1. 推理路径 A
2. 推理路径 B
3. 推理路径 C
4. 综合比较
5. 最终结论
"""
```

**Tree-of-Thought（思维树）**：
```python
# 用于需要探索多种方案的任务
def tree_of_thought_prompt(problem: str) -> str:
    return f"""
问题：{problem}

请用思维树的方式探索解决方案：

第一层分支（方案 A、B、C）：
- 方案 A：...
- 方案 B：...
- 方案 C：...

第二层展开（A1、A2...）：
- A1：...
- A2：...

第三层细化：
- A1a：...
- A1b：...

最终选择：综合评估后选择最优路径
"""
```

#### 2.4 Role-Based Prompting（角色提示）

```python
# 角色定义模板
ROLE_PROMPT = """
# 角色设定
你是一位 [角色名称]。

## 专业背景
[描述该角色的专业知识和经验]

## 核心能力
- [能力1]
- [能力2]
- [能力3]

## 行为准则
- 始终 [准则1]
- 避免 [准则2]
- 优先考虑 [准则3]

## 沟通风格
[描述该角色说话/写作的风格]

## 专业知识边界
- 擅长：[具体领域]
- 谨慎：[需进一步确认的领域]
- 超出范围：[明确表示不知道]
"""

# 具体示例
ARCHITECT_ROLE = """
你是一位拥有 20 年经验的企业级系统架构师。

## 专业背景
- 主导过多个大型分布式系统设计
- 精通微服务、云原生架构
- 熟悉金融、电商等行业的系统特点

## 核心能力
- 系统可扩展性设计
- 性能优化与容量规划
- 技术选型与风险评估

## 行为准则
- 始终权衡技术理想与业务现实
- 避免过度设计
- 优先考虑可维护性和可观测性

## 沟通风格
- 简洁明了，用数据说话
- 喜欢用架构图和流程图
- 善于将复杂问题拆解
"""
```

#### 2.5 结构化输出

**JSON Schema 约束**：
```python
STRUCTURED_PROMPT = """
请分析以下文本的情感，并严格按以下 JSON Schema 输出：

```json
{{
  "sentiment": "string, 值为 positive/negative/neutral 之一",
  "confidence": "number, 0-1 之间的小数",
  "keywords": ["string, 情感关键词列表，最多5个"],
  "reasoning": "string, 简要推理过程"
}}

原文：{text}

注意：
1. 必须严格遵循 JSON 格式
2. 不要输出除 JSON 外的任何内容
3. confidence 必须是数字，不能是字符串
"""
```

**Markdown 表格输出**：
```python
TABLE_PROMPT = """
请分析以下产品的竞品情况，以 Markdown 表格形式输出：

| 竞品名称 | 核心优势 | 核心劣势 | 我的差异化 |
|----------|----------|----------|------------|
|          |          |          |            |

产品：{product_description}
"""
```

**分步骤输出**：
```python
STEP_PROMPT = """
请按以下步骤分析问题，并在每步完成后明确标注"[步骤N完成]"：

第一步：问题定义
- 明确要解决的核心问题
- 识别关键约束条件

第二步：方案设计
- 提出 2-3 个可行方案
- 分析各方案优缺点

第三步：方案评估
- 从成本、时间、风险角度评估
- 推荐最优方案

第四步：实施建议
- 具体行动计划
- 潜在风险及应对

开始执行。
"""
```

### 3. 高级提示技术

#### 3.1 Prompt Chaining（提示链）

```python
class PromptChain:
    def __init__(self, llm):
        self.llm = llm
        self.steps = []
    
    def add_step(self, prompt: str, output_key: str):
        """添加链式步骤"""
        self.steps.append({
            "prompt": prompt,
            "output_key": output_key,
            "validator": None
        })
        return self
    
    def add_validation(self, validator: callable):
        """添加验证器"""
        self.steps[-1]["validator"] = validator
        return self
    
    async def execute(self, initial_input: dict) -> dict:
        context = initial_input.copy()
        
        for i, step in enumerate(self.steps):
            # 填充提示词模板
            prompt = self._render_prompt(step["prompt"], context)
            
            # 执行步骤
            result = await self.llm.chat(prompt)
            context[step["output_key"]] = result
            
            # 验证（如有）
            if step["validator"]:
                validated = step["validator"](result)
                if not validated.success:
                    context["_errors"] = validated.errors
                    break
        
        return context


# 使用示例
chain = (PromptChain(llm)
    .add_step(
        "分析以下用户反馈，提取核心问题：{feedback}",
        "core_issues"
    )
    .add_step(
        "基于提取的问题 {core_issues}，提出解决方案：",
        "solutions"
    )
    .add_validation(validate_solutions)
    .add_step(
        "评估以下方案 {solutions} 的可行性和优先级：",
        "prioritized_solutions"
    )
)

result = await chain.execute({"feedback": user_feedback})
```

#### 3.2 Generation Knowledge Prompting

```python
def generation_knowledge_prompt(question: str) -> str:
    """
    先让模型生成相关知识，再用这些知识回答问题
    适用于需要外部知识的问题
    """
    return f"""
请先回答以下问题，但在回答之前，请先列出你将用到的关键概念和原理。

问题：{question}

格式：
## 所需知识
1. [概念1]：[简要定义]
2. [概念2]：[简要定义]

## 回答
[基于上述知识的完整回答]
"""
```

#### 3.3 Least-to-Most Prompting

```python
def least_to_most_prompt(problem: str) -> str:
    """
    先分解问题，再逐个解决，最后综合
    适用于复杂多步问题
    """
    return f"""
让我们逐步解决这个问题。

第一步：问题分解
将以下问题分解为最简单的子问题：
{problem}

子问题列表：
1. ...
2. ...

第二步：解决子问题
依次解决每个子问题...

第三步：综合
将子问题的解决方案综合为最终答案...
"""
```

#### 3.4 Emotional Prompting

```python
def emotional_prompt(task: str, emotional_context: str = "") -> str:
    """
    添加情感提示，提升模型参与度
    """
    templates = [
        "这是一个非常重要的问题，请认真对待：{task}",
        "我正在准备一场重要的演讲，请帮我完善：{task}",
        "这个问题困扰我很久了，请给出一个全面的解答：{task}",
    ]
    
    emotional_wrapper = random.choice(templates)
    return emotional_wrapper.format(task=task)
```

### 4. 提示词管理

#### 4.1 提示词版本管理

```python
# 提示词版本管理
class PromptVersion:
    def __init__(self, prompt: str, metadata: dict):
        self.prompt = prompt
        self.version = metadata.get("version", "1.0.0")
        self.created_at = metadata.get("created_at", datetime.now())
        self.author = metadata.get("author")
        self.description = metadata.get("description")
        self.test_results = metadata.get("test_results", [])
    
    def increment_patch(self):
        """补丁版本：微小修改"""
        parts = self.version.split(".")
        parts[2] = str(int(parts[2]) + 1)
        return ".".join(parts)
    
    def increment_minor(self):
        """次版本：新增功能/优化"""
        parts = self.version.split(".")
        parts[1] = str(int(parts[1]) + 1)
        parts[2] = "0"
        return ".".join(parts)


class PromptRegistry:
    def __init__(self, storage_path: str):
        self.storage = PromptStorage(storage_path)
        self.current_versions = {}
    
    async def save(self, name: str, prompt: PromptVersion):
        await self.storage.save(name, prompt)
        self.current_versions[name] = prompt.version
    
    async def load(self, name: str, version: str = None) -> PromptVersion:
        if version:
            return await self.storage.load(name, version)
        latest = await self.storage.load_latest(name)
        return latest
    
    async def rollback(self, name: str, target_version: str):
        """回滚到指定版本"""
        prompt = await self.storage.load(name, target_version)
        prompt.version = self.increment_minor()
        await self.save(name, prompt)
```

#### 4.2 提示词测试框架

```python
class PromptTester:
    def __init__(self, llm):
        self.llm = llm
        self.results = []
    
    def add_test_case(
        self,
        name: str,
        input_data: dict,
        expected_output: dict,
        metadata: dict = None
    ):
        """添加测试用例"""
        self.results.append({
            "name": name,
            "input": input_data,
            "expected": expected_output,
            "metadata": metadata or {}
        })
    
    async def run_tests(self) -> TestReport:
        """运行所有测试用例"""
        report = TestReport()
        
        for test in self.results:
            result = await self.execute_test(test)
            report.add_result(test["name"], result)
        
        return report
    
    async def execute_test(self, test: dict) -> TestResult:
        """执行单个测试"""
        # 渲染提示词
        prompt = self.render_prompt(test["input"])
        
        # 执行
        output = await self.llm.chat(prompt)
        
        # 评估
        evaluation = self.evaluate(test["expected"], output)
        
        return TestResult(
            passed=evaluation["passed"],
            output=output,
            evaluation=evaluation,
            latency=latency
        )
    
    def evaluate(self, expected: dict, actual: dict) -> dict:
        """评估输出是否符合预期"""
        errors = []
        
        for key, expected_value in expected.items():
            actual_value = actual.get(key)
            
            if isinstance(expected_value, type):
                if not isinstance(actual_value, expected_value):
                    errors.append(f"{key} 类型错误：期望 {expected_value}，实际 {type(actual_value)}")
            elif expected_value is not None:
                if actual_value != expected_value:
                    errors.append(f"{key} 值不匹配：期望 {expected_value}，实际 {actual_value}")
        
        return {
            "passed": len(errors) == 0,
            "errors": errors
        }
```

#### 4.3 A/B 测试框架

```python
class PromptABTest:
    def __init__(self, llm, test_name: str):
        self.llm = llm
        self.test_name = test_name
        self.variants = {}
    
    def add_variant(self, variant_id: str, prompt: str, weight: float = 1.0):
        """添加测试变体"""
        self.variants[variant_id] = {
            "prompt": prompt,
            "weight": weight,
            "results": []
        }
    
    async def run(self, test_inputs: list, metrics: list) -> ABTestResult:
        """
        运行 A/B 测试
        metrics: 评估指标，如 ["accuracy", "latency", "cost"]
        """
        # 分配流量
        assignments = self.assign_traffic(test_inputs)
        
        results = {vid: [] for vid in self.variants}
        
        for input_data, variant_id in assignments:
            prompt = self.variants[variant_id]["prompt"]
            output = await self.llm.chat(self.render(prompt, input_data))
            
            evaluation = self.evaluate(output, metrics)
            results[variant_id].append(evaluation)
        
        # 统计分析
        return self.analyze_results(results)
    
    def assign_traffic(self, inputs: list) -> list:
        """基于权重分配流量"""
        variants = list(self.variants.keys())
        weights = [self.variants[v]["weight"] for v in variants]
        
        assignments = []
        for input_data in inputs:
            variant_id = random.choices(variants, weights=weights)[0]
            assignments.append((input_data, variant_id))
        
        return assignments
    
    def analyze_results(self, results: dict) -> ABTestResult:
        """统计分析结果"""
        analysis = {}
        
        for vid, vid_results in results.items():
            if not vid_results:
                continue
            
            metrics_stats = {}
            for metric in vid_results[0].keys():
                values = [r[metric] for r in vid_results if metric in r]
                metrics_stats[metric] = {
                    "mean": statistics.mean(values),
                    "std": statistics.stdev(values) if len(values) > 1 else 0,
                    "count": len(values)
                }
            
            analysis[vid] = metrics_stats
        
        # 计算显著性
        significance = self.calculate_significance(analysis)
        
        return ABTestResult(
            test_name=self.test_name,
            analysis=analysis,
            significance=significance,
            winner=self.select_winner(analysis, significance)
        )
```

### 5. 常见问题与解决方案

#### 5.1 输出格式不稳定

**问题**：相同提示词产生不同格式的输出。

**解决方案**：
```python
# 1. 强化格式指令
"请严格按以下格式输出，不要添加任何解释：..."

# 2. 使用 XML 标签隔离
"""
输出格式：
<result>
<sentiment>情感分类</sentiment>
<confidence>置信度</confidence>
</result>
"""

# 3. 使用 JSON Schema
# 并在后续解析时验证格式
```

#### 5.2 幻觉问题

**问题**：模型生成看似合理但实际错误的内容。

**解决方案**：
```python
# 1. 明确约束
"如果不确定，请明确说明'我不知道'或'信息不足'"

# 2. 要求引用来源
"请基于以下信息回答，并引用你使用的具体信息"

# 3. 分步验证
"首先确认信息是否充足，如不足请说明需要什么信息"

# 4. 添加置信度
"对于每个陈述，请给出置信度 high/medium/low"
```

#### 5.3 上下文长度限制

**问题**：复杂任务超出上下文窗口。

**解决方案**：
```python
# 1. 任务分解
"这个任务分为三个步骤，先完成第一步..."

# 2. 压缩历史
# 在长对话中定期总结前文

# 3. 外部存储
# 将中间结果存储，必要时检索

# 4. 选择性上下文
# 只传递与当前任务相关的信息
```

#### 5.4 指令遵循不稳定

**问题**：模型忽略部分指令。

**解决方案**：
```python
# 1. 指令优先级排序
# 将最重要的指令放在最前面

# 2. 指令重复
# 在结尾重复关键约束

# 3. 负面约束
# 明确说明不要做什么
"请务必避免：1)... 2)... 3)..."

# 4. 示例强化
# 通过 Few-shot 展示期望行为
```

## 最佳实践清单

### 设计阶段
- [ ] 明确任务目标和成功标准
- [ ] 识别模型的已知能力边界
- [ ] 选择合适的提示技术（Zero/Few/CoT）
- [ ] 设计清晰、一致的输出格式

### 开发阶段
- [ ] 从简单提示词开始，逐步迭代
- [ ] 添加充分的约束条件
- [ ] 包含边界情况的处理
- [ ] 添加错误处理和回退策略

### 测试阶段
- [ ] 创建代表性测试集
- [ ] 测试正常情况和边界情况
- [ ] 测量输出一致性
- [ ] 评估不同模型的表现

### 生产阶段
- [ ] 版本化管理提示词
- [ ] 建立监控和告警
- [ ] 持续收集用户反馈
- [ ] 定期优化提示词

## 延伸阅读

- [上下文工程]({{ '/knowledge-base/themes/context-engineering.html' | relative_url }})
- [LLM 应用架构]({{ '/knowledge-base/themes/llm-application-architecture.html' | relative_url }})
- [Agent 工作流设计]({{ '/knowledge-base/themes/agent-workflow-design.html' | relative_url }})
- [驾驭工程可读性原则]({{ '/knowledge-base/themes/readability-principles.html' | relative_url }})
