---
title: Agent 工作流设计
summary: 设计单 Agent 与多 Agent 协作的工作流编排系统
permalink: /knowledge-base/themes/agent-workflow-design.html
type: principle
identity: architect
field: ai
tags: [ai, agent, workflow, orchestration, multi-agent]
version: v1.0.0
confidence: high
applicability:
  - 设计需要多步推理的复杂任务系统时
  - 构建多 Agent 协作的工作流时
  - 设计 Agent 与外部系统集成架构时
non_applicability:
  - 单次简单问答不需要工作流
  - 确定性任务（传统规则引擎更合适）
---

# Agent 工作流设计

所属领域：[人工智能专家]({{ '/knowledge-base/domains/ai-expert.html' | relative_url }})

## 定义

设计 AI Agent 的任务拆解、工具调用、记忆管理、多步推理和多 Agent 协作的工作流编排系统。核心目标是将 LLM 的推理能力封装为可靠、可复用、可观测的自动化流程。

**与普通 LLM 调用的区别**：

| 维度 | LLM 调用 | Agent 工作流 |
|------|----------|--------------|
| **状态管理** | 无状态 | 维护任务状态、记忆、进度 |
| **多步推理** | 单次请求 | 循环迭代、反思、重试 |
| **工具调用** | 手动 | 自动发现、调用、评估结果 |
| **错误处理** | 简单重试 | 策略化降级、转移 |
| **可观测性** | 有限 | 全链路追踪 |

## 核心要点

### 1. 单 Agent 架构

#### 1.1 Agent 核心组件

```
┌─────────────────────────────────────────────────────┐
│                      Agent                          │
├─────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │
│  │   感知层    │  │   规划层    │  │   执行层    │ │
│  │  Perception │  │  Planning   │  │  Execution │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬─────┘ │
│         │                │                │        │
│         └────────────────┼────────────────┘        │
│                          ▼                          │
│                  ┌────────────────┐                 │
│                  │     记忆层     │                 │
│                  │    Memory      │                 │
│                  └────────────────┘                 │
└─────────────────────────────────────────────────────┘
```

**感知层**：解析用户输入、工具返回、上下文信息
**规划层**：任务分解、步骤选择、自我反思
**执行层**：工具调用、结果验证、状态更新
**记忆层**：短期对话、中期上下文、长期知识

#### 1.2 角色定义与系统提示

```python
# Agent 角色定义示例
AGENT_PROMPTS = {
    "research_agent": {
        "role": "深度研究专家",
        "capabilities": [
            "网络搜索与信息提取",
            "多源信息整合与交叉验证",
            "结构化报告生成"
        ],
        "constraints": [
            "不臆造未经验证的信息",
            "标注信息来源和置信度",
            "超过 3 个信息源时进行综合分析"
        ],
        "output_format": {
            "summary": "核心发现（3 句话）",
            "details": "详细分析（分点论述）",
            "sources": ["来源列表"],
            "confidence": "high/medium/low",
            "gaps": "信息缺口说明"
        }
    },
    "code_agent": {
        "role": "代码工程专家",
        "capabilities": [
            "代码生成与重构",
            "Bug 定位与修复",
            "代码审查与优化建议"
        ],
        "constraints": [
            "优先使用已有代码而非重复造轮子",
            "生成代码必须包含测试",
            "重大改动需要人工确认"
        ],
        "workflow": [
            "理解需求",
            "搜索现有代码",
            "设计解决方案",
            "实现与测试",
            "提交代码审查"
        ]
    }
}
```

#### 1.3 记忆系统设计

**记忆分层架构**：

