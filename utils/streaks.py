"""
Streak Calculation
==================
Calculates consecutive day streaks for users based on task completion.
"""

from datetime import date, timedelta
from models import DailyTask
from utils.tasks import ensure_daily_tasks


def compute_current_streak(user_id, anchor_date):
    """
    Calculate consecutive day streak ending at anchor_date.
    
    A streak day is counted if the user completed at least one task that day.
    Works backwards from anchor_date until finding a day with no completed tasks.
    
    Args:
        user_id (int): User's database ID
        anchor_date (date): Date to calculate streak from (usually today)
    
    Returns:
        int: Number of consecutive days with at least one completed task
    
    Example:
        If user completed tasks on Mon, Tue, Wed but not Thu,
        and anchor_date is Wed, returns 3.
    """
    streak = 0
    current_date = anchor_date

    while True:
        # Ensure daily tasks exist for this date
        ensure_daily_tasks(user_id, current_date)

        # Get tasks for this date
        tasks = DailyTask.query.filter_by(
            user_id=user_id,
            date=current_date
        ).all()

        # Break if no tasks exist
        if not tasks:
            break

        # Check if at least one task was completed
        if any(t.completed for t in tasks):
            streak += 1
            current_date -= timedelta(days=1)
        else:
            # Streak broken
            break

    return streak