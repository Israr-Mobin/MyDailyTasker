"""
Daily Task Management - WITH PROPER HISTORY TRACKING
=====================================================
Uses Task.created_at to ensure tasks only appear from creation date forward.
"""

from datetime import date, timedelta
from models import db, Task, DailyTask, Category


def ensure_daily_tasks(user_id, selected_date):
    """
    Ensure DailyTask records exist for tasks that should appear on this date.
    
    CRITICAL: Only creates DailyTask for tasks that:
    1. Were created on or before selected_date (created_at.date() <= selected_date)
    2. Are not deleted, OR were deleted after selected_date
    
    Args:
        user_id (int): User's database ID
        selected_date (date): Date to ensure tasks for
    """
    # Get tasks that should appear on this date
    tasks = Task.get_active_tasks_for_date(user_id, selected_date)

    # Get existing daily tasks for this date
    existing_task_ids = {
        dt.task_id
        for dt in DailyTask.query.filter_by(
            user_id=user_id,
            date=selected_date
        ).all()
        if dt.task_id is not None
    }

    # Create missing daily tasks with snapshot data
    for task in tasks:
        if task.id not in existing_task_ids:
            daily = DailyTask(
                user_id=user_id,
                task_id=task.id,
                date=selected_date,
                completed=False,
                # SNAPSHOT FIELDS
                task_title=task.title,
                task_duration=task.duration,
                category_name=task.category.name
            )
            db.session.add(daily)

    db.session.commit()


def ensure_daily_tasks_range(user_id, start_date, end_date):
    """
    Ensure DailyTask records exist for a date range.
    
    Args:
        user_id (int): User's database ID
        start_date (date): Start of range (inclusive)
        end_date (date): End of range (inclusive)
    """
    current = start_date
    while current <= end_date:
        ensure_daily_tasks(user_id, current)
        current += timedelta(days=1)