```
┌─────────────────────────────────────────────┐
│              长期记忆 (Long-term)            │
│  ┌───────────────────────────────────────┐  │
│  │ 语义记忆：向量化存储的知识片段           │  │
│  │ 程序记忆：Agent 的技能和工作流模板       │  │
│  │ 情景记忆：历史成功/失败案例              │  │
│  └───────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
                      ▲
                      │ 检索
                      │
┌─────────────────────────────────────────────┐
│              中期记忆 (Episodic)             │
│  ┌───────────────────────────────────────┐  │
│  │ 当前任务相关上下文                      │  │
│  │ 最近 N 轮对话摘要                       │  │
│  │ 任务进度和中间结果                      │  │
│  └───────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
                      ▲
                      │ 更新
                      │
┌─────────────────────────────────────────────┐
│              短期记忆 (Working)              │
│  ┌───────────────────────────────────────┐  │
│  │ 当前对话上下文（完整）                  │  │
│  │ 当前步骤的中间结果                      │  │
│  │ 待处理的任务队列                        │  │
│  └───────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

**记忆检索策略**：
```python
class MemoryRetrieval:
    def __init__(self, vector_store):
        self.vector_store = vector_store
    
    def retrieve(self, query: str, task_context: dict) -> list:
        # 1. 语义检索
        semantic_results = self.vector_store.search(
            query, 
            top_k=5,
            filter={"type": "knowledge"}
        )
        
        # 2. 任务上下文过滤
        filtered = [
            r for r in semantic_results
            if self.relevant_to_task(r, task_context)
        ]
        
        # 3. 时间衰减
        recency_weighted = self.apply_recency_decay(filtered)
        
        # 4. 相关性重排
        reranked = self.rerank(recency_weighted, query)
        
        return reranked
    
    def save_episode(self, task: str, result: dict, lessons: str):
        """保存经验片段"""
        self.vector_store.add({
            "type": "episode",
            "task": task,
            "result": result,
            "lessons": lessons,
            "timestamp": datetime.now()
        })
```

### 2. 推理与规划模式

#### 2.1 ReAct 模式（Reasoning + Acting）

```python
class ReActAgent:
    def __init__(self, llm, tools, max_iterations=10):
        self.llm = llm
        self.tools = {t.name: t for t in tools}
        self.max_iterations = max_iterations
    
    async def run(self, task: str) -> str:
        history = []
        observation = "任务开始。"
        
        for i in range(self.max_iterations):
            # 1. 推理
            reasoning = await self.llm.chat([
                *history,
                {"role": "user", "content": f"任务: {task}"},
                {"role": "assistant", "content": observation}
            ])
            
            # 2. 判断下一步行动
            decision = self.parse_reasoning(reasoning)
            
            if decision.action == "finish":
                return decision.response
            
            # 3. 执行行动
            tool = self.tools.get(decision.tool_name)
            if tool:
                result = await tool.execute(decision.tool_input)
                observation = f"观察结果: {result}"
            else:
                observation = f"错误: 工具 {decision.tool_name} 不存在"
            
            history.append({"role": "assistant", "content": reasoning})
        
        return "任务超时，未能在规定次数内完成"
```

**ReAct 输出格式**：
```
Thought: 我需要先搜索相关资料了解这个话题...
Action: search
Action Input: {"query": "最新的人工智能发展趋势 2026"}
Observation: 搜索返回了 10 条结果，包含...
```

#### 2.2 Plan-and-Execute 模式

```python
class PlanAndExecuteAgent:
    def __init__(self, llm, executor):
        self.llm = llm
        self.executor = executor
    
    async def plan(self, task: str) -> list[Step]:
        """将复杂任务分解为可执行步骤"""
        plan_prompt = f"""
        任务: {task}
        
        请将这个任务分解为具体的执行步骤。每个步骤应该：
        1. 有明确的输入和输出
        2. 可以独立验证结果
        3. 尽量控制在 5 分钟内完成
        
        输出格式：
        1. [步骤名称]: [具体描述]
        2. [步骤名称]: [具体描述]
        ...
        """
        
        response = await self.llm.chat([{"role": "user", "content": plan_prompt}])
        return self.parse_steps(response)
    
    async def execute(self, task: str) -> str:
        # 1. 规划阶段
        steps = await self.plan(task)
        
        # 2. 顺序执行阶段
        results = []
        for step in steps:
            result = await self.executor.run(step)
            results.append(result)
            
            # 3. 验证阶段
            if not self.validate_step(step, result):
                # 回退并重新规划
                steps = await self.replan(task, results)
        
        return self.synthesize(results)
