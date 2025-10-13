from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.sql import func
import enum

from ..database.base import Base


class ReminderType(str, enum.Enum):
    """提醒类型"""
    MEDICATION = "medication"  # 用药提醒
    MEASUREMENT = "measurement"  # 测量提醒
    EXERCISE = "exercise"  # 运动提醒
    CHECKUP = "checkup"  # 复查提醒
    CUSTOM = "custom"  # 自定义提醒


class Reminder(Base):
    """提醒模型"""
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    reminder_type = Column(Enum(ReminderType), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(String(1000))
    
    # 提醒时间
    remind_at = Column(DateTime, nullable=False)
    
    # 是否重复
    is_recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(String(100))  # daily, weekly, monthly
    
    # 状态
    is_active = Column(Boolean, default=True)
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Reminder(id={self.id}, type={self.reminder_type}, title={self.title})>"
