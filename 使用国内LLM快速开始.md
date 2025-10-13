# 🇨🇳 使用国内LLM快速开始

**无需OpenAI账号！** 使用国内免费的智谱AI，5分钟完成配置！

---

## 🚀 快速配置（3步）

### 第一步：注册智谱AI（2分钟）

1. **访问官网**：https://open.bigmodel.cn/
2. **注册账号**：使用手机号注册
3. **实名认证**：上传身份证照片
4. **获取API Key**：
   - 进入"控制台"
   - 点击"API密钥"
   - 创建新密钥
   - 复制API Key（格式：`xxx.xxxxxxxxxx`）

**免费额度**：新用户自动获得 **2500万Token**！

---

### 第二步：配置项目（1分钟）

#### 方法A：使用配置脚本（推荐）

```powershell
cd backend
.\配置智谱AI.bat
```

脚本会自动：
- ✅ 创建`.env`文件
- ✅ 打开编辑器
- ✅ 提示配置步骤

#### 方法B：手动配置

```powershell
cd backend
copy .env.example .env
notepad .env
```

在`.env`文件中修改：

```env
# LLM配置
LLM_PROVIDER=zhipu
LLM_TEMPERATURE=0.7

# 智谱AI配置
ZHIPU_API_KEY=你的API_Key（替换这里）
ZHIPU_MODEL=glm-4
```

---

### 第三步：启动项目（2分钟）

```powershell
# 1. 激活虚拟环境（如果还没有）
python -m venv venv
venv\Scripts\activate
cd .\backend\
# 2. 安装依赖（首次）
# 1. 先升级pip到最新版本
python -m pip install --upgrade pip

# 2. 使用国内镜像安装依赖（更快更稳定）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 3. 初始化数据库（首次）
python init_db.py

# 4. 启动后端
python -m uvicorn app.main:app --reload --port 8000
```

**新终端启动前端**：

```powershell
cd frontend
npm install
npm run dev
```

---

## ✅ 测试是否成功

### 1. 访问前端

打开浏览器：http://localhost:5173

### 2. 测试对话

在AI助手中输入：
```
你好，请介绍一下你自己
```

如果能正常回复，说明配置成功！🎉

### 3. 测试工具调用

输入：
```
查询我最近的血糖数据
```

应该能看到Agent调用工具并返回数据。

---

## 📊 智谱AI vs OpenAI

| 对比项 | 智谱AI GLM-4 | OpenAI GPT-4 |
|--------|-------------|--------------|
| **免费额度** | 2500万Token ✅ | 需要付费 ❌ |
| **注册难度** | 手机号+身份证 ✅ | 需要国外手机号 ❌ |
| **访问速度** | 国内快 ✅ | 需要代理 ❌ |
| **性能** | 接近GPT-4 ⭐⭐⭐⭐ | 最强 ⭐⭐⭐⭐⭐ |
| **Function Calling** | 支持 ✅ | 支持 ✅ |
| **中文理解** | 优秀 ⭐⭐⭐⭐⭐ | 良好 ⭐⭐⭐⭐ |

**结论**：国内开发推荐智谱AI！

---

## 💰 成本对比

### 智谱AI免费额度

- **新用户赠送**：2500万Token
- **可支持对话**：约31,250次
- **够用时长**：开发测试完全够用

### 实际消耗

**本项目平均每次对话**：
- 输入：~500 Token
- 输出：~300 Token
- 合计：~800 Token

**2500万Token可以用多久**：
- 每天10次对话：约3年
- 每天50次对话：约7个月
- 每天100次对话：约3个月

**完全够用！** ✅

---

## 🎯 模型选择

智谱AI提供3个模型：

| 模型 | 特点 | 适用场景 | 推荐 |
|------|------|---------|------|
| **glm-4** | 标准版 | 日常使用 | ⭐⭐⭐⭐⭐ |
| glm-4-plus | 增强版 | 复杂推理 | ⭐⭐⭐⭐ |
| glm-4-flash | 快速版 | 简单对话 | ⭐⭐⭐ |

**推荐使用 `glm-4`**（性能和速度平衡）

---

## 🔧 常见问题

### Q1: API Key无效

**检查**：
- 格式是否正确（`xxx.xxxxxxxxxx`）
- 是否完整复制
- `.env`文件中是否有引号（不要加引号）

**正确格式**：
```env
ZHIPU_API_KEY=xxx.xxxxxxxxxx
```

**错误格式**：
```env
ZHIPU_API_KEY="xxx.xxxxxxxxxx"  # ❌ 不要加引号
```

### Q2: 找不到.env文件

```powershell
# 创建.env文件
cd backend
copy .env.example .env
```

### Q3: Token不足

**查看余额**：
- 登录智谱AI控制台
- 查看Token余额

**充值**：
- 新用户有2500万免费Token
- 用完后可以充值（很便宜）

### Q4: 响应慢

**优化方案**：
```env
# 使用快速版模型
ZHIPU_MODEL=glm-4-flash

# 减少迭代次数
AGENT_MAX_ITERATIONS=5
```

### Q5: 不支持Function Calling

**确保使用**：
- `glm-4`（支持）✅
- `glm-4-plus`（支持）✅
- `glm-4-flash`（支持）✅

所有模型都支持Function Calling！

---

## 📝 完整配置示例

### .env文件内容

```env
# LLM配置
LLM_PROVIDER=zhipu
LLM_TEMPERATURE=0.7

# 智谱AI配置
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

---

## 🎓 更多资源

### 官方文档
- 智谱AI官网：https://open.bigmodel.cn/
- API文档：https://open.bigmodel.cn/dev/api
- 模型介绍：https://open.bigmodel.cn/dev/howuse/model

### 项目文档
- 详细教程：[docs/国内LLM接入指南.md](docs/国内LLM接入指南.md)
- 快速开始：[START.md](START.md)
- Agent开发：[docs/AGENT_GUIDE.md](docs/AGENT_GUIDE.md)

---

## 🎉 开始使用

现在你已经配置好了！

**下一步**：
1. ✅ 启动项目
2. ✅ 测试对话功能
3. ✅ 体验Agent能力
4. ✅ 向老板展示

**祝你成功！** 🚀

---

## 💡 提示

### 切换到OpenAI

如果以后想用OpenAI，只需修改`.env`：

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=你的OpenAI_Key
```

### 同时支持多个模型

代码已经支持多个LLM提供商，随时切换！

---

## 📞 需要帮助？

- 查看文档：`docs/国内LLM接入指南.md`
- 智谱AI客服：官网在线客服
- 项目Issues：提交问题

**现在就去注册智谱AI，开始你的AI智能体之旅吧！** 🎉
