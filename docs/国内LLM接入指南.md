# 🇨🇳 国内LLM接入指南

本项目已支持多种国内大模型，完全免费，无需OpenAI账号！

---

## 🌟 推荐模型对比

| 模型 | 免费额度 | 性能 | Function Calling | 接入难度 | 推荐指数 |
|------|---------|------|-----------------|---------|---------|
| **智谱AI GLM-4** | 2500万Token | ⭐⭐⭐⭐⭐ | ✅ 支持 | ⭐ 最简单 | ⭐⭐⭐⭐⭐ |
| 阿里通义千问 | 100万Token | ⭐⭐⭐⭐ | ✅ 支持 | ⭐⭐ 简单 | ⭐⭐⭐⭐ |
| 百度文心一言 | 试用额度 | ⭐⭐⭐⭐ | ✅ 支持 | ⭐⭐ 简单 | ⭐⭐⭐ |
| 讯飞星火 | 试用额度 | ⭐⭐⭐ | ⚠️ 部分支持 | ⭐⭐⭐ 中等 | ⭐⭐⭐ |

**推荐：智谱AI GLM-4** ⭐

---

## 🚀 方案一：智谱AI（推荐）

### 为什么选择智谱AI？

1. ✅ **完全兼容OpenAI格式**（代码改动最小）
2. ✅ **免费额度最大**（2500万Token）
3. ✅ **支持Function Calling**（Agent必需）
4. ✅ **国内访问快**（不需要代理）
5. ✅ **性能强大**（接近GPT-4水平）

### 注册步骤

#### 1. 访问官网
https://open.bigmodel.cn/

#### 2. 注册账号
- 点击"注册/登录"
- 手机号注册
- 完成实名认证（需要身份证照片）

#### 3. 获取API Key
1. 登录后进入"控制台"
2. 左侧菜单 → "API密钥"
3. 点击"创建新的API Key"
4. 复制API Key（格式：`xxx.xxxxxxxxxx`）

#### 4. 查看免费额度
- 控制台首页可以看到Token余额
- 新用户自动获得2500万Token
- 足够用很久！

### 配置步骤

#### 1. 创建.env文件

```powershell
cd backend
copy .env.example .env
```

#### 2. 编辑.env文件

```env
# LLM配置
LLM_PROVIDER=zhipu
LLM_TEMPERATURE=0.7

# 智谱AI配置
ZHIPU_API_KEY=你的API_Key（替换这里）
ZHIPU_MODEL=glm-4
```

#### 3. 启动项目

```powershell
# 激活虚拟环境
venv\Scripts\activate

# 初始化数据库
python init_db.py

# 启动服务
python -m uvicorn app.main:app --reload --port 8000
```

#### 4. 测试

访问 http://localhost:5173，在AI助手中输入：
```
你好，请介绍一下你自己
```

如果能正常回复，说明配置成功！✅

### 模型选择

| 模型名称 | 特点 | 适用场景 | Token价格 |
|---------|------|---------|----------|
| glm-4 | 标准版 | 推荐使用 ⭐ | 免费 |
| glm-4-plus | 增强版 | 复杂推理 | 免费 |
| glm-4-flash | 快速版 | 简单对话 | 免费 |

**推荐使用 `glm-4`**

---

## 🔄 方案二：阿里通义千问

### 注册步骤

#### 1. 访问阿里云
https://dashscope.aliyun.com/

#### 2. 注册并开通
- 阿里云账号登录
- 开通"模型服务灵积"
- 实名认证

#### 3. 获取API Key
- 进入控制台
- 创建API Key
- 复制保存

### 代码修改

需要安装阿里云SDK：

```powershell
pip install dashscope
```

修改 `agent_core.py`：

```python
if llm_provider == "qwen":
    from langchain_community.llms import Tongyi
    self.llm = Tongyi(
        model_name="qwen-turbo",
        dashscope_api_key=os.getenv("QWEN_API_KEY")
    )
```

配置 `.env`：

```env
LLM_PROVIDER=qwen
QWEN_API_KEY=你的API_Key
```

---

## 🔄 方案三：百度文心一言

### 注册步骤

#### 1. 访问百度智能云
https://cloud.baidu.com/

#### 2. 开通文心一言
- 搜索"文心一言"
- 开通服务
- 创建应用

#### 3. 获取API Key
- 进入应用管理
- 获取API Key和Secret Key

### 代码修改

安装百度SDK：

```powershell
pip install qianfan
```

修改 `agent_core.py`：

```python
if llm_provider == "ernie":
    from langchain_community.llms import QianfanLLMEndpoint
    self.llm = QianfanLLMEndpoint(
        model="ERNIE-Bot-4",
        qianfan_ak=os.getenv("ERNIE_API_KEY"),
        qianfan_sk=os.getenv("ERNIE_SECRET_KEY")
    )
```

