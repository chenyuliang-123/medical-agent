#!/bin/bash

echo "修复 Docker 镜像拉取问题..."

# 1. 备份原配置
sudo cp /etc/docker/daemon.json /etc/docker/daemon.json.bak 2>/dev/null || true

# 2. 配置新的镜像源和 DNS
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": [
    "https://dockerproxy.com",
    "https://docker.nju.edu.cn"
  ],
  "dns": ["223.5.5.5", "8.8.8.8", "114.114.114.114"],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF

# 3. 重启 Docker
echo "重启 Docker 服务..."
sudo systemctl daemon-reload
sudo systemctl restart docker

# 4. 等待服务启动
sleep 5

# 5. 验证配置
echo "验证 Docker 配置..."
docker info | grep -A 5 "Registry Mirrors"

# 6. 测试镜像拉取
echo "测试镜像拉取..."
docker pull hello-world

echo "配置完成！现在可以重新部署项目。"