```

#### 2.3 Reflexion 模式（自我反思）

```python
class ReflexionAgent:
    async def run_with_reflection(self, task: str) -> str:
        # 1. 初始尝试
        result = await self.execute(task)
        
        # 2. 自我评估
        evaluation = await self.self_evaluate(task, result)
        
        if evaluation.passed:
            return result
        
        # 3. 分析失败原因
        failure_analysis = await self.analyze_failure(task, result, evaluation)
        
        # 4. 生成改进策略
        improvement = await self.generate_improvement(failure_analysis)
        
        # 5. 重试或降级
        if evaluation.can_retry:
            # 应用改进策略重试
            return await self.execute_with_strategy(task, improvement)
        else:
            # 降级处理或返回部分结果
            return self.degrade_gracefully(result, evaluation)
    
    async def self_evaluate(self, task: str, result: str) -> Evaluation:
        """LLM 自我评估"""
        eval_prompt = f"""
        任务: {task}
        结果: {result}
        
        请从以下维度评估结果质量：
        1. 任务完成度（0-100）
        2. 准确性（是否包含错误信息）
        3. 完整性（是否涵盖所有要求）
        4. 可用性（结果是否可直接使用）
        
        返回：
        - passed: boolean
        - can_retry: boolean
        - issues: [发现的问题列表]
        """
        # ... 实现
```

### 3. 多 Agent 协作

#### 3.1 协作模式分类

| 模式 | 描述 | 适用场景 | 示例 |
|------|------|----------|------|
| **导演模式** | 一个 Agent 协调多个专家 Agent | 复杂任务分解 | 论文写作：规划→写作→审查 |
| **辩论模式** | 多 Agent 对抗性讨论 | 方案评审、风险识别 | 产品设计评审 |
| **流水线模式** | Agent 串行处理数据流 | 数据处理、内容生成 | 代码：解析→实现→测试 |
| **并行模式** | 多个 Agent 同时处理子任务 | 调研、测试并行化 | 市场调研：多个数据源并行 |
| **层级模式** | Agent 嵌套子 Agent | 复杂任务的递归分解 | 系统设计：架构→模块→组件 |

#### 3.2 通信协议设计

```python
# Agent 间消息格式
class AgentMessage:
    def __init__(
        self,
        sender: str,           # 发送者 Agent ID
        receiver: str,         # 接收者 Agent ID (或 "broadcast")
        content: dict,         # 消息内容
        message_type: str,     # request/response/notification
        conversation_id: str,  # 关联的对话 ID
        metadata: dict = None  # 元数据
    ):
        self.sender = sender
        self.receiver = receiver
        self.content = content
        self.message_type = message_type
        self.conversation_id = conversation_id
        self.metadata = metadata or {}
        self.timestamp = datetime.now()
    
    def to_json(self) -> str:
        return json.dumps({
            "sender": self.sender,
            "receiver": self.receiver,
            "content": self.content,
            "type": self.message_type,
            "conversation_id": self.conversation_id,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        })


