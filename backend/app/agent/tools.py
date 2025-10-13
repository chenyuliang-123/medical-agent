"""AI智能体工具集 - Agent可以调用这些工具来完成任务"""

from langchain.tools import tool
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
import json

from ..models import HealthData, BloodGlucose, BloodPressure, Weight, Reminder, User
from ..models.health_data import MeasurementType
from ..models.reminder import ReminderType


class HealthTools:
    """健康管理工具类"""
    
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id
    
    @tool
    def query_health_data(
        self,
        data_type: str,
        days: int = 7,
        limit: int = 10
    ) -> str:
        """
        查询用户的健康数据
        
        参数:
        - data_type: 数据类型，可选值：blood_glucose(血糖), blood_pressure(血压), weight(体重)
        - days: 查询最近多少天的数据，默认7天
        - limit: 最多返回多少条记录，默认10条
        
        返回: JSON格式的健康数据列表
        """
        try:
            # 计算起始日期
            start_date = datetime.now() - timedelta(days=days)
            
            # 根据类型查询
            if data_type == "blood_glucose":
                query = self.db.query(BloodGlucose).filter(
                    and_(
                        BloodGlucose.user_id == self.user_id,
                        BloodGlucose.measured_at >= start_date
                    )
                ).order_by(desc(BloodGlucose.measured_at)).limit(limit)
                
                results = []
                for record in query:
                    results.append({
                        "date": record.measured_at.strftime("%Y-%m-%d %H:%M"),
                        "value": record.value,
                        "type": record.measurement_type.value,
                        "unit": "mmol/L",
                        "notes": record.notes
                    })
                    
            elif data_type == "blood_pressure":
                query = self.db.query(BloodPressure).filter(
                    and_(
                        BloodPressure.user_id == self.user_id,
                        BloodPressure.measured_at >= start_date
                    )
                ).order_by(desc(BloodPressure.measured_at)).limit(limit)
                
                results = []
                for record in query:
                    results.append({
                        "date": record.measured_at.strftime("%Y-%m-%d %H:%M"),
                        "systolic": record.systolic,
                        "diastolic": record.diastolic,
                        "heart_rate": record.heart_rate,
                        "notes": record.notes
                    })
                    
            elif data_type == "weight":
                query = self.db.query(Weight).filter(
                    and_(
                        Weight.user_id == self.user_id,
                        Weight.measured_at >= start_date
                    )
                ).order_by(desc(Weight.measured_at)).limit(limit)
                
                results = []
                for record in query:
                    results.append({
                        "date": record.measured_at.strftime("%Y-%m-%d %H:%M"),
                        "value": record.value,
                        "bmi": record.bmi,
                        "unit": "kg",
                        "notes": record.notes
                    })
            else:
                return json.dumps({"error": f"不支持的数据类型: {data_type}"}, ensure_ascii=False)
            
            if not results:
                return json.dumps({
                    "message": f"最近{days}天没有{data_type}数据",
                    "data": []
                }, ensure_ascii=False)
            
            return json.dumps({
                "data_type": data_type,
                "count": len(results),
                "data": results
            }, ensure_ascii=False)
            
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)
    
    @tool
    def analyze_health_trend(self, data_type: str, days: int = 30) -> str:
        """
        分析健康数据趋势
        
        参数:
        - data_type: 数据类型（blood_glucose, blood_pressure, weight）
        - days: 分析最近多少天的数据
        
        返回: 趋势分析结果
        """
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            if data_type == "blood_glucose":
                records = self.db.query(BloodGlucose).filter(
                    and_(
                        BloodGlucose.user_id == self.user_id,
                        BloodGlucose.measured_at >= start_date
                    )
                ).order_by(BloodGlucose.measured_at).all()
                
                if not records:
                    return json.dumps({"message": "没有足够的数据进行分析"}, ensure_ascii=False)
                
                values = [r.value for r in records]
                avg = sum(values) / len(values)
                max_val = max(values)
                min_val = min(values)
                
                # 计算趋势
                if len(values) >= 2:
                    first_half = values[:len(values)//2]
                    second_half = values[len(values)//2:]
                    avg_first = sum(first_half) / len(first_half)
                    avg_second = sum(second_half) / len(second_half)
                    
                    if avg_second > avg_first + 0.5:
                        trend = "上升"
                    elif avg_second < avg_first - 0.5:
                        trend = "下降"
                    else:
                        trend = "平稳"
                else:
                    trend = "数据不足"
                
                # 异常统计
                high_count = sum(1 for v in values if v > 7.0)
                low_count = sum(1 for v in values if v < 3.9)
                
                return json.dumps({
                    "data_type": "血糖",
                    "period": f"最近{days}天",
                    "count": len(values),
                    "average": round(avg, 2),
                    "max": max_val,
                    "min": min_val,
                    "trend": trend,
                    "high_count": high_count,
                    "low_count": low_count,
                    "analysis": f"平均血糖{round(avg, 2)}mmol/L，趋势{trend}。"
                               f"有{high_count}次偏高，{low_count}次偏低。"
                }, ensure_ascii=False)
                
            elif data_type == "blood_pressure":
                records = self.db.query(BloodPressure).filter(
                    and_(
                        BloodPressure.user_id == self.user_id,
                        BloodPressure.measured_at >= start_date
                    )
                ).order_by(BloodPressure.measured_at).all()
                
                if not records:
                    return json.dumps({"message": "没有足够的数据进行分析"}, ensure_ascii=False)
                
                systolic_values = [r.systolic for r in records]
                diastolic_values = [r.diastolic for r in records]
                
                avg_sys = sum(systolic_values) / len(systolic_values)
                avg_dia = sum(diastolic_values) / len(diastolic_values)
                
                high_count = sum(1 for s, d in zip(systolic_values, diastolic_values) 
                               if s >= 140 or d >= 90)
                
                return json.dumps({
                    "data_type": "血压",
                    "period": f"最近{days}天",
                    "count": len(records),
                    "average_systolic": round(avg_sys, 1),
                    "average_diastolic": round(avg_dia, 1),
                    "high_count": high_count,
                    "analysis": f"平均血压{round(avg_sys, 1)}/{round(avg_dia, 1)}mmHg，"
                               f"有{high_count}次超标。"
                }, ensure_ascii=False)
            
            else:
                return json.dumps({"error": "不支持的数据类型"}, ensure_ascii=False)
                
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)
    
    @tool
    def create_reminder(
        self,
        title: str,
        reminder_type: str,
        remind_time: str,
        content: Optional[str] = None,
        is_recurring: bool = False,
        recurrence_pattern: Optional[str] = None
    ) -> str:
        """
        创建健康提醒
        
        参数:
        - title: 提醒标题
        - reminder_type: 提醒类型（medication-用药, measurement-测量, exercise-运动, checkup-复查）
        - remind_time: 提醒时间，格式：YYYY-MM-DD HH:MM 或 HH:MM（今天）
        - content: 提醒内容（可选）
        - is_recurring: 是否重复（可选）
        - recurrence_pattern: 重复模式（daily-每天, weekly-每周, monthly-每月）
        
        返回: 创建结果
        """
        try:
            # 解析时间
            if ":" in remind_time and "-" not in remind_time:
                # 只有时间，默认今天
                time_parts = remind_time.split(":")
                remind_at = datetime.now().replace(
                    hour=int(time_parts[0]),
                    minute=int(time_parts[1]),
                    second=0,
                    microsecond=0
                )
            else:
                remind_at = datetime.strptime(remind_time, "%Y-%m-%d %H:%M")
            
            # 映射提醒类型
            type_map = {
                "medication": ReminderType.MEDICATION,
                "measurement": ReminderType.MEASUREMENT,
                "exercise": ReminderType.EXERCISE,
                "checkup": ReminderType.CHECKUP
            }
            
            reminder = Reminder(
                user_id=self.user_id,
                reminder_type=type_map.get(reminder_type, ReminderType.CUSTOM),
                title=title,
                content=content,
                remind_at=remind_at,
                is_recurring=is_recurring,
                recurrence_pattern=recurrence_pattern
            )
            
            self.db.add(reminder)
            self.db.commit()
            
            return json.dumps({
                "success": True,
                "message": f"已创建提醒：{title}",
                "remind_at": remind_at.strftime("%Y-%m-%d %H:%M"),
                "is_recurring": is_recurring
            }, ensure_ascii=False)
            
        except Exception as e:
            self.db.rollback()
            return json.dumps({"error": str(e)}, ensure_ascii=False)
    
    @tool
    def calculate_health_metrics(self, metric_type: str, **params) -> str:
        """
        计算健康指标
        
        参数:
        - metric_type: 指标类型（bmi-身体质量指数, hba1c_estimate-估算糖化血红蛋白）
        - params: 计算所需参数
        
        返回: 计算结果
        """
        try:
            if metric_type == "bmi":
                weight = params.get("weight")  # kg
                height = params.get("height")  # cm
                
                if not weight or not height:
                    return json.dumps({"error": "需要体重(kg)和身高(cm)参数"}, ensure_ascii=False)
                
                height_m = height / 100
                bmi = weight / (height_m ** 2)
                
                if bmi < 18.5:
                    category = "偏瘦"
                elif bmi < 24:
                    category = "正常"
                elif bmi < 28:
                    category = "超重"
                else:
                    category = "肥胖"
                
                return json.dumps({
                    "metric": "BMI",
                    "value": round(bmi, 2),
                    "category": category,
                    "interpretation": f"您的BMI为{round(bmi, 2)}，属于{category}范围"
                }, ensure_ascii=False)
            
            elif metric_type == "hba1c_estimate":
                # 根据平均血糖估算HbA1c
                avg_glucose = params.get("avg_glucose")  # mmol/L
                
                if not avg_glucose:
                    return json.dumps({"error": "需要平均血糖值"}, ensure_ascii=False)
                
                # 简化公式：HbA1c(%) ≈ (平均血糖mmol/L + 2.59) / 1.59
                hba1c = (avg_glucose + 2.59) / 1.59
                
                if hba1c < 6.5:
                    category = "控制良好"
                elif hba1c < 7.0:
                    category = "控制尚可"
                elif hba1c < 8.0:
                    category = "需要改善"
                else:
                    category = "控制不佳"
                
                return json.dumps({
                    "metric": "HbA1c估算",
                    "value": round(hba1c, 2),
                    "unit": "%",
                    "category": category,
                    "note": "这是基于平均血糖的估算值，实际值需要验血检测"
                }, ensure_ascii=False)
            
            else:
                return json.dumps({"error": "不支持的指标类型"}, ensure_ascii=False)
                
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)
    
    @tool
    def search_knowledge(self, query: str) -> str:
        """
        检索医疗知识库
        
        参数:
        - query: 查询问题
        
        返回: 相关知识
        """
        # 这里简化实现，实际应该使用向量数据库检索
        knowledge_base = {
            "血糖": {
                "正常范围": "空腹血糖：3.9-6.1mmol/L，餐后2小时：<7.8mmol/L",
                "低血糖": "<3.9mmol/L，症状包括心慌、出汗、饥饿感，需立即补充糖分",
                "高血糖": "空腹>7.0或餐后>11.1，长期高血糖会导致并发症",
                "监测频率": "建议每天测3-4次：空腹、三餐后2小时"
            },
            "血压": {
                "正常范围": "收缩压<120mmHg，舒张压<80mmHg",
                "高血压": "收缩压≥140mmHg或舒张压≥90mmHg",
                "监测": "建议每天早晚各测一次，取平均值"
            },
            "饮食": {
                "糖尿病": "控制总热量，少食多餐，低GI食物为主，多吃蔬菜",
                "高血压": "低盐饮食（<6g/天），多吃钾丰富食物，控制体重"
            },
            "运动": {
                "建议": "每周至少150分钟中等强度运动，如快走、游泳",
                "注意": "餐后1小时运动，避免空腹运动，随身携带糖果"
            }
        }
        
        # 简单关键词匹配
        results = []
        query_lower = query.lower()
        
        for category, items in knowledge_base.items():
            if category in query:
                results.append({
                    "category": category,
                    "content": items
                })
        
        if not results:
            # 返回相关的所有信息
            for category, items in knowledge_base.items():
                for key, value in items.items():
                    if any(word in query for word in [category, key]):
                        results.append({
                            "category": category,
                            "topic": key,
                            "content": value
                        })
        
        if results:
            return json.dumps(results, ensure_ascii=False)
        else:
            return json.dumps({
                "message": "未找到相关知识，请尝试其他关键词",
                "suggestions": ["血糖", "血压", "饮食", "运动"]
            }, ensure_ascii=False)


def get_agent_tools(db: Session, user_id: int) -> List:
    """获取Agent可用的工具列表"""
    health_tools = HealthTools(db, user_id)
    
    return [
        health_tools.query_health_data,
        health_tools.analyze_health_trend,
        health_tools.create_reminder,
        health_tools.calculate_health_metrics,
        health_tools.search_knowledge,
    ]
