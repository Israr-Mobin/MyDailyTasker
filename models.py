"""
Database Models - WITH created_at FOR PROPER HISTORY
=====================================================
Added created_at to Task to track when tasks were created.
This ensures tasks only appear from their creation date forward.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import date, time, datetime, timedelta
import secrets

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User account model."""
    __tablename__ = "user"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)

    # Theme preference
    theme = db.Column(db.String(20), default='theme-light', nullable=False)
    auto_theme = db.Column(db.Boolean, default=False, nullable=False)

    # Email reminder settings
    reminders_enabled = db.Column(db.Boolean, default=False, nullable=False)
    reminder_time = db.Column(db.Time, nullable=True)
    last_reminder_sent = db.Column(db.Date, nullable=True)

    # Deleted tasks retention period (in days)
    deleted_tasks_retention = db.Column(db.Integer, default=7, nullable=False)
    
    # Rest day for streak recovery (0=Monday, 6=Sunday)
    rest_day_of_week = db.Column(db.Integer, default=6, nullable=False)

    # Relationships
    tasks = db.relationship("Task", backref="user", cascade="all, delete-orphan")
    categories = db.relationship("Category", backref="user", cascade="all, delete-orphan")
    daily_tasks = db.relationship("DailyTask", backref="user", cascade="all, delete-orphan")
    badges = db.relationship("Badge", backref="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email}>"


class Category(db.Model):
    """Task category model."""
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

    __table_args__ = (
        db.UniqueConstraint("user_id", "name", name="uq_user_category"),
    )

    def __repr__(self):
        return f"<Category {self.name}>"


class Task(db.Model):
    """
    Master task template with creation tracking.
    
    IMPORTANT CHANGE:
    - created_at: Tracks when the task was created
    - Task only appears on dates >= created_at.date()
    - This ensures new tasks don't appear on past dates
    """
    __tablename__ = "task"
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    duration = db.Column(db.String(50), nullable=True)
    
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
    
    # CRITICAL: When was this task created?
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Soft delete field (for "Recently Deleted" feature)
    deleted_at = db.Column(db.DateTime, nullable=True, index=True)
    
    # Relationships
    daily_tasks = db.relationship(
        "DailyTask",
        backref="task",
        foreign_keys="DailyTask.task_id"
    )

    def soft_delete(self):
        """Soft delete - mark for Recently Deleted."""
        self.deleted_at = datetime.utcnow()
    
    def restore(self):
        """Restore from Recently Deleted."""
        self.deleted_at = None
    
    @property
    def is_deleted(self):
        """Check if task is in Recently Deleted."""
        return self.deleted_at is not None
    
    @property
    def created_date(self):
        """Get the date this task was created (without time)."""
        return self.created_at.date()
    
    def was_active_on_date(self, check_date):
        """
        Check if this task should appear on a specific date.
        
        Task appears if:
        1. It was created on or before that date (created_at.date() <= check_date)
        2. It wasn't deleted yet (deleted_at is None OR deleted_at.date() > check_date)
        
        Args:
            check_date: Date to check
            
        Returns:
            bool: True if task should appear on this date
        """
        # Task must have been created by this date
        if self.created_date > check_date:
            return False
        
        # If not deleted, it's active
        if self.deleted_at is None:
            return True
        
        # If deleted, check if deletion happened after this date
        deleted_date = self.deleted_at.date()
        return check_date < deleted_date
    
    @staticmethod
    def get_active_tasks(user_id):
        """Get all currently active (non-deleted) tasks for a user."""
        return Task.query.filter_by(user_id=user_id, deleted_at=None).all()
    
    @staticmethod
    def get_active_tasks_for_date(user_id, check_date):
        """
        Get tasks that should appear on a specific date.
        
        Args:
            user_id: User's database ID
            check_date: Date to get tasks for
            
        Returns:
            List of Task objects that were active on that date
        """
        # Get all tasks for user
        all_tasks = Task.query.filter_by(user_id=user_id).all()
        
        # Filter to tasks that should appear on this date
        return [t for t in all_tasks if t.was_active_on_date(check_date)]
    
    @staticmethod
    def get_deleted_tasks(user_id, retention_days=7):
        """Get recently deleted tasks (for Recently Deleted feature)."""
        cutoff = datetime.utcnow() - timedelta(days=retention_days)
        return Task.query.filter(
            Task.user_id == user_id,
            Task.deleted_at.isnot(None),
            Task.deleted_at > cutoff
        ).all()

    def __repr__(self):
        return f"<Task {self.title}>"


class DailyTask(db.Model):
    """
    Daily task instance - THE PERMANENT HISTORICAL RECORD.
    
    These records are NEVER deleted.
    They preserve the complete history of what happened each day.
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
    
    # Task reference (nullable because Task might be deleted)
    task_id = db.Column(
        db.Integer,
        db.ForeignKey("task.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Snapshot fields - preserve data even if Task/Category deleted
    task_title = db.Column(db.String(200), nullable=False)
    task_duration = db.Column(db.String(50), nullable=True)
    category_name = db.Column(db.String(50), nullable=False)

    __table_args__ = (
        db.Index("ix_daily_task_user_date", "user_id", "date"),
    )

    def __repr__(self):
        return f"<DailyTask '{self.task_title}' on {self.date}>"


class Badge(db.Model):
    """Achievement badge model."""
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

    __table_args__ = (
        db.UniqueConstraint("user_id", "name", name="uq_user_badge"),
    )

    def __repr__(self):
        return f"<Badge {self.name} - User {self.user_id}>"


class ShareToken(db.Model):
    """PDF sharing token model."""
    __tablename__ = "share_token"
    
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(64), unique=True, nullable=False, index=True)
    pdf_type = db.Column(db.String(20), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False, index=True)
    
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False
    )
    
    year = db.Column(db.Integer, nullable=True)
    month = db.Column(db.Integer, nullable=True)
    start_date = db.Column(db.Date, nullable=True)

    @staticmethod
    def create(user_id, pdf_type, expires_in_days=7, **kwargs):
        return ShareToken(
            token=secrets.token_urlsafe(32),
            user_id=user_id,
            pdf_type=pdf_type,
            expires_at=datetime.utcnow() + timedelta(days=expires_in_days),
            **kwargs
        )

    def __repr__(self):
        return f"<ShareToken {self.token[:8]}... - {self.pdf_type}>"


class Quote(db.Model):
    """Motivational quote model."""
    __tablename__ = "quote"
    
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    author = db.Column(db.String(100), nullable=True)
    category = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    @staticmethod
    def get_daily_quote(selected_date=None):
        """Get quote of the day using deterministic selection."""
        if selected_date is None:
            selected_date = date.today()
        
        total_quotes = Quote.query.count()
        if total_quotes == 0:
            return None
        
        day_seed = (selected_date.year * 10000 + 
                   selected_date.month * 100 + 
                   selected_date.day)
        quote_index = day_seed % total_quotes
        
        return Quote.query.offset(quote_index).first()

    def __repr__(self):
        return f"<Quote by {self.author or 'Unknown'}>"