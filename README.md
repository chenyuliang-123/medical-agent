# 慢病管理AI智能体系统

## 项目简介

这是一个基于LangChain的AI智能体系统，专注于慢性病（糖尿病、高血压）的智能管理。

### 核心特性

- 🤖 **AI智能体引擎**：基于LangChain的Agent框架，具备自主推理和决策能力
- 🛠️ **工具调用系统**：支持多种工具动态调用（数据查询、分析、提醒等）
- 💬 **自然语言交互**：支持多轮对话，理解上下文
- 📊 **健康数据监测**：血糖、血压、体重等指标追踪
- 🎯 **主动预警**：智能分析健康数据，主动发现异常
- 📚 **知识库检索**：RAG技术，提供专业医疗建议
- 📈 **数据可视化**：健康趋势图表展示
- 🔔 **智能提醒**：用药、复查、运动提醒

## 技术栈

### 后端
- Python 3.10+
- FastAPI - Web框架
- LangChain - Agent框架
- OpenAI GPT-4 / Claude - LLM
- ChromaDB - 向量数据库
- SQLAlchemy - ORM
- SQLite - 数据库

### 前端
- Vue 3 + TypeScript
- Element Plus - UI组件库
- ECharts - 数据可视化
- Axios - HTTP客户端
- Pinia - 状态管理

## 项目结构

```
agent/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── agent/             # AI智能体核心
│   │   │   ├── agent_core.py  # Agent引擎
│   │   │   ├── tools.py       # 工具集定义
│   │   │   ├── memory.py      # 记忆系统
│   │   │   └── prompts.py     # Prompt模板
│   │   ├── api/               # API路由
│   │   ├── models/            # 数据模型
│   │   ├── services/          # 业务逻辑
│   │   ├── database/          # 数据库配置
│   │   └── main.py            # 应用入口
│   └── requirements.txt
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── views/             # 页面
│   │   ├── components/        # 组件
│   │   └── api/               # API调用
│   └── package.json
├── knowledge/                  # 知识库
│   └── chronic_disease.json
└── docs/                       # 文档
```

## 快速开始

### 1. 环境准备

```bash
# Python 3.10+
# Node.js 18+
```

### 2. 后端启动

```bash
cd backend

# 创建虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
copy .env.example .env
# 编辑.env文件，填入OpenAI API Key

# 启动服务
python -m uvicorn app.main:app --reload --port 8000
```

### 3. 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 4. 访问应用

- 前端：http://localhost:5173
- 后端API文档：http://localhost:8000/docs

## AI智能体能力

### 1. 工具调用能力
- 查询健康数据
- 分析健康趋势
- 计算健康指标
- 检索医疗知识
- 生成健康报告
- 设置提醒

### 2. 推理与规划
- 健康状态评估
- 风险预测
- 制定健康计划
- 多步骤任务分解

### 3. 主动监测
- 定时健康检查
- 异常自动预警
- 主动发送提醒

### 4. 记忆系统
- 对话上下文记忆
- 用户健康档案
- 历史数据追踪
- 个性化偏好

## 使用示例

### 对话示例1：健康咨询
```
用户：我今天测的血糖是8.5mmol/L，这正常吗？

智能体：
[调用工具：查询用户历史血糖数据]
[调用工具：检索血糖知识库]

根据您的记录，这是餐后2小时的血糖值。
相比您上周的平均值7.8mmol/L有所升高。

分析：
- 正常餐后2小时血糖应<7.8mmol/L
- 您的值略高，需要关注

建议：
1. 回忆今天是否摄入了较多碳水化合物？
2. 建议明天早上空腹再测一次
3. 如果连续3天>8.0，建议联系医生调整用药

我已为您设置明早7:00的测量提醒。
```

### 对话示例2：健康计划
```
用户：帮我制定一个降血糖的计划

智能体：
[分析用户健康数据]
[制定个性化方案]

根据您的情况，我为您制定了4周血糖控制计划：

第1周：建立监测习惯
- 每日3次血糖监测（空腹、餐后2h、睡前）
- 记录饮食和运动

第2周：饮食调整
- 减少精制碳水摄入
- 增加膳食纤维
- 控制每餐主食量在100g

第3周：增加运动
- 每天30分钟快走
- 餐后1小时开始

第4周：巩固习惯
- 评估效果
- 调整方案

我会每周提醒您完成目标，需要开始吗？
```

## 开发指南

### 添加新工具

```python
# backend/app/agent/tools.py

from langchain.tools import tool

@tool
def your_new_tool(param: str) -> str:
    """工具描述，Agent会根据这个描述决定何时调用"""
    # 实现工具逻辑
    return result
```

### 自定义Prompt

编辑 `backend/app/agent/prompts.py` 中的系统提示词。

### 扩展知识库

在 `knowledge/` 目录添加新的知识文档，系统会自动加载。

## API文档

启动后端后访问：http://localhost:8000/docs

主要接口：
- `POST /api/chat` - 与智能体对话
- `GET /api/health-data` - 获取健康数据
- `POST /api/health-data` - 添加健康数据
- `GET /api/reports` - 获取健康报告

## 配置说明

### 环境变量（.env）

```env
# OpenAI配置
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4-turbo-preview

# 数据库
DATABASE_URL=sqlite:///./chronic_disease.db

# 向量数据库
CHROMA_PERSIST_DIRECTORY=./chroma_db

# 应用配置
DEBUG=True
LOG_LEVEL=INFO
```

## 注意事项

⚠️ **医疗免责声明**
- 本系统仅供健康管理参考，不能替代专业医疗诊断
- 遇到紧急情况请立即就医
- 用药调整需咨询医生

## 后续扩展

- [ ] 支持更多慢性病类型
- [ ] 集成可穿戴设备数据
- [ ] 多模态支持（图像识别）
- [ ] 移动端App
- [ ] 医生协作功能

## License

MIT

## 联系方式

如有问题，请提Issue或联系开发者。
