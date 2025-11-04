# MySQL 数据库部署说明

## 概述

项目已从 SQLite 切换到 MySQL 数据库，提供更好的性能和并发支持。

## 修改内容

### 1. 新增 MySQL 服务

在 `docker-compose.cn.yml` 中添加了 MySQL 8.0 容器：
- **容器名**: agent-mysql
- **端口**: 3306
- **数据持久化**: mysql-data volume

### 2. 更新依赖

在 `requirements.txt` 中添加：
- `pymysql==1.1.0` - MySQL 驱动
- `cryptography==41.0.7` - 加密支持

### 3. 数据库配置

默认配置（可在 `.env` 文件中修改）：
```env
MYSQL_ROOT_PASSWORD=root123456
MYSQL_DATABASE=agent_db
MYSQL_USER=agent_user
MYSQL_PASSWORD=agent_pass123
```

## 部署步骤

### 1. 更新服务器文件

上传以下修改的文件到服务器：
- `docker-compose.cn.yml`
- `backend/requirements.txt`
- `backend/app/database/base.py`
- `backend/init.sql`
- `.env.example`

### 2. 更新 .env 配置

```bash
cd /opt/ai_slow_hj/agent

# 备份现有配置
cp .env .env.backup

# 添加 MySQL 配置
cat >> .env <<'EOF'

# MySQL 数据库配置
MYSQL_ROOT_PASSWORD=root123456
MYSQL_DATABASE=agent_db
MYSQL_USER=agent_user
MYSQL_PASSWORD=agent_pass123
DATABASE_URL=mysql+pymysql://agent_user:agent_pass123@mysql:3306/agent_db?charset=utf8mb4
EOF
```

### 3. 重新部署

```bash
# 停止现有服务
docker-compose -f docker-compose.cn.yml down

# 重新构建后端（安装 MySQL 驱动）
docker-compose -f docker-compose.cn.yml build backend

# 启动所有服务（包括 MySQL）
docker-compose -f docker-compose.cn.yml up -d

# 查看日志
docker-compose -f docker-compose.cn.yml logs -f
```

## 数据迁移（可选）

如果需要从 SQLite 迁移现有数据到 MySQL：

### 方法 1: 使用脚本迁移

```bash
# 创建迁移脚本
cat > migrate_to_mysql.py <<'EOF'
import sqlite3
import pymysql
import os

# SQLite 连接
sqlite_conn = sqlite3.connect('./backend/data/agent.db')
sqlite_cursor = sqlite_conn.cursor()

# MySQL 连接
mysql_conn = pymysql.connect(
    host='localhost',
    port=3306,
    user='agent_user',
    password='agent_pass123',
    database='agent_db',
    charset='utf8mb4'
)
mysql_cursor = mysql_conn.cursor()

# 获取所有表
sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = sqlite_cursor.fetchall()

for table in tables:
    table_name = table[0]
    if table_name == 'sqlite_sequence':
        continue
    
    print(f"迁移表: {table_name}")
    
    # 读取 SQLite 数据
    sqlite_cursor.execute(f"SELECT * FROM {table_name}")
    rows = sqlite_cursor.fetchall()
    
    if rows:
        # 获取列数
        placeholders = ','.join(['%s'] * len(rows[0]))
        
        # 插入到 MySQL
        for row in rows:
            try:
                mysql_cursor.execute(
                    f"INSERT INTO {table_name} VALUES ({placeholders})",
                    row
                )
            except Exception as e:
                print(f"错误: {e}")
                continue

mysql_conn.commit()
sqlite_conn.close()
mysql_conn.close()

print("迁移完成！")
EOF

# 执行迁移
python migrate_to_mysql.py
```

### 方法 2: 手动导出导入

```bash
# 1. 导出 SQLite 数据为 SQL
sqlite3 ./backend/data/agent.db .dump > sqlite_dump.sql

# 2. 转换并导入到 MySQL
# 需要手动编辑 sqlite_dump.sql，调整语法差异

# 3. 导入到 MySQL
docker exec -i agent-mysql mysql -uagent_user -pagent_pass123 agent_db < sqlite_dump.sql
```

## 访问 MySQL 数据库

### 方法 1: 使用 MySQL 客户端工具

推荐工具：
- **MySQL Workbench** (官方，免费)
- **DBeaver** (跨平台，免费)
- **Navicat** (商业软件)
- **phpMyAdmin** (Web界面)

