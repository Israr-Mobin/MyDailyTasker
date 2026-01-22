"""
Daily Task Management
=====================
Utilities for creating and managing daily task instances.

DailyTask records are generated automatically when users view a date,
ensuring that all master tasks have corresponding daily entries.
"""

from datetime import date, timedelta
from models import db, Task, DailyTask


def ensure_daily_tasks(user_id, selected_date):
    """
    Ensure DailyTask records exist for all user tasks on a given date.
    
    Creates missing DailyTask entries by comparing the user's master
    task list with existing daily tasks for the date.
    
    Args:
        user_id (int): User's database ID
        selected_date (date): Date to ensure tasks for
    
    This function is idempotent - safe to call multiple times.
    """
    # Get all master tasks for user
    tasks = Task.query.filter_by(user_id=user_id).all()

    # Get existing daily tasks for this date
    existing = {
        dt.task_id
        for dt in DailyTask.query.filter_by(
            user_id=user_id,
            date=selected_date
        ).all()
    }

    # Create missing daily tasks
    for task in tasks:
        if task.id not in existing:
            daily = DailyTask(
                user_id=user_id,
                task_id=task.id,
                date=selected_date,
                completed=False
            )
            db.session.add(daily)

    db.session.commit()


def ensure_daily_tasks_range(user_id, start_date, end_date):
    """
    Ensure DailyTask records exist for a date range.
    
    Useful for pre-generating daily tasks for monthly or weekly views
    to minimize database queries.
    
    Args:
        user_id (int): User's database ID
        start_date (date): Start of date range (inclusive)
        end_date (date): End of date range (inclusive)
    """
    current = start_date
    while current <= end_date:
        ensure_daily_tasks(user_id, current)
        current += timedelta(days=1)