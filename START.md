# 🚀 慢病管理AI智能体 - 启动指南

## ✨ 项目特色

这是一个**真正的AI智能体系统**，而不是普通程序！

### 智能体核心特性

✅ **自主推理决策** - 基于LangChain的Agent框架，能够自主分析和决策  
✅ **工具调用能力** - 动态调用6种工具完成复杂任务  
✅ **上下文记忆** - 记住对话历史和用户信息  
✅ **主动监测** - 能够主动发现问题并提供建议  
✅ **知识检索** - RAG技术，检索医疗知识库  
✅ **自然语言交互** - 流畅的多轮对话

---

## 📋 快速启动（3步）

### 第一步：配置后端

```powershell
# 1. 进入后端目录
cd backend

# 2. 创建虚拟环境
python -m venv venv
venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置API Key
copy .env.example .env
# 编辑.env文件，填入你的OpenAI API Key

# 5. 初始化数据库（创建示例数据）
python init_db.py

# 6. 启动后端
python -m uvicorn app.main:app --reload --port 8000
```

**后端启动成功！** 访问 http://localhost:8000/docs 查看API文档

---

### 第二步：配置前端

**打开新的终端窗口**

```powershell
# 1. 进入前端目录
cd frontend

# 2. 安装依赖
npm install

# 3. 启动前端
npm run dev
```

**前端启动成功！** 访问 http://localhost:5173

---

### 第三步：开始使用

1. 打开浏览器：http://localhost:5173
2. 点击"AI助手"
3. 开始对话！

---

## 💬 测试Agent能力

### 1️⃣ 测试数据查询工具

输入：
```
查询我最近7天的血糖数据
```

**Agent会做什么：**
- 调用 `query_health_data` 工具
- 查询数据库
- 分析数据并返回

---

### 2️⃣ 测试趋势分析工具

输入：
```
分析我最近的血糖趋势
```

**Agent会做什么：**
- 调用 `analyze_health_trend` 工具
- 计算平均值、最大值、最小值
- 判断趋势（上升/下降/平稳）
- 统计异常次数

---

### 3️⃣ 测试提醒创建工具

输入：
```
设置明天早上7点的血糖测量提醒
```

**Agent会做什么：**
- 调用 `create_reminder` 工具
- 解析时间
- 创建提醒记录
- 确认创建成功

---

### 4️⃣ 测试知识检索工具

输入：
```
糖尿病患者应该如何饮食？
```

**Agent会做什么：**
- 调用 `search_knowledge` 工具
- 检索知识库
- 返回专业建议

---

### 5️⃣ 测试健康指标计算工具

输入：
```
帮我计算BMI，我的体重是72kg，身高170cm
```

**Agent会做什么：**
- 调用 `calculate_health_metrics` 工具
- 计算BMI值
- 判断健康状态

---

### 6️⃣ 测试多工具协作

输入：
```
我今天测的血糖是8.5，这正常吗？如果不正常应该怎么办？
```

**Agent会做什么：**
1. 调用 `query_health_data` 查询历史数据
2. 调用 `search_knowledge` 查询正常范围
3. 综合分析给出建议
4. 可能调用 `create_reminder` 设置复测提醒

---

## 🎯 Agent vs 普通程序对比

| 场景 | 普通程序 | AI智能体 |
|------|---------|----------|
| 用户说"血糖8.5" | ❌ 无法理解 | ✅ 自动询问测量时间，查询历史，给出建议 |
| 查询数据 | ❌ 需要点击按钮选择 | ✅ 自然语言："查询我最近的血糖" |
| 异常处理 | ❌ 只显示数据 | ✅ 主动分析，发现异常，给出建议 |
| 多步骤任务 | ❌ 需要多次操作 | ✅ 一句话完成："分析血糖并设置提醒" |

---

## 🛠️ 技术架构

```
┌─────────────────────────────────────────┐
│         用户（自然语言输入）              │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│    LangChain Agent (GPT-4)              │
│    - 理解意图                            │
│    - 制定计划                            │
│    - 决策工具调用                        │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│         工具集 (Tools)                   │
│  ├─ query_health_data                   │
│  ├─ analyze_health_trend                │
│  ├─ create_reminder                     │
│  ├─ search_knowledge                    │
│  ├─ calculate_health_metrics            │
│  └─ ...                                 │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│         数据层                           │
│  ├─ SQLite数据库                        │
│  ├─ 知识库                              │
│  └─ 记忆系统                            │
└─────────────────────────────────────────┘
```

---

## 📁 项目结构