配置 `.env`：

```env
LLM_PROVIDER=ernie
ERNIE_API_KEY=你的API_Key
ERNIE_SECRET_KEY=你的Secret_Key
```

---

## 📊 性能对比

### 实测效果（慢病管理场景）

| 模型 | 响应速度 | 准确性 | 工具调用 | 中文理解 |
|------|---------|--------|---------|---------|
| 智谱GLM-4 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ 完美 | ⭐⭐⭐⭐⭐ |
| 通义千问 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ 良好 | ⭐⭐⭐⭐⭐ |
| 文心一言 | ⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ 良好 | ⭐⭐⭐⭐ |
| GPT-4 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ 完美 | ⭐⭐⭐⭐ |

**结论**：智谱GLM-4在国内场景下表现最佳！

---

## 💰 成本对比

### 免费额度

| 模型 | 新用户赠送 | 每日限额 | 有效期 |
|------|-----------|---------|--------|
| 智谱GLM-4 | 2500万Token | 无限制 | 长期 |
| 通义千问 | 100万Token | 有限制 | 3个月 |
| 文心一言 | 试用额度 | 有限制 | 1个月 |

### Token消耗估算

**本项目平均每次对话**：
- 输入：约500 Token
- 输出：约300 Token
- 合计：约800 Token

**智谱2500万Token可以支持**：
- 约 31,250 次对话
- 足够开发和测试！

---

## 🔧 切换模型

### 快速切换

只需修改 `.env` 文件：

```env
# 使用智谱AI
LLM_PROVIDER=zhipu
ZHIPU_API_KEY=xxx

# 或使用OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=xxx
```

重启服务即可！

---

## ✅ 配置检查清单

### 智谱AI配置检查

- [ ] 已注册智谱AI账号
- [ ] 已完成实名认证
- [ ] 已获取API Key
- [ ] 已创建 `.env` 文件
- [ ] 已填入 `ZHIPU_API_KEY`
- [ ] 已设置 `LLM_PROVIDER=zhipu`
- [ ] 已启动服务
- [ ] 已测试对话功能

---

## 🐛 常见问题

### Q1: API Key无效

**检查**：
- API Key格式是否正确（`xxx.xxxxxxxxxx`）
- 是否复制完整
- 是否有多余的空格

**解决**：
- 重新复制API Key
- 确保 `.env` 文件中没有引号

### Q2: 网络连接失败

**智谱AI**：
- 国内直接访问，不需要代理
- 检查网络连接

**OpenAI**：
- 需要代理或VPN
- 建议使用国内模型

### Q3: Token不足

**查看余额**：
- 登录智谱AI控制台
- 查看Token余额

**充值**：
- 新用户有2500万免费Token
- 用完后可以充值（很便宜）

### Q4: 不支持Function Calling

**确保使用**：
- 智谱：`glm-4` 或 `glm-4-plus`
- 通义：`qwen-turbo` 或 `qwen-plus`
- 文心：`ERNIE-Bot-4`

这些模型都支持Function Calling！

### Q5: 响应慢

**优化建议**：
- 使用 `glm-4-flash`（更快）
- 减少 `AGENT_MAX_ITERATIONS`
- 优化Prompt长度

---

## 🎯 最佳实践

### 开发阶段

```env
LLM_PROVIDER=zhipu
ZHIPU_MODEL=glm-4-flash  # 快速版，省Token
LLM_TEMPERATURE=0.7
AGENT_VERBOSE=True  # 开启调试
```

### 生产环境

```env
LLM_PROVIDER=zhipu
ZHIPU_MODEL=glm-4  # 标准版，性能好
LLM_TEMPERATURE=0.5  # 降低随机性
AGENT_VERBOSE=False  # 关闭调试
```

---

## 📞 技术支持

### 智谱AI
- 官网：https://open.bigmodel.cn/
- 文档：https://open.bigmodel.cn/dev/api
- 客服：在线客服

### 问题反馈
- 项目Issues
- 查看日志：`backend/logs/`

---

## 🎉 总结

**推荐配置**：

1. ✅ 使用智谱AI GLM-4
2. ✅ 免费额度大（2500万Token）
3. ✅ 性能强大（接近GPT-4）
4. ✅ 国内访问快
5. ✅ 完全兼容现有代码

**5分钟即可完成配置！** 🚀

---

## 📝 配置模板

复制以下内容到你的 `.env` 文件：

```env
# LLM配置
LLM_PROVIDER=zhipu
LLM_TEMPERATURE=0.7

# 智谱AI配置（推荐）
ZHIPU_API_KEY=你的API_Key
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

**现在就去注册智谱AI，开始使用吧！** 🎉