# 消息类型定义
MESSAGE_TYPES = {
    "TASK_REQUEST": {
        "description": "发送任务请求",
        "required_fields": ["task", "expected_output"],
        "optional_fields": ["priority", "deadline", "constraints"]
    },
    "TASK_RESPONSE": {
        "description": "返回任务结果",
        "required_fields": ["result", "status"],
        "optional_fields": ["evidence", "confidence", "lessons"]
    },
    "STATUS_UPDATE": {
        "description": "状态更新通知",
        "required_fields": ["status", "progress"],
        "optional_fields": ["blockers", "next_steps"]
    },
    "CONSULTATION": {
        "description": "咨询其他 Agent 意见",
        "required_fields": ["question", "context"],
        "optional_fields": ["expertise_required"]
    }
}
```

#### 3.3 多 Agent 系统架构

```python
class MultiAgentSystem:
    def __init__(self):
        self.agents = {}  # agent_id -> Agent
        self.message_queue = asyncio.Queue()
        self.shared_memory = SharedMemory()
        self.execution_engine = ExecutionEngine()
    
    def register_agent(self, agent_id: str, agent: Agent, role: str):
        self.agents[agent_id] = {
            "agent": agent,
            "role": role,
            "status": "idle"
        }
    
    async def start_collaboration(self, workflow: Workflow):
        """启动多 Agent 协作"""
        # 1. 初始化工作流
        self.execution_engine.initialize(workflow)
        
        # 2. 启动消息循环
        message_handler = asyncio.create_task(self.handle_messages())
        
        # 3. 触发初始任务
        await self.send_message(Message(
            sender="system",
            receiver=workflow.initial_agent,
            content={"task": workflow.initial_task}
        ))
        
        # 4. 等待工作流完成
        await workflow.completion_event.wait()
        
        # 5. 清理
        message_handler.cancel()
    
    async def handle_messages(self):
        """消息处理循环"""
        while True:
            message = await self.message_queue.get()
            
            # 路由到对应 Agent
            if message.receiver == "broadcast":
                for agent_id in self.agents:
                    await self.dispatch_to_agent(agent_id, message)
            else:
                await self.dispatch_to_agent(message.receiver, message)
    
    async def dispatch_to_agent(self, agent_id: str, message: Message):
        """分发消息到 Agent"""
        if agent_id not in self.agents:
            return
        
        agent_info = self.agents[agent_id]
        agent_info["status"] = "busy"
        
        try:
            response = await agent_info["agent"].process(message)
            
            # 根据响应类型处理
            if response.type == "task_complete":
                await self.on_task_complete(agent_id, response)
            elif response.type == "needs_collaboration":
                await self.forward_to_collaborators(agent_id, response)
            elif response.type == "blocked":
                await self.handle_blockage(agent_id, response)
                
        finally:
            agent_info["status"] = "idle"
```

### 4. 工程实践

#### 4.1 状态管理

```python
# 持久化 Agent 状态
@dataclass
class AgentState:
    session_id: str
    task_id: str
    current_step: int
    memory: list[dict]
    tool_call_history: list[dict]
    checkpoints: dict[int, dict]  # checkpoint_id -> state snapshot
    
    def checkpoint(self) -> int:
        """创建检查点，返回 checkpoint_id"""
        checkpoint_id = len(self.checkpoints)
        self.checkpoints[checkpoint_id] = {
            "step": self.current_step,
            "memory": copy.deepcopy(self.memory),
            "timestamp": datetime.now()
        }
        return checkpoint_id
    
    def restore(self, checkpoint_id: int):
        """恢复到指定检查点"""
        if checkpoint_id not in self.checkpoints:
            raise ValueError(f"Checkpoint {checkpoint_id} not found")
        
        state = self.checkpoints[checkpoint_id]
        self.current_step = state["step"]
        self.memory = copy.deepcopy(state["memory"])


# 状态持久化存储
class StateStore:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
        self.ttl = 7 * 24 * 3600  # 7 天过期
    
    async def save(self, state: AgentState):
        key = f"agent_state:{state.session_id}:{state.task_id}"
        await self.redis.set(key, pickle.dumps(state), ex=self.ttl)
    
    async def load(self, session_id: str, task_id: str) -> Optional[AgentState]:
        key = f"agent_state:{session_id}:{task_id}"
        data = await self.redis.get(key)
        if data:
            return pickle.loads(data)
        return None
```

#### 4.2 超时与重试策略

```python
class TimeoutConfig:
    def __init__(
        self,
        per_step_timeout: int = 60,      # 每步超时（秒）
        total_timeout: int = 600,         # 总任务超时
        max_retries: int = 3,             # 最大重试次数
        retry_delay: float = 2.0           # 重试延迟（秒）
    ):
        self.per_step_timeout = per_step_timeout
        self.total_timeout = total_timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay


