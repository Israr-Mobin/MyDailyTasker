"""
Statistics Calculation Utilities
=================================
Helper functions for calculating task completion statistics.

Note: These functions are legacy - dashboard_stats.py provides
more efficient implementations for the dashboard view.
"""

from datetime import timedelta, date
from models import DailyTask
from utils.tasks import ensure_daily_tasks
import calendar


def daily_completion(user_id, date):
    """
    Calculate completion percentage for a single day.
    
    Args:
        user_id (int): User's database ID
        date (date): Date to calculate for
    
    Returns:
        int: Completion percentage (0-100)
    """
    tasks = DailyTask.query.filter_by(
        user_id=user_id,
        date=date
    ).all()

    if not tasks:
        return 0

    completed = sum(1 for t in tasks if t.completed)
    return round((completed / len(tasks)) * 100)


def weekly_completion(user_id, start_date):
    """
    Calculate completion percentage for a week.
    
    Args:
        user_id (int): User's database ID
        start_date (date): Start of week (usually Monday)
    
    Returns:
        int: Completion percentage (0-100)
    """
    total_tasks = 0
    completed_tasks = 0

    for i in range(7):
        current_date = start_date + timedelta(days=i)
        ensure_daily_tasks(user_id, current_date)

        daily_tasks = DailyTask.query.filter_by(
            user_id=user_id,
            date=current_date
        ).all()
        
        total_tasks += len(daily_tasks)
        completed_tasks += sum(1 for t in daily_tasks if t.completed)

    if total_tasks == 0:
        return 0

    return round((completed_tasks / total_tasks) * 100)


def monthly_completion(user_id, year, month):
    """
    Calculate completion statistics for a month.
    
    Args:
        user_id (int): User's database ID
        year (int): Year
        month (int): Month (1-12)
    
    Returns:
        dict: Contains 'completed' count and 'percent'
    """
    start_date = date(year, month, 1)
    end_day = calendar.monthrange(year, month)[1]

    total_tasks = 0
    completed_tasks = 0

    for day in range(1, end_day + 1):
        current_date = date(year, month, day)
        ensure_daily_tasks(user_id, current_date)

        daily_tasks = DailyTask.query.filter_by(
            user_id=user_id,
            date=current_date
        ).all()

        total_tasks += len(daily_tasks)
        completed_tasks += sum(1 for t in daily_tasks if t.completed)

    if total_tasks == 0:
        percent = 0
    else:
        percent = round((completed_tasks / total_tasks) * 100)

    return {
        "completed": completed_tasks,
        "percent": percent
    }