-- MySQL 数据库初始化脚本（仅供参考）
-- 注意：本项目使用外部 MySQL 服务器 (10.10.31.112:3306/ai_slow)
-- 此脚本不会自动执行，仅作为参考

-- 设置字符集
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- 确保数据库存在并配置正确的字符集
-- 在外部 MySQL 服务器上手动执行：
-- CREATE DATABASE IF NOT EXISTS ai_slow CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE ai_slow;

-- 注意：表结构会由 SQLAlchemy 自动创建
-- 应用启动时会自动创建所需的表
