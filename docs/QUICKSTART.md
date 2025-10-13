# 快速开始指南

## 环境要求

- Python 3.10+
- Node.js 18+
- OpenAI API Key

## 第一步：配置后端

### 1. 进入后端目录

```powershell
cd backend
```

### 2. 创建虚拟环境

```powershell
python -m venv venv
venv\Scripts\activate
```

### 3. 安装依赖

```powershell
pip install -r requirements.txt
```

### 4. 配置环境变量

```powershell
# 复制环境变量模板
copy .env.example .env

# 编辑.env文件，填入你的OpenAI API Key
notepad .env
```

在`.env`文件中修改：
```env
OPENAI_API_KEY=sk-your-api-key-here
```

### 5. 初始化数据库

```powershell
python init_db.py
```

这会创建数据库并添加示例数据。

### 6. 启动后端服务

```powershell
python -m uvicorn app.main:app --reload --port 8000
```

后端服务启动在：http://localhost:8000

API文档：http://localhost:8000/docs

## 第二步：配置前端

### 1. 打开新的终端，进入前端目录

```powershell
cd frontend
```

### 2. 安装依赖

```powershell
npm install
```

### 3. 启动前端服务

```powershell
npm run dev
```

前端服务启动在：http://localhost:5173

## 第三步：开始使用

1. 打开浏览器访问：http://localhost:5173

2. 默认使用用户ID=1（张三）

3. 在AI助手页面开始对话，例如：
   - "查询我最近的血糖数据"
   - "我今天测的血糖是8.5，正常吗？"
   - "给我一些饮食建议"
   - "设置明天早上7点的血糖测量提醒"

## 常见问题

### Q1: OpenAI API调用失败

**A:** 检查以下几点：
- API Key是否正确
- 网络是否可以访问OpenAI
- 账户余额是否充足

如果无法访问OpenAI，可以考虑：
- 使用代理
- 使用国内的LLM API（需要修改代码）
- 使用本地LLM（如Ollama）

### Q2: 数据库错误

**A:** 删除`chronic_disease.db`文件，重新运行`python init_db.py`

### Q3: 前端无法连接后端

**A:** 确保：
- 后端服务正在运行（http://localhost:8000）
- 检查`vite.config.ts`中的代理配置

### Q4: 依赖安装失败

**A:** 
- Python依赖：尝试使用国内镜像 `pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`
- Node依赖：尝试使用淘宝镜像 `npm install --registry=https://registry.npmmirror.com`

## 测试Agent功能

### 测试工具调用

在AI助手中输入：
```
查询我最近7天的血糖数据
```

你应该看到Agent调用`query_health_data`工具，并返回数据分析。

### 测试趋势分析

```
分析我最近的血糖趋势
```

Agent会调用`analyze_health_trend`工具进行分析。

### 测试提醒创建

```
设置明天早上7点的血糖测量提醒
```

Agent会调用`create_reminder`工具创建提醒。

### 测试知识检索

```
糖尿病患者应该如何饮食？
```

Agent会调用`search_knowledge`工具检索知识库。

## 下一步

- 查看 [API文档](http://localhost:8000/docs)
- 阅读 [开发文档](./DEVELOPMENT.md)
- 自定义Agent行为（修改`backend/app/agent/prompts.py`）
- 添加新工具（修改`backend/app/agent/tools.py`）

## 技术支持

如有问题，请查看：
- README.md
- 项目Issues
- API文档
