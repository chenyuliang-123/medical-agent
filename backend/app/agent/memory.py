"""AI智能体记忆系统"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from ..models import ChatHistory, User


class AgentMemory:
    """Agent记忆管理"""
    
    def __init__(self, db: Session, user_id: int, session_id: str = None):
        self.db = db
        self.user_id = user_id
        self.session_id = session_id or str(uuid.uuid4())
        self.short_term_memory = []  # 当前会话的短期记忆
    
    def add_message(self, role: str, content: str, tool_calls: List[Dict] = None):
        """添加消息到记忆"""
        # 保存到短期记忆
        self.short_term_memory.append({
            "role": role,
            "content": content,
            "tool_calls": tool_calls
        })
        
        # 持久化到数据库
        chat_record = ChatHistory(
            user_id=self.user_id,
            session_id=self.session_id,
            role=role,
            content=content,
            tool_calls=tool_calls
        )
        self.db.add(chat_record)
        self.db.commit()
    
    def get_conversation_history(self, limit: int = 10) -> List[Dict]:
        """获取对话历史"""
        # 优先从短期记忆获取
        if self.short_term_memory:
            return self.short_term_memory[-limit:]
        
        # 从数据库加载
        records = self.db.query(ChatHistory).filter(
            ChatHistory.user_id == self.user_id,
            ChatHistory.session_id == self.session_id
        ).order_by(ChatHistory.created_at.desc()).limit(limit).all()
        
        history = []
        for record in reversed(records):
            history.append({
                "role": record.role,
                "content": record.content,
                "tool_calls": record.tool_calls
            })
        
        return history
    
    def get_user_context(self) -> Dict[str, Any]:
        """获取用户上下文信息"""
        user = self.db.query(User).filter(User.id == self.user_id).first()
        
        if not user:
            return {}
        
        return {
            "name": user.name,
            "age": user.age,
            "gender": user.gender,
            "disease_type": user.disease_type.value if user.disease_type else None,
            "diagnosis_date": user.diagnosis_date.strftime("%Y-%m-%d") if user.diagnosis_date else None
        }
    
    def clear_session(self):
        """清除当前会话"""
        self.short_term_memory = []
        self.session_id = str(uuid.uuid4())
    
    def format_for_llm(self) -> List[Dict[str, str]]:
        """格式化为LLM可用的消息格式"""
        messages = []
        
        # 添加用户上下文
        user_context = self.get_user_context()
        if user_context:
            context_str = f"用户信息：{user_context['name']}"
            if user_context.get('age'):
                context_str += f"，{user_context['age']}岁"
            if user_context.get('disease_type'):
                disease_map = {
                    'diabetes': '糖尿病',
                    'hypertension': '高血压',
                    'both': '糖尿病和高血压'
                }
                context_str += f"，患有{disease_map.get(user_context['disease_type'], user_context['disease_type'])}"
            
            messages.append({
                "role": "system",
                "content": context_str
            })
        
        # 添加对话历史
        for msg in self.get_conversation_history():
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        return messages
