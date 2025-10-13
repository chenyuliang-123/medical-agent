# AI智能体开发指南

## 什么是AI智能体（Agent）

AI智能体是一个能够：
1. **自主感知**环境和数据
2. **自主决策**采取何种行动
3. **调用工具**完成复杂任务
4. **学习记忆**用户偏好和历史

的智能系统。

## 本项目的Agent架构

```
用户输入
    ↓
┌─────────────────────────────────┐
│  LLM (GPT-4)                    │
│  - 理解用户意图                  │
│  - 制定行动计划                  │
│  - 决定调用哪些工具              │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│  工具集 (Tools)                  │
│  - query_health_data            │
│  - analyze_health_trend         │
│  - create_reminder              │
│  - search_knowledge             │
│  - calculate_health_metrics     │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│  数据层                          │
│  - 数据库                        │
│  - 知识库                        │
│  - 用户档案                      │
└─────────────────────────────────┘
    ↓
返回结果给用户
```

## 核心组件详解

### 1. Agent核心 (`agent_core.py`)

这是Agent的"大脑"，负责：
- 接收用户输入
- 调用LLM进行推理
- 管理工具调用
- 维护对话上下文

关键代码：
```python
class ChronicDiseaseAgent:
    def __init__(self, db, user_id, session_id):
        self.llm = ChatOpenAI(model="gpt-4")
        self.tools = get_agent_tools(db, user_id)
        self.agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
```

### 2. 工具集 (`tools.py`)

工具是Agent的"手和脚"，每个工具都是一个可以被调用的函数。

#### 工具定义示例

```python
@tool
def query_health_data(data_type: str, days: int = 7) -> str:
    """
    查询用户的健康数据
    
    参数:
    - data_type: 数据类型（blood_glucose, blood_pressure, weight）
    - days: 查询最近多少天的数据
    
    返回: JSON格式的健康数据
    """
    # 实现查询逻辑
    return json.dumps(results)
```

**重要**：
- 函数的docstring非常重要，LLM会根据它决定何时调用这个工具
- 参数类型要明确
- 返回值建议使用JSON格式

#### 添加新工具

1. 在`tools.py`中定义新函数
2. 使用`@tool`装饰器
3. 写清楚docstring
4. 在`get_agent_tools()`中返回

示例 - 添加"生成健康报告"工具：

```python
@tool
def generate_health_report(user_id: int, period: str = "week") -> str:
    """
    生成用户的健康报告
    
    参数:
    - user_id: 用户ID
    - period: 报告周期（week-周报, month-月报）
    
    返回: 健康报告内容
    """
    # 查询数据
    glucose_data = query_glucose(user_id, period)
    pressure_data = query_pressure(user_id, period)
    
    # 生成报告
    report = {
        "period": period,
        "glucose_summary": analyze_glucose(glucose_data),
        "pressure_summary": analyze_pressure(pressure_data),
        "recommendations": generate_recommendations()
    }
    
    return json.dumps(report, ensure_ascii=False)
```

### 3. Prompt工程 (`prompts.py`)

Prompt是Agent的"指令手册"，定义了Agent的：
- 角色定位
- 能力范围
- 工作原则
- 交互风格

#### Prompt优化技巧

**1. 明确角色**
```python
你是一个专业的慢病管理AI智能体，专注于帮助糖尿病和高血压患者...
```

**2. 列出能力**
```python
## 你的核心能力
1. 健康数据分析
2. 个性化建议
3. 主动预警
...
```

**3. 定义原则**
```python
## 工作原则
1. 安全第一：遇到紧急情况立即建议就医
2. 数据驱动：优先使用工具查询数据
...
```

**4. 提供示例**
```python
## 示例对话
用户：我今天测的血糖是8.5
助手：[调用工具查询历史数据]
...
```

### 4. 记忆系统 (`memory.py`)

记忆系统让Agent能够：
- 记住对话上下文
- 了解用户背景信息
- 追踪历史交互

