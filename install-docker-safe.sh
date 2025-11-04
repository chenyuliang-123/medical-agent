#!/bin/bash

set -e

echo "=========================================="
echo "  CentOS 7 Docker 安全安装脚本"
echo "=========================================="

# 检查是否已有备份
if [ -d "/etc/yum.repos.d/backup" ]; then
    echo "检测到已有备份目录，跳过备份步骤"
else
    # 备份原有 repo（仅备份，不删除）
    echo "备份原有镜像源配置..."
    sudo mkdir -p /etc/yum.repos.d/backup
    sudo cp /etc/yum.repos.d/*.repo /etc/yum.repos.d/backup/ 2>/dev/null || true
    echo "原有配置已备份到: /etc/yum.repos.d/backup/"
fi

# 检查原有镜像源是否可用
echo "检查原有镜像源状态..."
if sudo yum repolist 2>/dev/null | grep -q "repolist: 0"; then
    echo "原有镜像源不可用，需要更换"
    NEED_REPLACE=true
else
    echo "原有镜像源可用"
    NEED_REPLACE=false
fi

# 只在需要时才替换镜像源
if [ "$NEED_REPLACE" = true ]; then
    echo "配置阿里云镜像源..."
    sudo tee /etc/yum.repos.d/CentOS-Base-Aliyun.repo <<-'EOF'
[base-aliyun]
name=CentOS-7 - Base - Aliyun
baseurl=https://mirrors.aliyun.com/centos/7/os/$basearch/
gpgcheck=1
gpgkey=https://mirrors.aliyun.com/centos/RPM-GPG-KEY-CentOS-7
priority=1

[updates-aliyun]
name=CentOS-7 - Updates - Aliyun
baseurl=https://mirrors.aliyun.com/centos/7/updates/$basearch/
gpgcheck=1
gpgkey=https://mirrors.aliyun.com/centos/RPM-GPG-KEY-CentOS-7
priority=1

[extras-aliyun]
name=CentOS-7 - Extras - Aliyun
baseurl=https://mirrors.aliyun.com/centos/7/extras/$basearch/
gpgcheck=1
gpgkey=https://mirrors.aliyun.com/centos/RPM-GPG-KEY-CentOS-7
priority=1
EOF
    
    # 禁用原有的失效源（不删除）
    echo "禁用失效的原有镜像源..."
    sudo sed -i 's/enabled=1/enabled=0/g' /etc/yum.repos.d/CentOS-*.repo 2>/dev/null || true
    sudo sed -i 's/enabled=1/enabled=0/g' /etc/yum.repos.d/*-sclo*.repo 2>/dev/null || true
else
    echo "保留原有镜像源配置"
fi

# 清理缓存
echo "清理并重建 yum 缓存..."
sudo yum clean all
sudo yum makecache fast

# 安装依赖
echo "安装依赖包..."
sudo yum install -y yum-utils device-mapper-persistent-data lvm2

# 添加 Docker 仓库
echo "添加 Docker 仓库..."
sudo yum-config-manager --add-repo https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo

# 安装 Docker
echo "安装 Docker..."
sudo yum install -y docker-ce docker-ce-cli containerd.io

# 启动 Docker
echo "启动 Docker 服务..."
sudo systemctl start docker
sudo systemctl enable docker

# 配置镜像加速
echo "配置 Docker 镜像加速..."
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com"
  ]
}
EOF

sudo systemctl daemon-reload
sudo systemctl restart docker

# 安装 Docker Compose
echo "安装 Docker Compose..."

# 尝试多个下载源
COMPOSE_VERSION="v2.23.0"
COMPOSE_FILE="/usr/local/bin/docker-compose"

# 下载源列表（按优先级）
DOWNLOAD_URLS=(
    "https://ghproxy.com/https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)"
    "https://download.fastgit.org/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)"
    "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)"
    "https://get.daocloud.io/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)"
)

# 尝试下载
DOWNLOAD_SUCCESS=false
for url in "${DOWNLOAD_URLS[@]}"; do
    echo "尝试从 $url 下载..."
    if sudo curl -L --connect-timeout 10 --max-time 300 "$url" -o "$COMPOSE_FILE" 2>/dev/null; then
        if [ -f "$COMPOSE_FILE" ] && [ -s "$COMPOSE_FILE" ]; then
            echo "下载成功！"
            DOWNLOAD_SUCCESS=true
            break
        fi
    fi
    echo "下载失败，尝试下一个源..."
done

# 如果所有源都失败，尝试使用 pip 安装
if [ "$DOWNLOAD_SUCCESS" = false ]; then
    echo "所有下载源失败，尝试使用 pip 安装..."
    sudo yum install -y python3-pip
    sudo pip3 install docker-compose -i https://mirrors.aliyun.com/pypi/simple/
else
    sudo chmod +x /usr/local/bin/docker-compose
    sudo ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
fi

# 添加用户权限
echo "配置用户权限..."
sudo usermod -aG docker $USER

echo ""
echo "=========================================="
echo "  安装完成！"
echo "=========================================="
echo ""
echo "Docker 版本："
docker --version
echo ""
echo "Docker Compose 版本："
docker-compose --version
echo ""
echo "原有镜像源配置已备份到: /etc/yum.repos.d/backup/"
echo ""
echo "请执行以下命令刷新用户组："
echo "  newgrp docker"
echo ""
echo "测试 Docker："
echo "  docker run hello-world"
echo ""
