#!/bin/bash

# 慢病管理AI智能体 - Docker 部署脚本

set -e

echo "=========================================="
echo "  慢病管理AI智能体 - Docker 部署"
echo "=========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: Docker 未安装${NC}"
    echo "请先安装 Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# 检查 Docker Compose 是否安装
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}错误: Docker Compose 未安装${NC}"
    echo "请先安装 Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# 检查 .env 文件
if [ ! -f .env ]; then
    echo -e "${YELLOW}警告: .env 文件不存在${NC}"
    echo "正在从 .env.example 创建 .env 文件..."
    cp .env.example .env
    echo -e "${YELLOW}请编辑 .env 文件，配置必要的环境变量（特别是 OPENAI_API_KEY）${NC}"
    read -p "按回车键继续..."
fi

# 创建必要的目录
echo -e "${GREEN}创建必要的目录...${NC}"
mkdir -p backend/data backend/logs backend/uploads

# 停止并删除旧容器
echo -e "${GREEN}停止旧容器...${NC}"
docker-compose down 2>/dev/null || true

# 构建镜像
echo -e "${GREEN}构建 Docker 镜像...${NC}"
docker-compose build --no-cache

# 启动服务
echo -e "${GREEN}启动服务...${NC}"
docker-compose up -d

# 等待服务启动
echo -e "${GREEN}等待服务启动...${NC}"
sleep 10

# 检查服务状态
echo -e "${GREEN}检查服务状态...${NC}"
docker-compose ps

# 检查后端健康状态
echo -e "${GREEN}检查后端健康状态...${NC}"
for i in {1..30}; do
    if curl -f http://localhost:8000/health &> /dev/null; then
        echo -e "${GREEN}✓ 后端服务启动成功${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}✗ 后端服务启动失败${NC}"
        echo "查看日志: docker-compose logs backend"
        exit 1
    fi
    sleep 2
done

# 检查前端健康状态
echo -e "${GREEN}检查前端健康状态...${NC}"
if curl -f http://localhost/ &> /dev/null; then
    echo -e "${GREEN}✓ 前端服务启动成功${NC}"
else
    echo -e "${RED}✗ 前端服务启动失败${NC}"
    echo "查看日志: docker-compose logs frontend"
    exit 1
fi

echo ""
echo "=========================================="
echo -e "${GREEN}部署完成！${NC}"
echo "=========================================="
echo ""
echo "访问地址:"
echo "  前端: http://localhost"
echo "  后端 API: http://localhost:8000"
echo "  API 文档: http://localhost:8000/docs"
echo ""
echo "常用命令:"
echo "  查看日志: docker-compose logs -f"
echo "  停止服务: docker-compose down"
echo "  重启服务: docker-compose restart"
echo "  查看状态: docker-compose ps"
echo ""
