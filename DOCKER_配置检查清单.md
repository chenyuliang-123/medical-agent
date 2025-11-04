# Docker 部署配置检查清单

## ✅ 部署前检查

### 1. 环境准备
- [ ] Docker 已安装（版本 20.10+）
- [ ] Docker Compose 已安装（版本 2.0+）
- [ ] 端口 80 和 8000 未被占用
- [ ] 磁盘空间充足（至少 20GB）

### 2. LLM 配置（二选一）

#### 方案 A：智谱AI（推荐国内用户）
- [ ] 已注册智谱AI账号 https://open.bigmodel.cn/
- [ ] 已获取 API Key（格式：`xxx.xxxxxxxxxx`）
- [ ] 已在 `.env` 中配置：
  ```env
  LLM_PROVIDER=zhipu
  ZHIPU_API_KEY=你的密钥
  ZHIPU_MODEL=glm-4
  ```

#### 方案 B：OpenAI
- [ ] 已获取 OpenAI API Key（格式：`sk-xxx`）
- [ ] 已在 `.env` 中配置：
  ```env
  LLM_PROVIDER=openai
  OPENAI_API_KEY=你的密钥
  OPENAI_MODEL=gpt-4-turbo-preview
  ```

### 3. 配置文件检查

```bash
# 检查 .env 文件是否存在
ls -la .env

# 查看配置内容
cat .env

# 确保包含以下必需配置
grep "LLM_PROVIDER" .env
grep "ZHIPU_API_KEY\|OPENAI_API_KEY" .env
```

### 4. Docker 镜像加速配置

```bash
# 检查镜像加速配置
cat /etc/docker/daemon.json

# 应该包含类似内容：
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://dockerproxy.com"
  ]
}
```

---

## 🚀 部署步骤

### 步骤 1：准备配置文件

```bash
# 进入项目目录
cd /path/to/agent

# 复制环境变量模板
cp .env.example .env

# 编辑配置（使用智谱AI）
vi .env
```

**最小配置示例（智谱AI）：**
```env
# LLM 配置
LLM_PROVIDER=zhipu
ZHIPU_API_KEY=你的智谱API密钥
ZHIPU_MODEL=glm-4

# 其他配置使用默认值即可
```

### 步骤 2：创建必要目录

```bash
mkdir -p backend/data backend/logs backend/uploads
```

### 步骤 3：构建并启动

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 步骤 4：验证部署

```bash
# 检查容器状态（应该都是 Up）
docker-compose ps

# 测试后端健康检查
curl http://localhost:8000/health

# 测试前端
curl http://localhost/

# 查看后端日志
docker-compose logs backend --tail=50
```

---

## 🔍 配置验证

### 检查 LLM 配置是否生效

```bash
# 进入后端容器
docker-compose exec backend bash

# 查看环境变量
env | grep LLM
env | grep ZHIPU
env | grep OPENAI

# 退出容器
exit
```

### 测试 API 调用

```bash
# 测试健康检查
curl http://localhost:8000/health

# 测试 API 文档
curl http://localhost:8000/docs

# 查看 API 响应
curl -X GET http://localhost:8000/api/v1/patients
```

---

## ❌ 常见配置错误

### 错误 1：API Key 格式错误

**错误示例：**
```env
ZHIPU_API_KEY="xxx.xxxxxxxxxx"  # ❌ 不要加引号
ZHIPU_API_KEY=xxx.xxxxxxxxxx    # ✅ 正确
```

### 错误 2：LLM_PROVIDER 配置错误

**错误示例：**
```env
LLM_PROVIDER=OpenAI  # ❌ 大小写错误
LLM_PROVIDER=openai  # ✅ 正确（小写）
```

### 错误 3：缺少必需配置

```bash
# 检查是否缺少配置
docker-compose logs backend | grep -i "error\|missing\|required"
```

### 错误 4：环境变量未传递到容器

```bash
# 检查容器内的环境变量
docker-compose exec backend env | grep ZHIPU

# 如果为空，检查 docker-compose.yml 中是否正确配置
```

---

## 📋 完整配置模板

### 使用智谱AI（推荐）

```env
# ==================== LLM 配置 ====================
LLM_PROVIDER=zhipu
LLM_TEMPERATURE=0.7

# ==================== 智谱AI 配置 ====================
ZHIPU_API_KEY=你的智谱API密钥
ZHIPU_MODEL=glm-4

# ==================== 应用配置 ====================
APP_ENV=production
LOG_LEVEL=info

# ==================== 数据库配置 ====================
DATABASE_URL=sqlite:///./data/agent.db
CHROMA_PERSIST_DIRECTORY=./data/chroma_db

# ==================== Agent 配置 ====================
AGENT_MAX_ITERATIONS=10
AGENT_VERBOSE=True

# ==================== CORS 配置 ====================
CORS_ORIGINS=http://localhost,http://localhost:80
```

### 使用 OpenAI

```env
# ==================== LLM 配置 ====================
LLM_PROVIDER=openai
LLM_TEMPERATURE=0.7

# ==================== OpenAI 配置 ====================
OPENAI_API_KEY=sk-你的OpenAI密钥
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_MODEL=gpt-4-turbo-preview

# ==================== 应用配置 ====================
APP_ENV=production
LOG_LEVEL=info

# ==================== 数据库配置 ====================
DATABASE_URL=sqlite:///./data/agent.db
CHROMA_PERSIST_DIRECTORY=./data/chroma_db

# ==================== Agent 配置 ====================
AGENT_MAX_ITERATIONS=10
AGENT_VERBOSE=True

# ==================== CORS 配置 ====================
CORS_ORIGINS=http://localhost,http://localhost:80
```

---

## 🎯 快速诊断命令

```bash
# 一键检查所有配置
cat << 'EOF' > check_config.sh
#!/bin/bash
echo "=== 配置检查 ==="
echo "1. 检查 .env 文件"
[ -f .env ] && echo "✅ .env 文件存在" || echo "❌ .env 文件不存在"

echo ""
echo "2. 检查 LLM 配置"
grep -q "LLM_PROVIDER" .env && echo "✅ LLM_PROVIDER 已配置" || echo "❌ LLM_PROVIDER 未配置"

echo ""
echo "3. 检查 API Key"
if grep -q "ZHIPU_API_KEY" .env && ! grep -q "your_zhipu_api_key_here" .env; then
    echo "✅ 智谱AI密钥已配置"
elif grep -q "OPENAI_API_KEY" .env && ! grep -q "your_openai_api_key_here" .env; then
    echo "✅ OpenAI密钥已配置"
else
    echo "❌ API密钥未配置或使用默认值"
fi

echo ""
echo "4. 检查 Docker 服务"
docker-compose ps

echo ""
echo "5. 检查后端健康状态"
curl -s http://localhost:8000/health || echo "❌ 后端服务未响应"
EOF

chmod +x check_config.sh
./check_config.sh
```

---

## 📞 获取帮助

如果遇到问题：

1. **查看日志**
   ```bash
   docker-compose logs backend --tail=100
   ```

2. **检查配置**
   ```bash
   ./check_config.sh
   ```

3. **重新部署**
   ```bash
   docker-compose down
   docker-compose up -d
   ```

4. **查看详细文档**
   - Docker 部署指南：`DOCKER_DEPLOY.md`
   - 智谱AI配置：`使用国内LLM快速开始.md`
   - 国内LLM接入：`docs/国内LLM接入指南.md`

---

**祝您部署顺利！** 🚀
