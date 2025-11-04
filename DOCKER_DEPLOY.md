# 🐳 慢病管理AI智能体 - Docker 部署指南

## 📋 目录

- [系统要求](#系统要求)
- [快速开始](#快速开始)
- [详细部署步骤](#详细部署步骤)
- [配置说明](#配置说明)
- [常用命令](#常用命令)
- [故障排查](#故障排查)
- [生产环境优化](#生产环境优化)

---

## 系统要求

### 软件依赖
- **Docker**: 20.10+ 
- **Docker Compose**: 2.0+
- **操作系统**: Linux / macOS / Windows (with WSL2)

### 硬件配置
- **CPU**: 2核心以上
- **内存**: 4GB以上（推荐8GB）
- **磁盘**: 20GB以上可用空间

---

## 快速开始

### 1. 安装 Docker

**Ubuntu/Debian:**
```bash
# 安装 Docker
curl -fsSL https://get.docker.com | bash

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker

# 添加当前用户到 docker 组
sudo usermod -aG docker $USER
newgrp docker
```

**CentOS/RHEL:**
```bash
# 安装 Docker
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker

# 添加当前用户到 docker 组
sudo usermod -aG docker $USER
newgrp docker
```

### 2. 安装 Docker Compose

```bash
# 下载 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 添加执行权限
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker-compose --version
```

### 3. 一键部署

```bash
# 克隆或上传项目到服务器
cd /path/to/agent

# 配置环境变量
cp .env.example .env
nano .env  # 编辑配置，设置 OPENAI_API_KEY

# 执行部署脚本
chmod +x deploy.sh
./deploy.sh
```

部署完成后访问：
- **前端**: http://localhost
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

---

## 详细部署步骤

### 步骤 1: 准备项目文件

```bash
# 上传项目到服务器
scp -r ./agent user@server:/opt/

# 或使用 git
cd /opt
git clone <your-repo-url> agent
cd agent
```

### 步骤 2: 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置文件
vim .env
```

**配置说明：**

项目支持两种 LLM 提供商，选择其中一种配置即可：

#### 方案 A：使用智谱AI（推荐国内用户）

```env
# LLM 配置
LLM_PROVIDER=zhipu
LLM_TEMPERATURE=0.7

# 智谱AI 配置
ZHIPU_API_KEY=your_zhipu_api_key_here
ZHIPU_MODEL=glm-4
```

**获取智谱AI密钥：**
1. 访问 https://open.bigmodel.cn/
2. 注册并实名认证
3. 进入控制台 → API密钥 → 创建新密钥
4. 复制密钥（格式：`xxx.xxxxxxxxxx`）
5. 新用户免费赠送 **2500万 Token**

#### 方案 B：使用 OpenAI

```env
# LLM 配置
LLM_PROVIDER=openai
LLM_TEMPERATURE=0.7

# OpenAI 配置
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_MODEL=gpt-4-turbo-preview
```

**其他配置项：**
```env
# 数据库配置
DATABASE_URL=sqlite:///./data/agent.db

# 向量数据库
CHROMA_PERSIST_DIRECTORY=./data/chroma_db

# Agent 配置
AGENT_MAX_ITERATIONS=10
AGENT_VERBOSE=True
```

### 步骤 3: 构建镜像

```bash
# 构建所有服务镜像
docker-compose build

# 或单独构建
docker-compose build backend
docker-compose build frontend
```

### 步骤 4: 启动服务

```bash
# 启动所有服务（后台运行）
docker-compose up -d

# 查看启动日志
docker-compose logs -f
```

### 步骤 5: 验证部署

```bash
# 检查容器状态
docker-compose ps

# 测试后端 API
curl http://localhost:8000/health

# 测试前端
curl http://localhost/
```

---

## 配置说明

### Docker Compose 配置

**端口映射:**
- `80:80` - 前端服务
- `8000:8000` - 后端 API

**数据持久化:**
- `./backend/data` - 数据库文件
- `./backend/logs` - 应用日志
- `./backend/uploads` - 上传文件

### 环境变量完整列表

#### LLM 配置

| 变量名 | 说明 | 默认值 | 必填 |
|--------|------|--------|------|
| `LLM_PROVIDER` | LLM提供商 | zhipu | ✅ |
| `LLM_TEMPERATURE` | 温度参数 | 0.7 | ❌ |

#### OpenAI 配置（LLM_PROVIDER=openai 时）

| 变量名 | 说明 | 默认值 | 必填 |
|--------|------|--------|------|
| `OPENAI_API_KEY` | OpenAI API 密钥 | - | ✅ |
| `OPENAI_API_BASE` | API 基础地址 | https://api.openai.com/v1 | ❌ |
| `OPENAI_MODEL` | 模型名称 | gpt-4-turbo-preview | ❌ |

#### 智谱AI 配置（LLM_PROVIDER=zhipu 时，推荐）

| 变量名 | 说明 | 默认值 | 必填 |
|--------|------|--------|------|
| `ZHIPU_API_KEY` | 智谱AI API 密钥 | - | ✅ |
| `ZHIPU_MODEL` | 模型名称 | glm-4 | ❌ |

**智谱AI模型选择：**
- `glm-4` - 标准版（推荐）
- `glm-4-plus` - 增强版
- `glm-4-flash` - 快速版

#### 应用配置

| 变量名 | 说明 | 默认值 | 必填 |
|--------|------|--------|------|
| `APP_ENV` | 运行环境 | production | ❌ |
| `LOG_LEVEL` | 日志级别 | info | ❌ |
| `DATABASE_URL` | 数据库连接 | sqlite:///./data/agent.db | ❌ |
| `CHROMA_PERSIST_DIRECTORY` | 向量数据库目录 | ./data/chroma_db | ❌ |
| `AGENT_MAX_ITERATIONS` | Agent最大迭代次数 | 10 | ❌ |
| `AGENT_VERBOSE` | 是否显示详细日志 | True | ❌ |

---

## 常用命令

### 服务管理

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 重启单个服务
docker-compose restart backend
docker-compose restart frontend

# 查看服务状态
docker-compose ps

# 查看资源使用
docker stats
```

### 日志查看

```bash
# 查看所有日志
docker-compose logs

# 实时查看日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs backend
docker-compose logs frontend

# 查看最近 100 行日志
docker-compose logs --tail=100
```

### 进入容器

```bash
# 进入后端容器
docker-compose exec backend bash

# 进入前端容器
docker-compose exec frontend sh

# 执行命令
docker-compose exec backend python manage.py migrate
```

### 数据备份

```bash
# 备份数据目录
tar -czf backup-$(date +%Y%m%d).tar.gz backend/data backend/logs

# 恢复数据
tar -xzf backup-20240101.tar.gz
```

### 更新部署

```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# 或使用脚本
./deploy.sh
```

---

## 故障排查

### 问题 1: 容器无法启动

```bash
# 查看详细日志
docker-compose logs backend
docker-compose logs frontend

# 检查容器状态
docker-compose ps

# 重新构建
docker-compose build --no-cache
docker-compose up -d
```

### 问题 2: 端口被占用

```bash
# 检查端口占用
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :8000

# 修改 docker-compose.yml 中的端口映射
# 例如: "8080:80" 或 "8001:8000"
```

### 问题 3: 后端 API 连接失败

```bash
# 检查后端健康状态
curl http://localhost:8000/health

# 检查环境变量
docker-compose exec backend env | grep OPENAI

# 查看后端日志
docker-compose logs backend --tail=100
```

### 问题 4: 前端无法访问后端

检查 `frontend/nginx.conf` 中的代理配置:
```nginx
location /api/ {
    proxy_pass http://backend:8000/api/;
    # ...
}
```

### 问题 5: 数据库连接错误

```bash
# 检查数据目录权限
ls -la backend/data/

# 重新创建数据库
docker-compose exec backend python -c "from database import init_db; init_db()"
```

---

## 生产环境优化

### 1. 使用 HTTPS

创建 `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  frontend:
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./ssl:/etc/nginx/ssl:ro
      - ./nginx-ssl.conf:/etc/nginx/conf.d/default.conf:ro
```

### 2. 添加数据库服务

```yaml
services:
  postgres:
    image: postgres:15-alpine
    container_name: agent-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: agent_db
      POSTGRES_USER: agent_user
      POSTGRES_PASSWORD: your_secure_password
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - agent-network

volumes:
  postgres-data:
```

### 3. 资源限制

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### 4. 日志管理

```yaml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 5. 监控和健康检查

```bash
# 安装 Docker 监控工具
docker run -d \
  --name=cadvisor \
  --volume=/:/rootfs:ro \
  --volume=/var/run:/var/run:ro \
  --volume=/sys:/sys:ro \
  --volume=/var/lib/docker/:/var/lib/docker:ro \
  --publish=8080:8080 \
  google/cadvisor:latest
```

### 6. 自动重启策略

```yaml
services:
  backend:
    restart: always  # 总是重启
    # 或
    restart: on-failure:3  # 失败时重启，最多3次
```

### 7. 使用 Docker Secrets（敏感信息）

```bash
# 创建 secret
echo "your_api_key" | docker secret create openai_api_key -

# 在 docker-compose.yml 中使用
services:
  backend:
    secrets:
      - openai_api_key

secrets:
  openai_api_key:
    external: true
```

---

## 镜像管理

### 构建并推送到私有仓库

```bash
# 登录 Docker Hub 或私有仓库
docker login registry.example.com

# 构建镜像
docker-compose build

# 打标签
docker tag agent-backend:latest registry.example.com/agent-backend:v1.0.0
docker tag agent-frontend:latest registry.example.com/agent-frontend:v1.0.0

# 推送镜像
docker push registry.example.com/agent-backend:v1.0.0
docker push registry.example.com/agent-frontend:v1.0.0
```

### 使用镜像部署

修改 `docker-compose.yml`:
```yaml
services:
  backend:
    image: registry.example.com/agent-backend:v1.0.0
    # 注释掉 build 部分
```

---

## 性能优化建议

1. **启用 Gzip 压缩** - 已在 Nginx 配置中启用
2. **静态资源缓存** - 已配置 1 年缓存
3. **使用 CDN** - 将静态资源上传到 CDN
4. **数据库优化** - 生产环境使用 PostgreSQL
5. **后端多进程** - 已配置 4 个 worker
6. **容器资源限制** - 防止资源耗尽

---

## 安全建议

1. ✅ 使用环境变量管理敏感信息
2. ✅ 启用 HTTPS（生产环境必须）
3. ✅ 定期更新 Docker 镜像
4. ✅ 限制容器权限（不使用 root）
5. ✅ 配置防火墙规则
6. ✅ 定期备份数据
7. ✅ 监控日志和异常

---

## 支持与反馈

如有问题，请查看：
- 项目文档: `README.md`
- 后端 API 文档: http://localhost:8000/docs
- 日志文件: `backend/logs/`

---

**祝您部署顺利！** 🚀
