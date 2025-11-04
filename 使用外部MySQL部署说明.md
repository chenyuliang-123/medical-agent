# 使用外部 MySQL 服务器部署说明

## 数据库信息

- **主机**: 10.10.31.112
- **端口**: 3306
- **数据库**: ai_slow
- **用户名**: root
- **密码**: mysql112
- **版本**: MySQL 5.7.31

## 部署步骤

### 1. 在 MySQL 服务器上准备数据库

连接到 MySQL 服务器并确保数据库存在：

```sql
-- 连接到 MySQL
mysql -h 10.10.31.112 -u root -pmysql112

-- 查看数据库是否存在
SHOW DATABASES LIKE 'ai_slow';

-- 如果不存在，创建数据库
CREATE DATABASE IF NOT EXISTS ai_slow 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE ai_slow;

-- 查看现有表
SHOW TABLES;
```

### 2. 更新服务器上的 .env 文件

```bash
cd /opt/ai_slow_hj/agent

# 编辑 .env 文件
vi .env

# 添加或修改以下内容：
DATABASE_URL=mysql+pymysql://root:mysql112@10.10.31.112:3306/ai_slow?charset=utf8mb4
```

或使用命令直接添加：

```bash
cd /opt/ai_slow_hj/agent

# 备份现有配置
cp .env .env.backup

# 更新数据库配置
cat >> .env <<'EOF'

# 外部 MySQL 数据库配置
DATABASE_URL=mysql+pymysql://root:mysql112@10.10.31.112:3306/ai_slow?charset=utf8mb4
EOF
```

### 3. 测试数据库连接

在部署前，先测试数据库连接是否正常：

```bash
# 方法1: 使用 Python 测试
python3 <<'EOF'
import pymysql

try:
    conn = pymysql.connect(
        host='10.10.31.112',
        port=3306,
        user='root',
        password='mysql112',
        database='ai_slow',
        charset='utf8mb4'
    )
    print("✓ 数据库连接成功！")
    conn.close()
except Exception as e:
    print(f"✗ 数据库连接失败: {e}")
EOF

# 方法2: 使用 MySQL 客户端测试
mysql -h 10.10.31.112 -P 3306 -u root -pmysql112 ai_slow -e "SELECT 1;"
```

### 4. 重新部署应用

```bash
cd /opt/ai_slow_hj/agent

# 停止现有服务
docker-compose -f docker-compose.cn.yml down

# 重新构建后端（确保安装了 pymysql）
docker-compose -f docker-compose.cn.yml build backend

# 启动服务
docker-compose -f docker-compose.cn.yml up -d

# 查看日志
docker-compose -f docker-compose.cn.yml logs -f backend
```

### 5. 验证部署

```bash
# 检查容器状态
docker-compose -f docker-compose.cn.yml ps

# 检查后端健康状态
curl http://localhost:9880/health

# 查看后端日志
docker-compose -f docker-compose.cn.yml logs backend --tail=50
```

## 数据库表初始化

应用启动时会自动创建所需的表。如果需要手动初始化：

```bash
# 进入后端容器
docker exec -it agent-backend bash

# 在容器内执行
python -c "from app.database.base import init_db; init_db()"

# 或者运行初始化脚本（如果有）
python init_db.py
```

## 访问数据库

### 使用 GUI 工具

推荐使用以下工具连接数据库：

1. **MySQL Workbench**
2. **DBeaver**
3. **Navicat**

连接信息：
```
主机: 10.10.31.112
端口: 3306
用户名: root
密码: mysql112
数据库: ai_slow
```

### 使用命令行

```bash
# 从任何可以访问该 MySQL 服务器的机器
mysql -h 10.10.31.112 -P 3306 -u root -pmysql112 ai_slow

# 查看表
SHOW TABLES;

# 查看表结构
DESCRIBE users;

# 查询数据
SELECT * FROM users LIMIT 10;
```

## 网络配置注意事项

### 1. 防火墙配置

确保 Docker 容器可以访问 MySQL 服务器：

```bash
# 在 MySQL 服务器上（10.10.31.112）
# 检查 3306 端口是否开放
sudo firewall-cmd --list-ports

# 如果未开放，添加规则
sudo firewall-cmd --permanent --add-port=3306/tcp
sudo firewall-cmd --reload
```

