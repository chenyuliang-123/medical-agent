#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
清理并重新创建示例提醒数据
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database.base import SessionLocal
from app.models.reminder import Reminder, ReminderType

def reset_reminders(user_id: int = 1):
    """清理并重新创建提醒数据"""
    db = SessionLocal()
    
    try:
        # 删除该用户的所有提醒
        deleted = db.query(Reminder).filter(Reminder.user_id == user_id).delete()
        print(f"删除了 {deleted} 条旧提醒记录")
        
        # 创建新的示例提醒
        now = datetime.now()
        
        reminders_data = [
            {
                "title": "早餐后血糖测量",
                "type": ReminderType.MEASUREMENT,
                "content": "请在早餐后2小时测量血糖",
                "time": now.replace(hour=9, minute=0, second=0, microsecond=0),
                "recurring": True,
                "pattern": "daily"
            },
            {
                "title": "服用降压药",
                "type": ReminderType.MEDICATION,
                "content": "请按时服用降压药",
                "time": now.replace(hour=8, minute=0, second=0, microsecond=0),
                "recurring": True,
                "pattern": "daily"
            },
            {
                "title": "午餐散步",
                "type": ReminderType.EXERCISE,
                "content": "午餐后散步30分钟",
                "time": now.replace(hour=13, minute=0, second=0, microsecond=0),
                "recurring": True,
                "pattern": "daily"
            },
            {
                "title": "晚餐前血糖测量",
                "type": ReminderType.MEASUREMENT,
                "content": "请在晚餐前测量血糖",
                "time": now.replace(hour=17, minute=30, second=0, microsecond=0),
                "recurring": True,
                "pattern": "daily"
            },
            {
                "title": "血糖监测提醒",
                "type": ReminderType.MEASUREMENT,
                "content": "请在早餐后2小时测量血糖",
                "time": (now + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0),
                "recurring": False,
                "pattern": None
            }
        ]
        
        for data in reminders_data:
            reminder = Reminder(
                user_id=user_id,
                reminder_type=data["type"],
                title=data["title"],
                content=data["content"],
                remind_at=data["time"],
                is_recurring=data["recurring"],
                recurrence_pattern=data["pattern"]
            )
            db.add(reminder)
            print(f"创建提醒: {data['title']} - {data['time'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        db.commit()
        print(f"\n✅ 成功创建 {len(reminders_data)} 条新提醒")
        
        # 显示创建的提醒
        print("\n" + "="*80)
        print("新创建的提醒:")
        print("="*80)
        
        reminders = db.query(Reminder).filter(Reminder.user_id == user_id).all()
        for reminder in reminders:
            print(f"\nID: {reminder.id}")
            print(f"  类型: {reminder.reminder_type.value}")
            print(f"  标题: {reminder.title}")
            print(f"  提醒时间: {reminder.remind_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  是否重复: {reminder.is_recurring}")
            print(f"  重复模式: {reminder.recurrence_pattern}")
        
    except Exception as e:
        print(f"❌ 操作失败: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("🔄 开始重置提醒数据...")
    print("="*80)
    reset_reminders(user_id=1)
    print("\n✅ 完成！")
