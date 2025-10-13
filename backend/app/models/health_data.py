from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from ..database.base import Base


class MeasurementType(str, enum.Enum):
    """测量类型"""
    FASTING = "fasting"  # 空腹
    BEFORE_MEAL = "before_meal"  # 餐前
    AFTER_MEAL = "after_meal"  # 餐后
    BEFORE_SLEEP = "before_sleep"  # 睡前
    RANDOM = "random"  # 随机


class HealthData(Base):
    """健康数据基类"""
    __tablename__ = "health_data"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    data_type = Column(String(50), nullable=False)  # blood_glucose, blood_pressure, weight
    measured_at = Column(DateTime, nullable=False)
    notes = Column(String(500))
    created_at = Column(DateTime, default=func.now())

    __mapper_args__ = {
        "polymorphic_identity": "health_data",
        "polymorphic_on": data_type,
    }


class BloodGlucose(HealthData):
    """血糖数据"""
    __tablename__ = "blood_glucose"

    id = Column(Integer, ForeignKey("health_data.id"), primary_key=True)
    value = Column(Float, nullable=False)  # mmol/L
    measurement_type = Column(Enum(MeasurementType), nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "blood_glucose",
    }

    def __repr__(self):
        return f"<BloodGlucose(value={self.value}, type={self.measurement_type})>"


class BloodPressure(HealthData):
    """血压数据"""
    __tablename__ = "blood_pressure"

    id = Column(Integer, ForeignKey("health_data.id"), primary_key=True)
    systolic = Column(Integer, nullable=False)  # 收缩压
    diastolic = Column(Integer, nullable=False)  # 舒张压
    heart_rate = Column(Integer)  # 心率

    __mapper_args__ = {
        "polymorphic_identity": "blood_pressure",
    }

    def __repr__(self):
        return f"<BloodPressure(systolic={self.systolic}, diastolic={self.diastolic})>"


class Weight(HealthData):
    """体重数据"""
    __tablename__ = "weight"

    id = Column(Integer, ForeignKey("health_data.id"), primary_key=True)
    value = Column(Float, nullable=False)  # kg
    bmi = Column(Float)  # BMI指数

    __mapper_args__ = {
        "polymorphic_identity": "weight",
    }

    def __repr__(self):
        return f"<Weight(value={self.value}, bmi={self.bmi})>"
