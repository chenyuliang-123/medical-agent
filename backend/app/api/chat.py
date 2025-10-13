"""聊天API路由"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict

from ..database import get_db
from ..agent import ChronicDiseaseAgent

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    """聊天请求"""
    message: str
    user_id: int
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    """聊天响应"""
    response: str
    tool_calls: List[Dict] = []
    session_id: str


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    与AI智能体对话
    """
    try:
        # 创建Agent实例
        agent = ChronicDiseaseAgent(
            db=db,
            user_id=request.user_id,
            session_id=request.session_id
        )
        
        # 处理消息
        result = await agent.chat(request.message)
        
        return ChatResponse(
            response=result["response"],
            tool_calls=result.get("tool_calls", []),
            session_id=result["session_id"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{user_id}")
def get_chat_history(
    user_id: int,
    session_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取对话历史"""
    try:
        agent = ChronicDiseaseAgent(db, user_id, session_id)
        history = agent.get_conversation_history()
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/history/{user_id}")
def clear_chat_history(
    user_id: int,
    session_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """清除对话历史"""
    try:
        agent = ChronicDiseaseAgent(db, user_id, session_id)
        agent.clear_conversation()
        return {"message": "对话历史已清除"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
