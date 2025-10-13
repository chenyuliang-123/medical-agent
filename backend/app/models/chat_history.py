from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func

from ..database.base import Base


class ChatHistory(Base):
    """对话历史模型"""
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String(100), index=True)  # 会话ID
    
    # 消息内容
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    
    # Agent相关
    tool_calls = Column(JSON)  # 工具调用记录
    metadata = Column(JSON)  # 其他元数据
    
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<ChatHistory(id={self.id}, role={self.role})>"
