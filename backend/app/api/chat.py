"""聊天API路由"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, AsyncGenerator
import json
import asyncio

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
    与AI智能体对话（非流式）
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


@router.post("/stream")
async def chat_stream(request: ChatRequest, db: Session = Depends(get_db)):
    """
    与AI智能体对话（真正的流式返回）
    """
    async def generate() -> AsyncGenerator[str, None]:
        try:
            from langchain.callbacks.base import AsyncCallbackHandler
            from langchain.schema import LLMResult
            
            # 创建流式回调处理器
            class StreamingCallbackHandler(AsyncCallbackHandler):
                def __init__(self):
                    self.tokens = []
                    
                async def on_llm_new_token(self, token: str, **kwargs) -> None:
                    """LLM生成新token时调用"""
                    self.tokens.append(token)
                    
                async def on_llm_end(self, response: LLMResult, **kwargs) -> None:
                    """LLM完成时调用"""
                    pass
            
            # 创建Agent实例
            agent = ChronicDiseaseAgent(
                db=db,
                user_id=request.user_id,
                session_id=request.session_id
            )
            
            # 保存用户消息
            agent.memory.add_message("user", request.message)
            
            # 发送开始事件
            yield f"data: {json.dumps({'type': 'start', 'session_id': agent.memory.session_id})}\n\n"
            
            # 获取对话历史
            chat_history = agent.memory.format_for_llm()
            
            # 创建流式回调
            streaming_handler = StreamingCallbackHandler()
            
            # 调用Agent（使用流式回调）
            full_response = ""
            tool_calls = []
            last_token_count = 0
            
            # 使用astream_events进行真正的流式处理
            async for event in agent.agent_executor.astream_events(
                {
                    "input": request.message,
                    "chat_history": chat_history
                },
                version="v1"
            ):
                kind = event["event"]
                
                # 工具调用开始
                if kind == "on_tool_start":
                    tool_name = event.get("name", "unknown")
                    yield f"data: {json.dumps({'type': 'tool_start', 'tool': tool_name})}\n\n"
                
                # 工具调用结束
                elif kind == "on_tool_end":
                    tool_output = str(event.get("data", {}).get("output", ""))[:200]
                    tool_call = {
                        "tool": event.get("name", "unknown"),
                        "output": tool_output
                    }
                    tool_calls.append(tool_call)
                    yield f"data: {json.dumps({'type': 'tool', 'data': tool_call})}\n\n"
                
                # LLM流式输出
                elif kind == "on_chat_model_stream":
                    chunk = event.get("data", {}).get("chunk")
                    if chunk and hasattr(chunk, "content"):
                        token = chunk.content
                        if token:
                            full_response += token
                            yield f"data: {json.dumps({'type': 'content', 'data': token})}\n\n"
            
            # 保存Agent响应到记忆
            agent.memory.add_message("assistant", full_response, tool_calls)
            
            # 发送完成事件
            yield f"data: {json.dumps({'type': 'done', 'session_id': agent.memory.session_id, 'tool_calls': tool_calls})}\n\n"
            
        except Exception as e:
            error_msg = f"处理消息时出错：{str(e)}"
            print(f"Agent Error: {error_msg}")
            import traceback
            traceback.print_exc()
            yield f"data: {json.dumps({'type': 'error', 'message': '抱歉，我遇到了一些技术问题。请稍后再试。'})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


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


@router.get("/sessions/{user_id}")
def get_chat_sessions(user_id: int, db: Session = Depends(get_db)):
    """获取用户的所有会话列表"""
    try:
        from ..models import ChatHistory
        from sqlalchemy import func, desc
        
        # 查询所有会话，按最后更新时间排序
        sessions = db.query(
            ChatHistory.session_id,
            func.max(ChatHistory.created_at).label('last_message_time'),
            func.count(ChatHistory.id).label('message_count')
        ).filter(
            ChatHistory.user_id == user_id,
            ChatHistory.session_id.isnot(None)
        ).group_by(
            ChatHistory.session_id
        ).order_by(
            desc('last_message_time')
        ).all()
        
        # 获取每个会话的第一条消息作为标题
        result = []
        for session in sessions:
            first_msg = db.query(ChatHistory).filter(
                ChatHistory.user_id == user_id,
                ChatHistory.session_id == session.session_id,
                ChatHistory.role == 'user'
            ).order_by(ChatHistory.created_at).first()
            
            result.append({
                'session_id': session.session_id,
                'title': first_msg.content[:30] + '...' if first_msg and len(first_msg.content) > 30 else (first_msg.content if first_msg else '新对话'),
                'last_message_time': session.last_message_time.isoformat(),
                'message_count': session.message_count
            })
        
        return {'sessions': result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
