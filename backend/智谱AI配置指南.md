# 智谱AI配置指南

## 第一步：获取API Key

1. 访问：https://open.bigmodel.cn/
2. 注册并登录
3. 进入"控制台" → "API密钥"
4. 创建新的API Key
5. 复制API Key（格式：xxx.xxxxxxxxxx）

## 第二步：配置.env文件

在 `backend` 目录下创建 `.env` 文件（如果不存在）：

```bash
# 复制模板
copy .env.example .env
```

然后编辑 `.env` 文件，修改以下内容：

```env
# LLM配置
LLM_PROVIDER=zhipu
LLM_TEMPERATURE=0.7

# 智谱AI配置
ZHIPU_API_KEY=你的智谱API_Key
ZHIPU_MODEL=glm-4

# 数据库配置
DATABASE_URL=sqlite:///./chronic_disease.db

# 向量数据库配置
CHROMA_PERSIST_DIRECTORY=./chroma_db

# 应用配置
APP_NAME=慢病管理AI智能体
APP_VERSION=1.0.0
DEBUG=True
LOG_LEVEL=INFO

# CORS配置
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]

# Agent配置
AGENT_MAX_ITERATIONS=10
AGENT_VERBOSE=True
```

## 第三步：启动项目

```powershell
cd backend

# 激活虚拟环境
venv\Scripts\activate

# 初始化数据库（如果还没有）
python init_db.py

# 启动服务
python -m uvicorn app.main:app --reload --port 8000
```

## 智谱AI模型选择

| 模型 | 特点 | 推荐场景 |
|------|------|---------|
| glm-4 | 标准版，性能强 | 推荐使用 ⭐ |
| glm-4-plus | 增强版，更强 | 复杂任务 |
| glm-4-flash | 快速版，便宜 | 简单对话 |

## 免费额度

- 新用户：2500万Token
- 每日限额：根据账号等级
- 足够开发和测试使用！

## 测试是否配置成功

启动后，在AI助手中输入：
```
你好，请介绍一下你自己
```

如果能正常回复，说明配置成功！

## 常见问题

### Q1: API Key格式错误
确保API Key格式为：`xxx.xxxxxxxxxx`

### Q2: 网络连接失败
智谱AI在国内，不需要代理，直接访问即可

### Q3: Token不足
登录控制台查看余额，新用户有2500万Token免费额度

## 切换回OpenAI

如果以后想用OpenAI，只需修改 `.env`：

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=你的OpenAI_Key
```

就这么简单！
