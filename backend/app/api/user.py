"""用户API路由"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from ..database import get_db
from ..models import User
from ..models.user import DiseaseType

router = APIRouter(prefix="/api/user", tags=["user"])


class UserCreate(BaseModel):
    """用户创建"""
    username: str
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    height: Optional[int] = None  # 身高(cm)
    disease_type: str
    diagnosis_date: Optional[datetime] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class UserResponse(BaseModel):
    """用户响应"""
    id: int
    username: str
    name: str
    age: Optional[int]
    gender: Optional[str]
    height: Optional[int]
    disease_type: str
    diagnosis_date: Optional[datetime]


@router.post("", response_model=UserResponse)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """创建用户"""
    try:
        # 检查用户名是否已存在
        existing_user = db.query(User).filter(User.username == user_data.username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="用户名已存在")
        
        user = User(
            username=user_data.username,
            name=user_data.name,
            age=user_data.age,
            gender=user_data.gender,
            height=user_data.height,
            disease_type=DiseaseType(user_data.disease_type),
            diagnosis_date=user_data.diagnosis_date,
            phone=user_data.phone,
            email=user_data.email
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return UserResponse(
            id=user.id,
            username=user.username,
            name=user.name,
            age=user.age,
            gender=user.gender,
            height=user.height,
            disease_type=user.disease_type.value,
            diagnosis_date=user.diagnosis_date
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """获取用户信息"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return UserResponse(
        id=user.id,
        username=user.username,
        name=user.name,
        age=user.age,
        gender=user.gender,
        height=user.height,
        disease_type=user.disease_type.value,
        diagnosis_date=user.diagnosis_date
    )


@router.get("")
def list_users(db: Session = Depends(get_db)):
    """获取用户列表"""
    users = db.query(User).all()
    return {
        "users": [
            {
                "id": u.id,
                "username": u.username,
                "name": u.name,
                "disease_type": u.disease_type.value
            }
            for u in users
        ]
    }