### 2. MySQL 用户权限

确保 root 用户允许从应用服务器访问：

```sql
-- 连接到 MySQL
mysql -u root -pmysql112

-- 查看用户权限
SELECT host, user FROM mysql.user WHERE user='root';

-- 如果需要，授予远程访问权限
GRANT ALL PRIVILEGES ON ai_slow.* TO 'root'@'%' IDENTIFIED BY 'mysql112';
GRANT ALL PRIVILEGES ON ai_slow.* TO 'root'@'10.10.31.193' IDENTIFIED BY 'mysql112';
FLUSH PRIVILEGES;
```

### 3. MySQL 配置

检查 MySQL 是否允许远程连接：

```bash
# 查看 MySQL 配置
cat /etc/my.cnf | grep bind-address

# 如果 bind-address=127.0.0.1，需要修改为 0.0.0.0
# 编辑配置文件
sudo vi /etc/my.cnf

# 修改或添加
[mysqld]
bind-address = 0.0.0.0

# 重启 MySQL
sudo systemctl restart mysqld
```

## 故障排查

### 1. 连接超时

```bash
# 测试网络连通性
ping 10.10.31.112

# 测试端口是否开放
telnet 10.10.31.112 3306
# 或
nc -zv 10.10.31.112 3306
```

### 2. 认证失败

```bash
# 检查用户名和密码
mysql -h 10.10.31.112 -u root -pmysql112

# 如果失败，重置密码或创建新用户
```

### 3. 权限不足

```sql
-- 检查用户权限
SHOW GRANTS FOR 'root'@'%';
SHOW GRANTS FOR 'root'@'10.10.31.193';

-- 授予所有权限
GRANT ALL PRIVILEGES ON ai_slow.* TO 'root'@'%';
FLUSH PRIVILEGES;
```

### 4. 字符集问题

```sql
-- 检查数据库字符集
SHOW CREATE DATABASE ai_slow;

-- 修改数据库字符集
ALTER DATABASE ai_slow CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 检查表字符集
SHOW CREATE TABLE table_name;
```

## 备份和恢复

### 备份数据库

```bash
# 完整备份
mysqldump -h 10.10.31.112 -u root -pmysql112 ai_slow > ai_slow_backup_$(date +%Y%m%d_%H%M%S).sql

# 只备份结构
mysqldump -h 10.10.31.112 -u root -pmysql112 --no-data ai_slow > ai_slow_structure.sql

# 只备份数据
mysqldump -h 10.10.31.112 -u root -pmysql112 --no-create-info ai_slow > ai_slow_data.sql
```

### 恢复数据库

```bash
# 恢复备份
mysql -h 10.10.31.112 -u root -pmysql112 ai_slow < ai_slow_backup.sql
```

## 性能优化建议

### 1. 连接池配置

已在 `backend/app/database/base.py` 中配置：
```python
engine_kwargs.update({
    "pool_size": 10,           # 连接池大小
    "max_overflow": 20,        # 最大溢出连接数
    "pool_recycle": 3600,      # 连接回收时间（秒）
    "pool_pre_ping": True      # 连接前测试
})
```

### 2. 索引优化

根据实际查询需求添加索引：
```sql
-- 示例：为常用查询字段添加索引
CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_created_at ON health_data(created_at);
```

### 3. 查询优化

```sql
-- 分析慢查询
SHOW VARIABLES LIKE 'slow_query_log%';

-- 启用慢查询日志
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;
```

## 安全建议

1. **不要使用 root 用户**：创建专用数据库用户
   ```sql
   CREATE USER 'agent_user'@'10.10.31.193' IDENTIFIED BY 'strong_password';
   GRANT ALL PRIVILEGES ON ai_slow.* TO 'agent_user'@'10.10.31.193';
   FLUSH PRIVILEGES;
   ```

2. **使用强密码**：修改默认密码

3. **限制访问来源**：只允许应用服务器 IP 访问

4. **定期备份**：设置自动备份任务

5. **监控日志**：定期检查 MySQL 错误日志

---

**配置完成！现在应用将使用外部 MySQL 服务器存储数据。** ✅
