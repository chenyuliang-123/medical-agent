#!/bin/bash

# 重新构建脚本 - 只在依赖变化时使用

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "=========================================="
echo "  重新构建部署"
echo "=========================================="

# 停止服务
echo -e "${GREEN}停止服务...${NC}"
docker-compose -f docker-compose.cn.yml down

# 重新构建（使用缓存）
echo -e "${GREEN}重新构建镜像...${NC}"
docker-compose -f docker-compose.cn.yml build

# 启动服务
echo -e "${GREEN}启动服务...${NC}"
docker-compose -f docker-compose.cn.yml up -d

# 等待服务启动
echo -e "${GREEN}等待服务启动...${NC}"
sleep 10

# 检查服务状态
echo -e "${GREEN}检查服务状态...${NC}"
docker-compose -f docker-compose.cn.yml ps

# 查看日志
echo -e "${GREEN}查看启动日志...${NC}"
docker-compose -f docker-compose.cn.yml logs --tail=50

echo ""
echo "=========================================="
echo -e "${GREEN}构建完成！${NC}"
echo "=========================================="
