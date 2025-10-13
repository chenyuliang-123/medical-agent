"""初始化数据库并添加示例数据"""

from datetime import datetime, timedelta
import random
from app.database import SessionLocal, init_db
from app.models import User, BloodGlucose, BloodPressure, Weight, Reminder
from app.models.user import DiseaseType
from app.models.health_data import MeasurementType
from app.models.reminder import ReminderType

def create_sample_data():
    """创建示例数据"""
    db = SessionLocal()
    
    try:
        # 创建示例用户
        user = User(
            username="zhangsan",
            name="张三",
            age=55,
            gender="男",
            disease_type=DiseaseType.BOTH,
            diagnosis_date=datetime.now() - timedelta(days=365*2),
            phone="13800138000",
            email="zhangsan@example.com"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print(f"✅ 创建用户: {user.name} (ID: {user.id})")
        
        # 创建血糖数据（最近7天）
        measurement_types = [
            MeasurementType.FASTING,
            MeasurementType.AFTER_MEAL,
            MeasurementType.BEFORE_SLEEP
        ]
        
        for i in range(21):  # 7天 x 3次
            day_offset = i // 3
            type_index = i % 3
            
            measured_time = datetime.now() - timedelta(days=day_offset)
            
            if measurement_types[type_index] == MeasurementType.FASTING:
                measured_time = measured_time.replace(hour=7, minute=0)
                value = round(random.uniform(5.8, 7.2), 1)
            elif measurement_types[type_index] == MeasurementType.AFTER_MEAL:
                measured_time = measured_time.replace(hour=13, minute=30)
                value = round(random.uniform(7.5, 9.5), 1)
            else:  # BEFORE_SLEEP
                measured_time = measured_time.replace(hour=21, minute=30)
                value = round(random.uniform(6.5, 8.5), 1)
            
            glucose = BloodGlucose(
                user_id=user.id,
                value=value,
                measurement_type=measurement_types[type_index],
                measured_at=measured_time
            )
            db.add(glucose)
        
        print("✅ 创建血糖数据: 21条")
        
        # 创建血压数据（最近7天，每天2次）
        for i in range(14):
            day_offset = i // 2
            is_morning = i % 2 == 0
            
            measured_time = datetime.now() - timedelta(days=day_offset)
            measured_time = measured_time.replace(
                hour=7 if is_morning else 19,
                minute=0
            )
            
            systolic = random.randint(120, 140)
            diastolic = random.randint(75, 90)
            heart_rate = random.randint(65, 85)
            
            pressure = BloodPressure(
                user_id=user.id,
                systolic=systolic,
                diastolic=diastolic,
                heart_rate=heart_rate,
                measured_at=measured_time
            )
            db.add(pressure)
        
        print("✅ 创建血压数据: 14条")
        
        # 创建体重数据（最近7天）
        base_weight = 72.5
        for i in range(7):
            measured_time = datetime.now() - timedelta(days=i)
            measured_time = measured_time.replace(hour=7, minute=30)
            
            weight_value = round(base_weight + random.uniform(-0.5, 0.5), 1)
            bmi = round(weight_value / (1.70 ** 2), 1)
            
            weight = Weight(
                user_id=user.id,
                value=weight_value,
                bmi=bmi,
                measured_at=measured_time
            )
            db.add(weight)
        
        print("✅ 创建体重数据: 7条")
        
        # 创建提醒
        reminders_data = [
            {
                "type": ReminderType.MEASUREMENT,
                "title": "早餐后血糖测量",
                "content": "请在早餐后2小时测量血糖",
                "hour": 9,
                "minute": 0
            },
            {
                "type": ReminderType.MEDICATION,
                "title": "服用降压药",
                "content": "请按时服用降压药",
                "hour": 8,
                "minute": 0
            },
            {
                "type": ReminderType.EXERCISE,
                "title": "午餐后散步",
                "content": "建议散步30分钟",
                "hour": 13,
                "minute": 0
            },
            {
                "type": ReminderType.MEASUREMENT,
                "title": "晚餐后血糖测量",
                "content": "请在晚餐后2小时测量血糖",
                "hour": 19,
                "minute": 30
            }
        ]
        
        for reminder_data in reminders_data:
            remind_time = datetime.now().replace(
                hour=reminder_data["hour"],
                minute=reminder_data["minute"],
                second=0,
                microsecond=0
            )
            
            # 如果时间已过，设置为明天
            if remind_time < datetime.now():
                remind_time += timedelta(days=1)
            
            reminder = Reminder(
                user_id=user.id,
                reminder_type=reminder_data["type"],
                title=reminder_data["title"],
                content=reminder_data["content"],
                remind_at=remind_time,
                is_recurring=True,
                recurrence_pattern="daily"
            )
            db.add(reminder)
        
        print("✅ 创建提醒: 4条")
        
        db.commit()
        print("\n🎉 示例数据创建完成！")
        print(f"\n📝 测试账号信息：")
        print(f"   用户ID: {user.id}")
        print(f"   用户名: {user.username}")
        print(f"   姓名: {user.name}")
        print(f"   疾病类型: 糖尿病+高血压")
        
    except Exception as e:
        print(f"❌ 创建示例数据失败: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 开始初始化数据库...")
    init_db()
    print("✅ 数据库初始化完成\n")
    
    print("📦 创建示例数据...")
    create_sample_data()
