"""
Dashboard Statistics Calculator
================================
Efficiently calculates daily, weekly, and monthly completion percentages
for the dashboard view.

Uses optimized queries to minimize database calls.
"""

from datetime import timedelta, date
from models import DailyTask
from utils.tasks import ensure_daily_tasks_range
import calendar


def get_dashboard_stats(user_id, selected_date):
    """
    Calculate completion statistics for dashboard display.
    
    Fetches all necessary data in a single query and processes it
    to compute daily, weekly, and monthly completion percentages.
    
    Args:
        user_id (int): User's database ID
        selected_date (date): Date to calculate stats for
    
    Returns:
        dict: Statistics containing:
            - daily_percent: Completion % for selected date
            - weekly_percent: Completion % for current week
            - monthly_percent: Completion % for current month
            - monthly_total: Total tasks in month
            - monthly_completed: Completed tasks in month
    """
    # Calculate month boundaries
    month_start = date(selected_date.year, selected_date.month, 1)
    month_end = date(
        selected_date.year,
        selected_date.month,
        calendar.monthrange(selected_date.year, selected_date.month)[1]
    )

    # Ensure all daily tasks exist for the month
    ensure_daily_tasks_range(user_id, month_start, month_end)

    # Fetch all daily tasks for the month in one query
    daily_tasks = DailyTask.query.filter(
        DailyTask.user_id == user_id,
        DailyTask.date.between(month_start, month_end)
    ).all()

    # Index tasks by date for efficient lookup
    tasks_by_date = {}
    for task in daily_tasks:
        tasks_by_date.setdefault(task.date, []).append(task)

    # Calculate DAILY completion %
    today_tasks = tasks_by_date.get(selected_date, [])
    daily_completed = sum(t.completed for t in today_tasks)
    daily_percent = (
        round((daily_completed / len(today_tasks)) * 100)
        if today_tasks else 0
    )

    # Calculate WEEKLY completion %
    week_start = selected_date - timedelta(days=selected_date.weekday())
    week_tasks = []
    for i in range(7):
        week_tasks.extend(
            tasks_by_date.get(week_start + timedelta(days=i), [])
        )

    weekly_completed = sum(t.completed for t in week_tasks)
    weekly_percent = (
        round((weekly_completed / len(week_tasks)) * 100)
        if week_tasks else 0
    )

    # Calculate MONTHLY completion %
    monthly_completed = sum(t.completed for t in daily_tasks)
    monthly_percent = (
        round((monthly_completed / len(daily_tasks)) * 100)
        if daily_tasks else 0
    )

    return {
        "daily_percent": daily_percent,
        "weekly_percent": weekly_percent,
        "monthly_percent": monthly_percent,
        "monthly_total": len(daily_tasks),
        "monthly_completed": monthly_completed
    }