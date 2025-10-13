"""健康数据API路由"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from ..database import get_db
from ..models import BloodGlucose, BloodPressure, Weight
from ..models.health_data import MeasurementType

router = APIRouter(prefix="/api/health", tags=["health"])


class BloodGlucoseCreate(BaseModel):
    """血糖数据创建"""
    user_id: int
    value: float
    measurement_type: str
    measured_at: datetime
    notes: Optional[str] = None


class BloodPressureCreate(BaseModel):
    """血压数据创建"""
    user_id: int
    systolic: int
    diastolic: int
    heart_rate: Optional[int] = None
    measured_at: datetime
    notes: Optional[str] = None


class WeightCreate(BaseModel):
    """体重数据创建"""
    user_id: int
    value: float
    bmi: Optional[float] = None
    measured_at: datetime
    notes: Optional[str] = None


@router.post("/blood-glucose")
def create_blood_glucose(data: BloodGlucoseCreate, db: Session = Depends(get_db)):
    """添加血糖数据"""
    try:
        record = BloodGlucose(
            user_id=data.user_id,
            value=data.value,
            measurement_type=MeasurementType(data.measurement_type),
            measured_at=data.measured_at,
            notes=data.notes
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return {"message": "血糖数据已添加", "id": record.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/blood-pressure")
def create_blood_pressure(data: BloodPressureCreate, db: Session = Depends(get_db)):
    """添加血压数据"""
    try:
        record = BloodPressure(
            user_id=data.user_id,
            systolic=data.systolic,
            diastolic=data.diastolic,
            heart_rate=data.heart_rate,
            measured_at=data.measured_at,
            notes=data.notes
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return {"message": "血压数据已添加", "id": record.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/weight")
def create_weight(data: WeightCreate, db: Session = Depends(get_db)):
    """添加体重数据"""
    try:
        record = Weight(
            user_id=data.user_id,
            value=data.value,
            bmi=data.bmi,
            measured_at=data.measured_at,
            notes=data.notes
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return {"message": "体重数据已添加", "id": record.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/blood-glucose/{user_id}")
def get_blood_glucose(user_id: int, limit: int = 10, db: Session = Depends(get_db)):
    """获取血糖数据"""
    records = db.query(BloodGlucose).filter(
        BloodGlucose.user_id == user_id
    ).order_by(BloodGlucose.measured_at.desc()).limit(limit).all()
    
    return {
        "data": [
            {
                "id": r.id,
                "value": r.value,
                "measurement_type": r.measurement_type.value,
                "measured_at": r.measured_at.isoformat(),
                "notes": r.notes
            }
            for r in records
        ]
    }


@router.get("/blood-pressure/{user_id}")
def get_blood_pressure(user_id: int, limit: int = 10, db: Session = Depends(get_db)):
    """获取血压数据"""
    records = db.query(BloodPressure).filter(
        BloodPressure.user_id == user_id
    ).order_by(BloodPressure.measured_at.desc()).limit(limit).all()
    
    return {
        "data": [
            {
                "id": r.id,
                "systolic": r.systolic,
                "diastolic": r.diastolic,
                "heart_rate": r.heart_rate,
                "measured_at": r.measured_at.isoformat(),
                "notes": r.notes
            }
            for r in records
        ]
    }