```
agent/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── agent/             # 🤖 AI智能体核心
│   │   │   ├── agent_core.py  # Agent引擎
│   │   │   ├── tools.py       # 工具集（6个工具）
│   │   │   ├── memory.py      # 记忆系统
│   │   │   └── prompts.py     # Prompt工程
│   │   ├── api/               # API路由
│   │   ├── models/            # 数据模型
│   │   └── main.py            # 应用入口
│   └── init_db.py             # 数据库初始化
├── frontend/                   # 前端应用
│   └── src/
│       ├── views/             # 页面组件
│       └── api/               # API调用
├── knowledge/                  # 📚 知识库
│   └── chronic_disease.json   # 慢病知识
└── docs/                       # 📖 文档
    ├── QUICKSTART.md          # 快速开始
    └── AGENT_GUIDE.md         # Agent开发指南
```

---

## 🎓 学习资源

### 1. 理解Agent概念
阅读：`docs/AGENT_GUIDE.md`

### 2. 查看API文档
访问：http://localhost:8000/docs

### 3. 自定义Agent行为
编辑：`backend/app/agent/prompts.py`

### 4. 添加新工具
编辑：`backend/app/agent/tools.py`

---

## ⚙️ 配置说明

### OpenAI API配置

在 `backend/.env` 中：

```env
# 使用GPT-4（推荐，推理能力强）
OPENAI_API_KEY=sk-your-key
OPENAI_MODEL=gpt-4-turbo-preview

# 或使用GPT-3.5（更快，更便宜）
OPENAI_MODEL=gpt-3.5-turbo
```

### 使用国内LLM

如果无法访问OpenAI，可以修改为：
- 智谱AI (GLM-4)
- 阿里云通义千问
- 百度文心一言

需要修改 `backend/app/agent/agent_core.py` 中的LLM初始化代码。

---

## 🐛 常见问题

### Q1: OpenAI API调用失败

**解决方案：**
1. 检查API Key是否正确
2. 检查网络连接
3. 检查账户余额
4. 考虑使用代理或国内LLM

### Q2: 依赖安装失败

**Python依赖：**
```powershell
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**Node依赖：**
```powershell
npm install --registry=https://registry.npmmirror.com
```

### Q3: 数据库错误

删除数据库文件重新初始化：
```powershell
del chronic_disease.db
python init_db.py
```

---

## 📊 示例数据

初始化后会创建：
- ✅ 1个测试用户（张三，55岁，糖尿病+高血压）
- ✅ 21条血糖数据（最近7天）
- ✅ 14条血压数据（最近7天）
- ✅ 7条体重数据（最近7天）
- ✅ 4条提醒（每日重复）

---

## 🎯 向老板展示

### 展示要点

1. **这是AI智能体，不是普通程序**
   - 展示自然语言交互
   - 展示工具调用过程
   - 展示推理决策能力

2. **核心技术亮点**
   - LangChain Agent框架
   - 工具调用（Tool Calling）
   - RAG知识检索
   - 记忆系统

3. **实际应用价值**
   - 提升患者体验
   - 减少医护工作量
   - 24小时在线服务
   - 个性化健康管理

### 演示流程

```
1. 打开系统，展示界面
   ↓
2. 输入："查询我最近的血糖数据"
   → 展示Agent调用工具
   ↓
3. 输入："我今天测的血糖是8.5，正常吗？"
   → 展示多工具协作
   ↓
4. 输入："给我制定一个降血糖的计划"
   → 展示推理规划能力
   ↓
5. 打开"健康概览"，展示数据可视化
   ↓
6. 说明技术架构和扩展性
```

---

## 🚀 下一步扩展

- [ ] 集成可穿戴设备数据
- [ ] 添加图像识别（识别血糖仪读数）
- [ ] 多模态支持（语音交互）
- [ ] 医生协作功能
- [ ] 移动端App
- [ ] 更多慢性病类型

---

## 📞 技术支持

- 📖 查看完整文档：`README.md`
- 🔧 Agent开发指南：`docs/AGENT_GUIDE.md`
- 🚀 快速开始：`docs/QUICKSTART.md`
- 💻 API文档：http://localhost:8000/docs

---

## ⚠️ 重要提醒

**医疗免责声明：**
- 本系统仅供健康管理参考
- 不能替代专业医疗诊断
- 遇到紧急情况请立即就医
- 用药调整需咨询医生

---

## 🎉 开始你的AI智能体之旅！

现在你已经拥有了一个完整的AI智能体系统，它能够：
- 🤖 自主推理和决策
- 🛠️ 调用工具完成任务
- 💭 记住对话和用户信息
- 📚 检索知识库
- 🎯 主动发现问题

**祝你成功向老板展示！** 🚀
