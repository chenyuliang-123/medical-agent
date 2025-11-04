#!/bin/bash

set -e

echo "=========================================="
echo "  CentOS 7 Docker 完整安装脚本"
echo "=========================================="

# 备份原有 repo
echo "备份原有镜像源配置..."
sudo mkdir -p /etc/yum.repos.d/backup
sudo mv /etc/yum.repos.d/*.repo /etc/yum.repos.d/backup/ 2>/dev/null || true

# 配置阿里云镜像源
echo "配置阿里云镜像源..."
sudo tee /etc/yum.repos.d/CentOS-Base.repo <<-'EOF'
[base]
name=CentOS-7 - Base
baseurl=https://mirrors.aliyun.com/centos/7/os/$basearch/
gpgcheck=1
gpgkey=https://mirrors.aliyun.com/centos/RPM-GPG-KEY-CentOS-7

[updates]
name=CentOS-7 - Updates
baseurl=https://mirrors.aliyun.com/centos/7/updates/$basearch/
gpgcheck=1
gpgkey=https://mirrors.aliyun.com/centos/RPM-GPG-KEY-CentOS-7

[extras]
name=CentOS-7 - Extras
baseurl=https://mirrors.aliyun.com/centos/7/extras/$basearch/
gpgcheck=1
gpgkey=https://mirrors.aliyun.com/centos/RPM-GPG-KEY-CentOS-7
EOF

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
sudo curl -L "https://get.daocloud.io/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
sudo ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose

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
echo "请执行以下命令刷新用户组："
echo "  newgrp docker"
echo ""
echo "测试 Docker："
echo "  docker run hello-world"
echo ""