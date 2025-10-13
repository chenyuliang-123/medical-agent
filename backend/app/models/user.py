from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
from datetime import datetime
import enum

from ..database.base import Base


class DiseaseType(str, enum.Enum):
    """慢性病类型"""
    DIABETES = "diabetes"  # 糖尿病
    HYPERTENSION = "hypertension"  # 高血压
    BOTH = "both"  # 两者都有


class User(Base):
    """用户模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    age = Column(Integer)
    gender = Column(String(10))
    
    # 慢性病信息
    disease_type = Column(Enum(DiseaseType), nullable=False)
    diagnosis_date = Column(DateTime)  # 确诊日期
    
    # 联系方式
    phone = Column(String(20))
    email = Column(String(100))
    
    # 时间戳
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<User(id={self.id}, name={self.name}, disease={self.disease_type})>"
