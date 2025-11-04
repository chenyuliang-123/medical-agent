# 🐧 慢病管理AI智能体 - Linux部署指南

## 📋 目录

- [系统要求](#系统要求)
- [部署前准备](#部署前准备)
- [后端部署](#后端部署)
- [前端部署](#前端部署)
- [Nginx配置](#nginx配置)
- [进程管理](#进程管理)
- [数据库备份](#数据库备份)
- [常见问题](#常见问题)

---

## 系统要求

### 操作系统
- Ubuntu 20.04 LTS / 22.04 LTS（推荐）
- CentOS 7+ / Rocky Linux 8+
- Debian 10+

### 硬件配置
- CPU: 2核心以上
- 内存: 4GB以上（推荐8GB）
- 磁盘: 20GB以上可用空间

### 软件依赖
- Python 3.9+
- Nginx（推荐，用于生产环境）
- Supervisor（推荐，用于进程管理）
- Node.js 16+ / npm 8+（**仅在服务器上构建前端时需要，如果本地已打包好 dist 则不需要**）

---

## 部署前准备

### 1. 更新系统

```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS/Rocky Linux
sudo yum update -y
```

### 2. 安装基础工具

```bash
# Ubuntu/Debian
sudo apt install -y git curl wget vim build-essential

# CentOS/Rocky Linux
sudo yum install -y git curl wget vim gcc gcc-c++ make
```

### 3. 安装Python 3.9+

```bash
# Ubuntu/Debian
sudo apt install -y python3 python3-pip python3-venv

# CentOS/Rocky Linux（可能需要EPEL源）
sudo yum install -y python39 python39-pip

# 验证Python版本
python3 --version
```

### 4. 安装Node.js和npm（可选）

> **注意：如果你已经在本地 Windows 打包好了 `dist` 目录，可以跳过此步骤！**
> 
> 只有在以下情况才需要安装 Node.js：
> - 需要在服务器上执行 `npm run build` 构建前端
> - 需要在服务器上修改前端代码

```bash
# 使用NodeSource仓库安装Node.js 18.x
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# 或使用nvm安装（推荐）
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 18
nvm use 18

# 验证安装
node --version
npm --version
```

### 5. 创建部署目录和用户（可选）

```bash
# 创建专用用户（推荐）
sudo useradd -m -s /bin/bash agent
sudo passwd agent

# 切换到agent用户
su - agent

# 创建部署目录
mkdir -p ~/apps
cd ~/apps
```

---

## 后端部署

### 1. 上传项目文件

```bash
# 方式1: 使用git克隆（如果有仓库）
cd ~/apps
git clone <your-repository-url> agent
cd agent

# 方式2: 使用scp上传（从本地Windows上传）
# 在Windows PowerShell中执行:
# scp -r d:\users\kevin\fusiontech\project\agent user@your-server-ip:~/apps/

# 方式3: 使用FTP工具（如FileZilla）上传整个项目目录
```

### 2. 配置后端环境

```bash
# 进入后端目录
cd ~/apps/agent/backend

# 创建Python虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 升级pip
pip install --upgrade pip

# 安装依赖（使用国内镜像加速）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 3. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量
vim .env
```

**编辑 `.env` 文件，填入以下配置：**

```env
# OpenAI配置
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_BASE_URL=https://api.openai.com/v1

# 或使用智谱AI（国内推荐）
# OPENAI_API_KEY=your-zhipu-api-key
# OPENAI_MODEL=glm-4
# OPENAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4/

# 数据库配置
DATABASE_URL=sqlite:///./chronic_disease.db

# 应用配置
APP_ENV=production
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=False

# 跨域配置（根据实际域名修改）
CORS_ORIGINS=["http://your-domain.com", "https://your-domain.com"]

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=/var/log/agent/app.log

# 知识库配置
KNOWLEDGE_BASE_PATH=../knowledge/chronic_disease.json
```

**保存并退出（vim操作：按 `i` 进入编辑模式，编辑完成后按 `ESC`，输入 `:wq` 保存退出）**

### 4. 初始化数据库

```bash
# 确保在虚拟环境中
source venv/bin/activate

# 运行数据库初始化脚本
python init_db.py
```

**预期输出：**
```
✅ 数据库初始化成功！
✅ 创建了1个测试用户
✅ 创建了21条血糖数据
✅ 创建了14条血压数据
...
```

### 5. 测试后端启动

```bash
# 测试启动（前台运行）
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# 如果成功，你会看到：
# INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**在浏览器访问测试：** `http://your-server-ip:8000/docs`

如果能看到API文档页面，说明后端部署成功！按 `Ctrl+C` 停止测试。

---

## 前端部署

前端部署有两种方式，根据你的情况选择：

### 方式1：直接上传已打包的 dist 目录（推荐）

> **适用场景：** 在本地 Windows 已经打包好，直接上传到服务器
> 
> **优点：** 服务器不需要安装 Node.js，部署更快更简单

#### 1. 在本地 Windows 打包

```powershell
# 在本地 Windows PowerShell 中执行
cd d:\users\kevin\fusiontech\project\agent\frontend

# 修改API地址为服务器地址（编辑 src/api/index.ts）
# 将 localhost 改为: http://your-server-ip:8000

# 构建生产版本
npm run build
```

#### 2. 上传 dist 目录到服务器

```powershell
# 使用 scp 上传（在 Windows PowerShell 中执行）
scp -r dist user@your-server-ip:/home/agent/apps/agent/frontend/

# 或使用 FTP 工具（如 FileZilla）上传 dist 目录
```

#### 3. 在服务器上验证

```bash
# 登录服务器后检查
ls -lh ~/apps/agent/frontend/dist/
```

**完成！** 直接跳到 [Nginx配置](#nginx配置) 部分。

---

### 方式2：在服务器上构建（需要 Node.js）

> **适用场景：** 需要在服务器上修改代码或重新构建
> 
> **前提：** 服务器已安装 Node.js（参考前面的安装步骤）

#### 1. 安装依赖

```bash
# 进入前端目录
cd ~/apps/agent/frontend

# 安装依赖（使用国内镜像加速）
npm install --registry=https://registry.npmmirror.com
```

#### 2. 配置API地址

```bash
# 编辑API配置文件
vim src/api/index.ts
```

**修改API基础URL：**

```typescript
// 将 localhost 改为服务器IP或域名
const BASE_URL = 'http://your-server-ip:8000';
// 或使用域名
// const BASE_URL = 'https://api.your-domain.com';
```

#### 3. 构建生产版本

```bash
# 构建前端
npm run build

# 构建完成后，会生成 dist 目录
ls -lh dist/
```

#### 4. 测试前端（可选）

```bash
# 使用vite预览构建结果
npm run preview -- --host 0.0.0.0 --port 5173

# 访问 http://your-server-ip:5173 测试
```

---

## Nginx配置

### 1. 安装Nginx

```bash
# Ubuntu/Debian
sudo apt install -y nginx

# CentOS/Rocky Linux
sudo yum install -y nginx

# 启动Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# 检查状态
sudo systemctl status nginx
```

### 2. 配置Nginx站点

```bash
# 创建配置文件
sudo vim /etc/nginx/sites-available/agent
```

**Nginx配置内容：**

```nginx
# 后端API服务
upstream backend_api {
    server 127.0.0.1:8000;
}

# HTTP服务器配置
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;  # 修改为你的域名或IP

    # 日志配置
    access_log /var/log/nginx/agent_access.log;
    error_log /var/log/nginx/agent_error.log;

    # 前端静态文件
    location / {
        root /home/agent/apps/agent/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
        
        # 静态资源缓存
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # 后端API代理
    location /api/ {
        proxy_pass http://backend_api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # API文档（生产环境可以注释掉）
    location /docs {
        proxy_pass http://backend_api/docs;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /openapi.json {
        proxy_pass http://backend_api/openapi.json;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 安全配置
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # 文件上传大小限制
    client_max_body_size 10M;
}
```

### 3. 启用站点配置

```bash
# Ubuntu/Debian（使用软链接）
sudo ln -s /etc/nginx/sites-available/agent /etc/nginx/sites-enabled/

# CentOS/Rocky Linux（直接编辑主配置）
# sudo vim /etc/nginx/nginx.conf
# 在 http 块中添加: include /etc/nginx/conf.d/*.conf;
# 然后将配置保存到: sudo vim /etc/nginx/conf.d/agent.conf

# 测试配置
sudo nginx -t

# 重载Nginx
sudo systemctl reload nginx
```

### 4. 配置防火墙

```bash
# Ubuntu/Debian (UFW)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp  # 如果需要直接访问后端
sudo ufw enable
sudo ufw status

# CentOS/Rocky Linux (firewalld)
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
sudo firewall-cmd --list-all
```

---

## 进程管理

### 方式1: 使用Supervisor（推荐）

#### 1. 安装Supervisor

```bash
# Ubuntu/Debian
sudo apt install -y supervisor

# CentOS/Rocky Linux
sudo yum install -y supervisor

# 启动Supervisor
sudo systemctl start supervisor
sudo systemctl enable supervisor
```

#### 2. 配置后端进程

```bash
# 创建配置文件
sudo vim /etc/supervisor/conf.d/agent-backend.conf
```

**Supervisor配置内容：**

```ini
[program:agent-backend]
command=/home/agent/apps/agent/backend/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
directory=/home/agent/apps/agent/backend
user=agent
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/supervisor/agent-backend.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=10
environment=PATH="/home/agent/apps/agent/backend/venv/bin"
```

#### 3. 重载并启动

```bash
# 重载Supervisor配置
sudo supervisorctl reread
sudo supervisorctl update

# 启动服务
sudo supervisorctl start agent-backend

# 查看状态
sudo supervisorctl status

# 其他常用命令
sudo supervisorctl stop agent-backend    # 停止
sudo supervisorctl restart agent-backend # 重启
sudo supervisorctl tail -f agent-backend # 查看日志
```

### 方式2: 使用systemd

#### 1. 创建systemd服务

```bash
sudo vim /etc/systemd/system/agent-backend.service
```

**systemd服务配置：**

```ini
[Unit]
Description=Chronic Disease AI Agent Backend
After=network.target

[Service]
Type=simple
User=agent
Group=agent
WorkingDirectory=/home/agent/apps/agent/backend
Environment="PATH=/home/agent/apps/agent/backend/venv/bin"
ExecStart=/home/agent/apps/agent/backend/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 2. 启动服务

```bash
# 重载systemd配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start agent-backend

# 设置开机自启
sudo systemctl enable agent-backend

# 查看状态
sudo systemctl status agent-backend

# 查看日志
sudo journalctl -u agent-backend -f
```

---

## 数据库备份

### 1. 创建备份脚本

```bash
# 创建备份目录
mkdir -p ~/backups

# 创建备份脚本
vim ~/backup-db.sh
```

**备份脚本内容：**

```bash
#!/bin/bash

# 配置
DB_PATH="/home/agent/apps/agent/backend/chronic_disease.db"
BACKUP_DIR="/home/agent/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/chronic_disease_$DATE.db"

# 创建备份
cp "$DB_PATH" "$BACKUP_FILE"

# 压缩备份
gzip "$BACKUP_FILE"

# 删除7天前的备份
find "$BACKUP_DIR" -name "chronic_disease_*.db.gz" -mtime +7 -delete

echo "数据库备份完成: $BACKUP_FILE.gz"
```

```bash
# 添加执行权限
chmod +x ~/backup-db.sh

# 测试备份
~/backup-db.sh
```

### 2. 设置定时备份

```bash
# 编辑crontab
crontab -e

# 添加以下行（每天凌晨2点备份）
0 2 * * * /home/agent/backup-db.sh >> /home/agent/backup.log 2>&1
```

### 3. 恢复数据库

```bash
# 停止后端服务
sudo supervisorctl stop agent-backend
# 或
sudo systemctl stop agent-backend

# 解压备份文件
gunzip /home/agent/backups/chronic_disease_20240101_020000.db.gz

# 恢复数据库
cp /home/agent/backups/chronic_disease_20240101_020000.db /home/agent/apps/agent/backend/chronic_disease.db

# 启动后端服务
sudo supervisorctl start agent-backend
# 或
sudo systemctl start agent-backend
```

---

## 日志管理

### 1. 配置日志目录

```bash
# 创建日志目录
sudo mkdir -p /var/log/agent
sudo chown agent:agent /var/log/agent
```

### 2. 配置日志轮转

```bash
# 创建logrotate配置
sudo vim /etc/logrotate.d/agent
```

**logrotate配置内容：**

```
/var/log/agent/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 agent agent
    sharedscripts
    postrotate
        supervisorctl restart agent-backend > /dev/null 2>&1 || true
    endscript
}
```

### 3. 查看日志

```bash
# 实时查看后端日志
tail -f /var/log/supervisor/agent-backend.log

# 查看Nginx访问日志
sudo tail -f /var/log/nginx/agent_access.log

# 查看Nginx错误日志
sudo tail -f /var/log/nginx/agent_error.log

# 查看系统日志
sudo journalctl -u agent-backend -f
```

---

## 性能优化

### 1. 后端优化

```bash
# 编辑后端配置，增加worker数量
# workers数量 = CPU核心数 * 2 + 1

# 在supervisor配置中修改:
# command=... --workers 4

# 或在systemd配置中修改:
# ExecStart=... --workers 4
```

### 2. Nginx优化

```bash
# 编辑Nginx配置
sudo vim /etc/nginx/nginx.conf
```

**添加性能优化配置：**

```nginx
# 在 http 块中添加
worker_processes auto;
worker_connections 2048;

# 启用gzip压缩
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json;

# 缓存配置
open_file_cache max=1000 inactive=20s;
open_file_cache_valid 30s;
open_file_cache_min_uses 2;
```

### 3. 系统优化

```bash
# 增加文件描述符限制
sudo vim /etc/security/limits.conf

# 添加以下行
* soft nofile 65535
* hard nofile 65535
```

---

## 监控和维护

### 1. 系统监控

```bash
# 安装htop（系统资源监控）
sudo apt install -y htop

# 运行htop
htop

# 查看磁盘使用
df -h

# 查看内存使用
free -h

# 查看进程
ps aux | grep uvicorn
```

### 2. 应用健康检查

```bash
# 创建健康检查脚本
vim ~/health-check.sh
```

**健康检查脚本：**

```bash
#!/bin/bash

# 检查后端API
BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs)

if [ "$BACKEND_STATUS" -eq 200 ]; then
    echo "✅ 后端服务正常"
else
    echo "❌ 后端服务异常，状态码: $BACKEND_STATUS"
    # 可以添加重启逻辑或发送告警
fi

# 检查Nginx
NGINX_STATUS=$(systemctl is-active nginx)
if [ "$NGINX_STATUS" = "active" ]; then
    echo "✅ Nginx服务正常"
else
    echo "❌ Nginx服务异常"
fi
```

```bash
# 添加执行权限
chmod +x ~/health-check.sh

# 设置定时检查（每5分钟）
crontab -e
# 添加: */5 * * * * /home/agent/health-check.sh >> /home/agent/health-check.log 2>&1
```

---

## 常见问题

### Q1: 端口被占用

```bash
# 查看端口占用
sudo lsof -i :8000
sudo netstat -tulnp | grep 8000

# 杀死占用进程
sudo kill -9 <PID>
```

### Q2: 权限问题

```bash
# 修改项目目录权限
sudo chown -R agent:agent /home/agent/apps/agent

# 修改日志目录权限
sudo chown -R agent:agent /var/log/agent
```

### Q3: Python依赖安装失败

```bash
# 安装编译工具
sudo apt install -y python3-dev build-essential

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q4: 数据库锁定

```bash
# 检查数据库文件权限
ls -l chronic_disease.db

# 停止所有访问数据库的进程
sudo supervisorctl stop agent-backend

# 重启服务
sudo supervisorctl start agent-backend
```

### Q5: Nginx 502错误

```bash
# 检查后端服务是否运行
sudo supervisorctl status agent-backend

# 检查后端日志
sudo tail -f /var/log/supervisor/agent-backend.log

# 检查Nginx错误日志
sudo tail -f /var/log/nginx/agent_error.log

# 测试后端是否可访问
curl http://localhost:8000/docs
```

### Q6: 内存不足

```bash
# 查看内存使用
free -h

# 减少worker数量
# 在supervisor配置中: --workers 2

# 或添加swap空间
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## 安全加固

### 1. 配置HTTPS（使用Let's Encrypt）

```bash
# 安装certbot
sudo apt install -y certbot python3-certbot-nginx

# 获取SSL证书
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

### 2. 配置防火墙

```bash
# 只开放必要端口
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 3. 限制API访问

在Nginx配置中添加：

```nginx
# 限制请求频率
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

location /api/ {
    limit_req zone=api_limit burst=20 nodelay;
    # ... 其他配置
}
```

---

## 快速部署脚本

创建一键部署脚本（仅供参考，请根据实际情况修改）：

```bash
vim ~/deploy.sh
```

```bash
#!/bin/bash

set -e

echo "🚀 开始部署慢病管理AI智能体..."

# 1. 更新代码
cd ~/apps/agent
git pull

# 2. 更新后端依赖
cd backend
source venv/bin/activate
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 3. 更新前端
cd ../frontend
npm install --registry=https://registry.npmmirror.com
npm run build

# 4. 重启服务
sudo supervisorctl restart agent-backend
sudo systemctl reload nginx

echo "✅ 部署完成！"
```

```bash
chmod +x ~/deploy.sh
```

---

## 验证部署

### 1. 检查服务状态

```bash
# 检查后端
sudo supervisorctl status agent-backend

# 检查Nginx
sudo systemctl status nginx

# 检查端口监听
sudo netstat -tulnp | grep -E ':(80|443|8000)'
```

### 2. 访问测试

- **前端页面**: http://your-domain.com 或 http://your-server-ip
- **API文档**: http://your-domain.com/docs
- **健康检查**: http://your-domain.com/api/health

### 3. 功能测试

1. 打开前端页面
2. 点击"AI助手"
3. 输入测试消息："查询我最近的血糖数据"
4. 检查是否正常返回结果

---

## 总结

完成以上步骤后，你的慢病管理AI智能体应该已经成功部署到Linux服务器上了！

### 关键文件位置

- **项目目录**: `/home/agent/apps/agent`
- **后端配置**: `/home/agent/apps/agent/backend/.env`
- **数据库**: `/home/agent/apps/agent/backend/chronic_disease.db`
- **前端构建**: `/home/agent/apps/agent/frontend/dist`
- **Nginx配置**: `/etc/nginx/sites-available/agent`
- **Supervisor配置**: `/etc/supervisor/conf.d/agent-backend.conf`
- **日志目录**: `/var/log/agent/`

### 常用命令

```bash
# 重启后端
sudo supervisorctl restart agent-backend

# 重启Nginx
sudo systemctl reload nginx

# 查看后端日志
sudo tail -f /var/log/supervisor/agent-backend.log

# 查看Nginx日志
sudo tail -f /var/log/nginx/agent_access.log

# 备份数据库
~/backup-db.sh

# 健康检查
~/health-check.sh
```

---

## 🎉 部署完成！

如有问题，请查看日志文件或参考常见问题部分。

**祝部署顺利！** 🚀
