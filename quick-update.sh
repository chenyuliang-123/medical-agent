#!/bin/bash

# 快速更新脚本 - 只重启服务，不重新构建

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "=========================================="
echo "  快速更新部署"
echo "=========================================="

# 停止服务
echo -e "${GREEN}停止服务...${NC}"
docker-compose -f docker-compose.cn.yml down

# 启动服务
echo -e "${GREEN}启动服务...${NC}"
docker-compose -f docker-compose.cn.yml up -d

# 等待服务启动
echo -e "${GREEN}等待服务启动...${NC}"
sleep 10

# 检查服务状态
echo -e "${GREEN}检查服务状态...${NC}"
docker-compose -f docker-compose.cn.yml ps

# 检查后端健康状态
echo -e "${GREEN}检查后端健康状态...${NC}"
for i in {1..30}; do
    if curl -f http://localhost:9880/health &> /dev/null; then
        echo -e "${GREEN}✓ 后端服务启动成功${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}✗ 后端服务启动失败${NC}"
        echo "查看日志: docker-compose -f docker-compose.cn.yml logs backend"
        exit 1
    fi
    sleep 2
done

# 检查前端健康状态
echo -e "${GREEN}检查前端健康状态...${NC}"
if curl -f http://localhost:19880/ &> /dev/null; then
    echo -e "${GREEN}✓ 前端服务启动成功${NC}"
else
    echo -e "${RED}✗ 前端服务启动失败${NC}"
    echo "查看日志: docker-compose -f docker-compose.cn.yml logs frontend"
    exit 1
fi

echo ""
echo "=========================================="
echo -e "${GREEN}更新完成！${NC}"
echo "=========================================="
echo ""
echo "访问地址:"
echo "  前端: http://localhost:19880"
echo "  后端 API: http://localhost:9880"
echo "  API 文档: http://localhost:9880/docs"
echo ""
echo "远程访问（替换为服务器IP）:"
echo "  前端: http://服务器IP:19880"
echo "  后端 API: http://服务器IP:9880"
echo ""
echo "常用命令:"
echo "  查看日志: docker-compose -f docker-compose.cn.yml logs -f"
echo "  重启服务: docker-compose -f docker-compose.cn.yml restart"
echo ""