连接信息：
```
主机: 服务器IP
端口: 3306
用户名: agent_user
密码: agent_pass123
数据库: agent_db
```

### 方法 2: 命令行访问

```bash
# 从容器内访问
docker exec -it agent-mysql mysql -uagent_user -pagent_pass123 agent_db

# 从宿主机访问（需要安装 MySQL 客户端）
mysql -h localhost -P 3306 -uagent_user -pagent_pass123 agent_db
```

### 方法 3: 使用 Docker 命令

```bash
# 进入 MySQL 容器
docker exec -it agent-mysql bash

# 在容器内连接数据库
mysql -uroot -proot123456

# 切换数据库
USE agent_db;

# 查看表
SHOW TABLES;

# 查询数据
SELECT * FROM users;
```

## 数据库管理

### 备份数据库

```bash
# 备份到文件
docker exec agent-mysql mysqldump -uroot -proot123456 agent_db > backup_$(date +%Y%m%d_%H%M%S).sql

# 或使用脚本
cat > backup_mysql.sh <<'EOF'
#!/bin/bash
BACKUP_DIR="./backups/mysql"
mkdir -p $BACKUP_DIR
BACKUP_FILE="$BACKUP_DIR/agent_db_$(date +%Y%m%d_%H%M%S).sql"
docker exec agent-mysql mysqldump -uroot -proot123456 agent_db > $BACKUP_FILE
echo "备份完成: $BACKUP_FILE"
EOF

chmod +x backup_mysql.sh
./backup_mysql.sh
```

### 恢复数据库

```bash
# 从备份文件恢复
docker exec -i agent-mysql mysql -uroot -proot123456 agent_db < backup_file.sql
```

### 查看数据库状态

```bash
# 查看容器状态
docker-compose -f docker-compose.cn.yml ps

# 查看 MySQL 日志
docker-compose -f docker-compose.cn.yml logs mysql

# 查看数据库大小
docker exec agent-mysql mysql -uroot -proot123456 -e "
SELECT 
    table_schema AS 'Database',
    ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)'
FROM information_schema.tables
WHERE table_schema = 'agent_db'
GROUP BY table_schema;
"
```

## 性能优化

### MySQL 配置优化

如需自定义 MySQL 配置，创建 `my.cnf`：

```bash
cat > backend/my.cnf <<'EOF'
[mysqld]
# 字符集
character-set-server=utf8mb4
collation-server=utf8mb4_unicode_ci

# 性能优化
max_connections=200
innodb_buffer_pool_size=256M
innodb_log_file_size=64M
innodb_flush_log_at_trx_commit=2

# 查询缓存
query_cache_type=1
query_cache_size=32M
EOF
```

然后在 `docker-compose.cn.yml` 中挂载：
```yaml
volumes:
  - ./backend/my.cnf:/etc/mysql/conf.d/custom.cnf:ro
```

## 故障排查

### 1. 连接失败

```bash
# 检查 MySQL 容器状态
docker ps | grep mysql

# 查看 MySQL 日志
docker logs agent-mysql

# 测试连接
docker exec agent-mysql mysqladmin ping -h localhost
```

### 2. 权限问题

```bash
# 进入 MySQL 容器
docker exec -it agent-mysql mysql -uroot -proot123456

# 检查用户权限
SHOW GRANTS FOR 'agent_user'@'%';

# 重新授权
GRANT ALL PRIVILEGES ON agent_db.* TO 'agent_user'@'%';
FLUSH PRIVILEGES;
```

### 3. 数据库初始化失败

```bash
# 查看初始化日志
docker logs agent-mysql | grep -i error

# 手动初始化
docker exec -it agent-mysql mysql -uroot -proot123456 < backend/init.sql
```

## 安全建议

1. **修改默认密码**：在生产环境中，请修改 `.env` 中的默认密码
2. **限制远程访问**：如不需要外部访问，可移除端口映射 `3306:3306`
3. **定期备份**：设置定时任务自动备份数据库
4. **监控日志**：定期检查 MySQL 日志，发现异常及时处理

## 回滚到 SQLite

如果需要回滚到 SQLite：

```bash
# 1. 修改 .env
DATABASE_URL=sqlite:///./data/agent.db

# 2. 停止 MySQL
docker-compose -f docker-compose.cn.yml stop mysql

# 3. 重启后端
docker-compose -f docker-compose.cn.yml restart backend
```

---

**MySQL 数据库配置完成！** 🎉