async def execute_with_timeout(
    agent: Agent,
    task: str,
    config: TimeoutConfig
) -> ExecutionResult:
    start_time = time.time()
    
    for attempt in range(config.max_retries + 1):
        try:
            # 设置单步超时
            result = await asyncio.wait_for(
                agent.run(task),
                timeout=config.per_step_timeout
            )
            return ExecutionResult(success=True, result=result)
            
        except asyncio.TimeoutError:
            elapsed = time.time() - start_time
            
            if elapsed > config.total_timeout:
                return ExecutionResult(
                    success=False,
                    error="total_timeout_exceeded",
                    partial_result=get_partial_result(agent)
                )
            
            if attempt < config.max_retries:
                await asyncio.sleep(config.retry_delay * (attempt + 1))
                task = f"{task}\n\n注意：上次执行超时，请精简你的输出。"
            else:
                return ExecutionResult(
                    success=False,
                    error="max_retries_exceeded",
                    partial_result=get_partial_result(agent)
                )
    
    return ExecutionResult(success=False, error="unknown")
```

#### 4.3 人机协作设计

```python
class HumanInTheLoop:
    """人机协作策略"""
    
    APPROVAL_TRIGGERS = [
        "code_deployment",      # 代码部署
        "data_deletion",        # 数据删除
        "external_api_call",    # 外部 API 调用
        "content_publication",  # 内容发布
        "config_change",        # 配置修改
        "high_cost_operation",  # 高成本操作
    ]
    
    def __init__(self, approval_queue: Queue, notification_service):
        self.approval_queue = approval_queue
        self.notification = notification_service
    
    async def request_approval(self, action: Action, context: dict) -> bool:
        """请求人工审批"""
        approval_request = {
            "action": action,
            "context": context,
            "risk_level": self.assess_risk(action, context),
            "alternatives": self.suggest_alternatives(action)
        }
        
        # 1. 发送通知
        await self.notification.send(
            f"需要审批: {action.type}",
            approval_request
        )
        
        # 2. 加入审批队列
        await self.approval_queue.put(approval_request)
        
        # 3. 等待审批结果（带超时）
        try:
            result = await asyncio.wait_for(
                self.get_approval_result(approval_request["id"]),
                timeout=24 * 3600  # 24 小时超时
            )
            return result.approved
        except asyncio.TimeoutError:
            return False  # 超时默认拒绝
    
    def assess_risk(self, action: Action, context: dict) -> str:
        """风险评估"""
        if action.type in ["data_deletion", "deployment"]:
            return "high"
        if context.get("estimated_cost", 0) > 1000:
            return "medium"
        return "low"
```

## 常见陷阱与应对

### 陷阱 1：Agent 陷入循环

**症状**：Agent 不断重复相似的思考和行动。

**应对**：
- 实现最大迭代次数限制
- 添加"已尝试方法"记忆，避免重复
- 使用 ReAct 模式时，强制要求每次思考有新的观察

### 陷阱 2：工具调用失败导致级联失败

**症状**：一个工具失败后整个工作流崩溃。

**应对**：
- 实现工具调用的隔离和降级策略
- 添加重试逻辑和优雅降级
- 记录工具失败模式，逐步优化

### 陷阱 3：记忆膨胀导致上下文爆炸

**症状**：Agent 越来越慢，输出越来越长。

**应对**：
- 实施记忆压缩和摘要策略
- 设置记忆容量上限
- 定期清理低价值记忆

## 最佳实践清单

- [ ] 定义清晰的 Agent 角色和能力边界
- [ ] 实施分层记忆系统，避免上下文膨胀
- [ ] 添加全链路追踪，便于问题诊断
- [ ] 实现优雅降级，不因单点失败导致整体失败
- [ ] 人机协作：关键决策点需要人工确认
- [ ] 状态持久化：支持断点续跑
- [ ] 工具调用日志：记录所有外部交互
- [ ] 定期评估：黄金集测试 Agent 输出质量

## 延伸阅读

- [LLM 应用架构]({{ '/knowledge-base/themes/llm-application-architecture.html' | relative_url }})
- [工程交付闭环]({{ '/knowledge-base/themes/engineering-delivery.html' | relative_url }})
- [云计算与云原生]({{ '/knowledge-base/domains/cloud-native.html' | relative_url }})
