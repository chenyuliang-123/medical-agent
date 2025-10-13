"""添加身高字段到用户表的迁移脚本"""

from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

# 数据库连接
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chronic_disease.db")
engine = create_engine(DATABASE_URL)

def upgrade():
    """添加height字段"""
    with engine.connect() as conn:
        try:
            # 检查字段是否已存在
            result = conn.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result]
            
            if 'height' not in columns:
                print("正在添加height字段到users表...")
                conn.execute(text("ALTER TABLE users ADD COLUMN height INTEGER"))
                conn.commit()
                print("✅ height字段添加成功！")
            else:
                print("⚠️  height字段已存在，跳过迁移")
                
        except Exception as e:
            print(f"❌ 迁移失败: {e}")
            conn.rollback()

def downgrade():
    """移除height字段（SQLite不支持DROP COLUMN）"""
    print("⚠️  SQLite不支持DROP COLUMN，如需回滚请手动处理")

if __name__ == "__main__":
    print("开始数据库迁移...")
    upgrade()
    print("迁移完成！")
