"""AI智能体核心引擎 - 基于LangChain的Agent实现"""

from typing import Dict, Any, List
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory

from .tools import get_agent_tools
from .memory import AgentMemory
from .prompts import SYSTEM_PROMPT

load_dotenv()


class ChronicDiseaseAgent:
    """慢病管理AI智能体"""
    
    def __init__(self, db: Session, user_id: int, session_id: str = None):
        self.db = db
        self.user_id = user_id
        self.memory = AgentMemory(db, user_id, session_id)
        
        # 初始化LLM
        # 支持OpenAI和智谱AI
        llm_provider = os.getenv("LLM_PROVIDER", "zhipu")  # openai 或 zhipu
        
        if llm_provider == "zhipu":
            # 使用智谱AI（兼容OpenAI格式）
            self.llm = ChatOpenAI(
                model=os.getenv("ZHIPU_MODEL", "glm-4"),
                temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
                api_key=os.getenv("ZHIPU_API_KEY"),
                base_url="https://open.bigmodel.cn/api/paas/v4/",
                streaming=True  # 启用流式输出
            )
        else:
            # 使用OpenAI
            self.llm = ChatOpenAI(
                model=os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview"),
                temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
                api_key=os.getenv("OPENAI_API_KEY"),
                streaming=True  # 启用流式输出
            )
        
        # 获取工具
        self.tools = get_agent_tools(db, user_id)
        
        # 创建Prompt模板
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # 创建Agent
        self.agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        # 创建Agent执行器
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=os.getenv("AGENT_VERBOSE", "True") == "True",
            max_iterations=int(os.getenv("AGENT_MAX_ITERATIONS", "10")),
            handle_parsing_errors=True,
            return_intermediate_steps=True
        )
    
    async def chat(self, user_message: str) -> Dict[str, Any]:
        """
        与用户对话
        
        参数:
        - user_message: 用户消息
        
        返回:
        - response: Agent响应
        - tool_calls: 工具调用记录
        """
        try:
            # 保存用户消息到记忆
            self.memory.add_message("user", user_message)
            
            # 获取对话历史
            chat_history = self.memory.format_for_llm()
            
            # 调用Agent
            result = await self.agent_executor.ainvoke({
                "input": user_message,
                "chat_history": chat_history
            })
            
            # 提取响应
            response = result.get("output", "抱歉，我遇到了一些问题。")
            intermediate_steps = result.get("intermediate_steps", [])
            
            # 提取工具调用信息
            tool_calls = []
            for step in intermediate_steps:
                if len(step) >= 2:
                    action, observation = step[0], step[1]
                    tool_calls.append({
                        "tool": action.tool if hasattr(action, 'tool') else "unknown",
                        "input": action.tool_input if hasattr(action, 'tool_input') else {},
                        "output": str(observation)[:200]  # 限制长度
                    })
            
            # 保存Agent响应到记忆
            self.memory.add_message("assistant", response, tool_calls)
            
            return {
                "response": response,
                "tool_calls": tool_calls,
                "session_id": self.memory.session_id
            }
            
        except Exception as e:
            error_msg = f"处理消息时出错：{str(e)}"
            print(f"Agent Error: {error_msg}")
            return {
                "response": "抱歉，我遇到了一些技术问题。请稍后再试。",
                "error": error_msg,
                "session_id": self.memory.session_id
            }
    
    def get_conversation_history(self) -> List[Dict]:
        """获取对话历史"""
        return self.memory.get_conversation_history()
    
    def clear_conversation(self):
        """清除对话历史"""
        self.memory.clear_session()
    
    def get_user_context(self) -> Dict[str, Any]:
        """获取用户上下文"""
        return self.memory.get_user_context()


def create_agent(db: Session, user_id: int, session_id: str = None) -> ChronicDiseaseAgent:
    """创建Agent实例的工厂函数"""
    return ChronicDiseaseAgent(db, user_id, session_id)
