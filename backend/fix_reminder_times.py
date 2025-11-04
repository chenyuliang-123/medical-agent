#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复提醒时间格式问题
"""

from datetime import datetime
from sqlalchemy.orm import Session
from app.database.base import SessionLocal, engine
from app.models.reminder import Reminder

def fix_reminder_times():
    """修复数据库中的提醒时间"""
    db = SessionLocal()
    
    try:
        # 获取所有提醒
        reminders = db.query(Reminder).all()
        
        print(f"找到 {len(reminders)} 条提醒记录")
        
        fixed_count = 0
        for reminder in reminders:
            old_time = reminder.remind_at
            
            # 检查时间是否有问题
            if old_time:
                # 如果年份不合理（小于2024或大于2030）
                if old_time.year < 2024 or old_time.year > 2030:
                    # 设置为今天的同一时间
                    now = datetime.now()
                    new_time = now.replace(
                        hour=old_time.hour,
                        minute=old_time.minute,
                        second=old_time.second if old_time.second else 0,
                        microsecond=0
                    )
                    
                    print(f"修复提醒 ID {reminder.id}:")
                    print(f"  标题: {reminder.title}")
                    print(f"  旧时间: {old_time}")
                    print(f"  新时间: {new_time}")
                    
                    reminder.remind_at = new_time
                    fixed_count += 1
                
                # 确保秒数存在
                elif old_time.second is None:
                    new_time = old_time.replace(second=0)
                    print(f"补充秒数 ID {reminder.id}: {old_time} -> {new_time}")
                    reminder.remind_at = new_time
                    fixed_count += 1
        
        if fixed_count > 0:
            db.commit()
            print(f"\n✅ 成功修复 {fixed_count} 条提醒记录")
        else:
            print("\n✅ 所有提醒时间格式正确，无需修复")
            
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        db.rollback()
    finally:
        db.close()


def show_all_reminders():
    """显示所有提醒"""
    db = SessionLocal()
    
    try:
        reminders = db.query(Reminder).all()
        
        print("\n" + "="*80)
        print("所有提醒记录:")
        print("="*80)
        
        for reminder in reminders:
            print(f"\nID: {reminder.id}")
            print(f"  用户ID: {reminder.user_id}")
            print(f"  类型: {reminder.reminder_type}")
            print(f"  标题: {reminder.title}")
            print(f"  内容: {reminder.content}")
            print(f"  提醒时间: {reminder.remind_at}")
            print(f"  是否重复: {reminder.is_recurring}")
            print(f"  重复模式: {reminder.recurrence_pattern}")
            print(f"  是否激活: {reminder.is_active}")
            print(f"  是否完成: {reminder.is_completed}")
            
    finally:
        db.close()


if __name__ == "__main__":
    print("🔧 开始修复提醒时间...")
    fix_reminder_times()
    show_all_reminders()
    print("\n✅ 完成！")