#### 两种记忆

**短期记忆**：当前会话的对话历史
```python
self.short_term_memory = []  # 存储当前对话
```

**长期记忆**：用户档案、历史数据
```python
def get_user_context(self):
    # 从数据库加载用户信息
    return user_profile
```

## Agent工作流程

### 完整的对话流程

```
1. 用户输入："我今天测的血糖是8.5，正常吗？"
   ↓
2. Agent接收输入，加载上下文
   - 用户信息：张三，55岁，糖尿病患者
   - 对话历史：最近讨论过饮食
   ↓
3. LLM分析意图
   - 意图：咨询血糖值是否正常
   - 需要：查询历史数据、对比正常范围
   ↓
4. 制定计划
   - 步骤1：调用query_health_data查询历史血糖
   - 步骤2：调用search_knowledge查询正常范围
   - 步骤3：分析并给出建议
   ↓
5. 执行工具调用
   Tool 1: query_health_data("blood_glucose", days=7)
   返回：最近7天平均7.2 mmol/L
   
   Tool 2: search_knowledge("血糖正常范围")
   返回：空腹3.9-6.1，餐后<7.8
   ↓
6. LLM综合信息生成回复
   "根据您的记录，8.5mmol/L需要结合测量时间判断..."
   ↓
7. 保存到记忆，返回用户
```

## 调试Agent

### 1. 开启详细日志

在`.env`中设置：
```env
AGENT_VERBOSE=True
DEBUG=True
```

### 2. 查看工具调用

在响应中会包含`tool_calls`字段：
```json
{
  "response": "...",
  "tool_calls": [
    {
      "tool": "query_health_data",
      "input": {"data_type": "blood_glucose", "days": 7},
      "output": "..."
    }
  ]
}
```

### 3. 测试单个工具

```python
# 在Python中直接测试
from app.agent.tools import HealthTools
from app.database import SessionLocal

db = SessionLocal()
tools = HealthTools(db, user_id=1)

result = tools.query_health_data("blood_glucose", days=7)
print(result)
```

## 优化Agent性能

### 1. 优化Prompt

- 更清晰的指令
- 更好的示例
- 更具体的约束

### 2. 优化工具

- 减少工具数量（LLM更容易选择）
- 优化工具描述
- 提高工具执行效率

### 3. 控制迭代次数

```python
AGENT_MAX_ITERATIONS=10  # 防止无限循环
```

### 4. 使用更强的模型

```env
OPENAI_MODEL=gpt-4-turbo-preview  # 更好的推理能力
```

## 常见问题

### Q1: Agent没有调用工具

**原因**：
- Prompt不够清晰
- 工具描述不够准确
- LLM认为不需要工具

**解决**：
- 在Prompt中强调"优先使用工具"
- 改进工具的docstring
- 提供调用工具的示例

### Q2: Agent调用了错误的工具

**原因**：
- 工具描述相似
- 参数命名不清晰

**解决**：
- 明确区分工具功能
- 使用更具体的工具名称
- 在docstring中说明使用场景

### Q3: Agent响应太慢

**原因**：
- 工具执行慢
- LLM推理慢
- 迭代次数过多

**解决**：
- 优化数据库查询
- 使用更快的模型
- 减少最大迭代次数

## 扩展建议

### 1. 添加更多工具

- 图表生成工具
- 邮件发送工具
- 数据导出工具
- 第三方API集成

### 2. 增强记忆能力

- 向量数据库存储对话
- 用户偏好学习
- 长期趋势分析

### 3. 多模态支持

- 图像识别（识别血糖仪读数）
- 语音交互
- 视频分析

### 4. 主动监测

- 定时任务检查健康数据
- 异常自动预警
- 主动发送提醒

## 参考资源

- [LangChain文档](https://python.langchain.com/)
- [OpenAI API文档](https://platform.openai.com/docs)
- [Agent设计模式](https://www.promptingguide.ai/)
