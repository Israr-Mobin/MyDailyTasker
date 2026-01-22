"""
Badge Award System
==================
Handles the logic for awarding achievement badges to users based on their progress.

Badges include:
- First Step: Complete your first task
- 7-Day Streak: Maintain a 7-day completion streak
- Perfect Week: Complete 100% of tasks in a week
- Consistency: Maintain a 30-day streak
"""

from models import db, Badge


def award_badges(user_id, stats):
    """
    Award badges to user based on their statistics.
    
    Args:
        user_id (int): User's database ID
        stats (dict): Dictionary containing:
            - total_completed: Total number of tasks completed all-time
            - current_streak: Current consecutive day streak
            - weekly_percent: This week's completion percentage
    
    The function checks if badges have already been earned to avoid duplicates.
    """
    # Get all badges user has already earned
    earned = {
        b.name for b in Badge.query.filter_by(user_id=user_id).all()
    }

    def award(name):
        """Helper function to award a badge if not already earned."""
        if name not in earned:
            db.session.add(Badge(user_id=user_id, name=name))

    # Award badges based on criteria
    if stats["total_completed"] >= 1:
        award("First Step")

    if stats["current_streak"] >= 7:
        award("7-Day Streak")

    if stats["weekly_percent"] == 100:
        award("Perfect Week")

    if stats["current_streak"] >= 30:
        award("Consistency")

    db.session.commit()