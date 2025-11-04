from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# 数据库URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chronic_disease.db")

# 根据数据库类型设置连接参数
connect_args = {}
engine_kwargs = {
    "echo": os.getenv("DEBUG", "False") == "True"
}

if "sqlite" in DATABASE_URL:
    connect_args = {"check_same_thread": False}
elif "mysql" in DATABASE_URL:
    # MySQL 连接池配置
    engine_kwargs.update({
        "pool_size": 10,
        "max_overflow": 20,
        "pool_recycle": 3600,
        "pool_pre_ping": True
    })

# 创建引擎
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    **engine_kwargs
)

# 创建会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库"""
    from app.models import User, HealthData, Reminder, ChatHistory
    Base.metadata.create_all(bind=engine)
