"""FastAPI主应用"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from .database import init_db
from .api import chat_router, health_router, user_router

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    print("🚀 初始化数据库...")
    init_db()
    print("✅ 数据库初始化完成")
    
    yield
    
    # 关闭时清理资源
    print("👋 应用关闭")


# 创建FastAPI应用
app = FastAPI(
    title=os.getenv("APP_NAME", "慢病管理AI智能体"),
    version=os.getenv("APP_VERSION", "1.0.0"),
    description="基于LangChain的慢病管理AI智能体系统",
    lifespan=lifespan
)

# 配置CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(chat_router)
app.include_router(health_router)
app.include_router(user_router)


@app.get("/")
def read_root():
    """根路径"""
    return {
        "message": "慢病管理AI智能体API",
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health")
def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=os.getenv("DEBUG", "True") == "True"
    )
