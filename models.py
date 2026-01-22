"""
Database Models for Daily Tasker
=================================
Defines all database models and relationships for the application.

Models:
- User: User accounts with authentication and preferences
- Category: Task categories for organization
- Task: User's master task list
- DailyTask: Daily instances of tasks with completion tracking
- Badge: Achievement badges earned by users
- ShareToken: Time-limited tokens for sharing PDF exports
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import date, time, datetime, timedelta
import secrets

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """
    User account model.
    
    Stores user credentials, preferences, and reminder settings.
    Implements Flask-Login UserMixin for authentication support.
    """
    __tablename__ = "user"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)

    # Theme preference 
    theme = db.Column(db.String(20), default='theme-light', nullable=False)

    # Email reminder settings
    reminders_enabled = db.Column(db.Boolean, default=False, nullable=False)
    reminder_time = db.Column(db.Time, nullable=True)
    last_reminder_sent = db.Column(db.Date, nullable=True)

    # Relationships
    tasks = db.relationship("Task", backref="user", cascade="all, delete-orphan")
    categories = db.relationship("Category", backref="user", cascade="all, delete-orphan")
    daily_tasks = db.relationship("DailyTask", backref="user", cascade="all, delete-orphan")
    badges = db.relationship("Badge", backref="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email}>"


class Category(db.Model):
    """
    Task category model.
    
    Organizes tasks into logical groups (e.g., Work, Personal, Health).
    Each user can have multiple categories with unique names.
    """
    __tablename__ = "category"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Relationships
    tasks = db.relationship("Task", backref="category", cascade="all, delete-orphan")

    # Ensure unique category names per user
    __table_args__ = (
        db.UniqueConstraint("user_id", "name", name="uq_user_category"),
    )

    def __repr__(self):
        return f"<Category {self.name}>"


class Task(db.Model):
    """
    Master task model.
    
    Stores the user's recurring tasks that appear daily.
    Each task belongs to one category and can have an optional duration.
    """
    __tablename__ = "task"
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    duration = db.Column(db.String(50), nullable=True)  # e.g., "30m", "1h", or time format
    
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    category_id = db.Column(
        db.Integer,
        db.ForeignKey("category.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Relationships
    daily_tasks = db.relationship(
        "DailyTask",
        backref="task",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    def __repr__(self):
        return f"<Task {self.title}>"


class DailyTask(db.Model):
    """
    Daily task instance model.
    
    Tracks completion status of tasks on specific dates.
    Generated automatically for each date the user views.
    """
    __tablename__ = "daily_task"
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=date.today, index=True)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    task_id = db.Column(
        db.Integer,
        db.ForeignKey("task.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Composite index for efficient queries
    __table_args__ = (
        db.Index("ix_daily_task_user_date", "user_id", "date"),
    )

    def __repr__(self):
        return f"<DailyTask {self.task_id} on {self.date}>"


class Badge(db.Model):
    """
    Achievement badge model.
    
    Stores badges earned by users for various achievements
    (e.g., first task, 7-day streak, perfect week).
    """
    __tablename__ = "badge"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Prevent duplicate badges
    __table_args__ = (
        db.UniqueConstraint("user_id", "name", name="uq_user_badge"),
    )

    def __repr__(self):
        return f"<Badge {self.name} - User {self.user_id}>"


class ShareToken(db.Model):
    """
    PDF sharing token model.
    
    Generates time-limited tokens for sharing PDF exports publicly.
    Tokens expire after a configurable period (default 7 days).
    """
    __tablename__ = "share_token"
    
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(64), unique=True, nullable=False, index=True)
    pdf_type = db.Column(db.String(20), nullable=False)  # "year", "month", or "week"
    expires_at = db.Column(db.DateTime, nullable=False, index=True)
    
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Optional fields based on PDF type
    year = db.Column(db.Integer, nullable=True)
    month = db.Column(db.Integer, nullable=True)
    start_date = db.Column(db.Date, nullable=True)

    @staticmethod
    def create(user_id, pdf_type, expires_in_days=7, **kwargs):
        """
        Factory method to create a new share token.
        
        Args:
            user_id: ID of the user creating the share
            pdf_type: Type of PDF ("year", "month", "week")
            expires_in_days: Number of days until token expires
            **kwargs: Additional fields (year, month, start_date)
        
        Returns:
            ShareToken: New token instance (not yet committed to DB)
        """
        return ShareToken(
            token=secrets.token_urlsafe(32),
            user_id=user_id,
            pdf_type=pdf_type,
            expires_at=datetime.utcnow() + timedelta(days=expires_in_days),
            **kwargs
        )

    def __repr__(self):
        return f"<ShareToken {self.token[:8]}... - {self.pdf_type}>"