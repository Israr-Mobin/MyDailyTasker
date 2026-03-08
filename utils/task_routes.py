"""
Task Management Routes - APPROACH A (FINAL)
============================================
Simplified routes using DailyTask historical snapshots.

With Approach A:
- Deleting a task just removes it from Task table
- Historical DailyTask records remain forever
- No complex date-based filtering needed
- "Recently Deleted" shows tasks from Task table
"""

from flask import request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import db, Task
from datetime import datetime, timedelta


# ====================
# TASK DELETION ROUTES
# ====================

def soft_delete_task_route():
    """
    Soft delete a task (move to Recently Deleted).
    
    The task will no longer appear in future dates, but all
    historical DailyTask records are preserved.
    
    Route: POST /task/soft-delete
    """
    task_id = request.form.get("task_id")
    
    if not task_id:
        flash("Invalid task ID")
        return redirect(url_for("dashboard"))
    
    task = Task.query.filter_by(
        id=task_id,
        user_id=current_user.id
    ).first()
    
    if not task:
        flash("Task not found")
        return redirect(url_for("dashboard"))
    
    # Soft delete
    task.soft_delete()
    db.session.commit()
    
    flash(f"Task '{task.title}' removed. Past progress preserved! Restore from menu within {current_user.deleted_tasks_retention} days.")
    return redirect(url_for("dashboard"))


def restore_task_route():
    """
    Restore a soft-deleted task.
    
    Route: POST /task/restore
    """
    task_id = request.form.get("task_id")
    
    if not task_id:
        flash("Invalid task ID")
        return redirect(url_for("dashboard"))
    
    task = Task.query.filter_by(
        id=task_id,
        user_id=current_user.id
    ).first()
    
    if not task:
        flash("Task not found")
        return redirect(url_for("dashboard"))
    
    if task.deleted_at is None:
        flash("Task is already active")
        return redirect(url_for("dashboard"))
    
    # Restore
    task.restore()
    db.session.commit()
    
    flash(f"Task '{task.title}' restored!")
    return redirect(url_for("dashboard"))


def permanently_delete_task_route():
    """
    Permanently delete a task from Task table.
    
    NOTE: DailyTask records are preserved via SET NULL constraint.
    Historical data remains intact even after permanent deletion.
    
    Route: POST /task/permanent-delete
    """
    task_id = request.form.get("task_id")
    
    if not task_id:
        flash("Invalid task ID")
        return redirect(url_for("dashboard"))
    
    task = Task.query.filter_by(
        id=task_id,
        user_id=current_user.id
    ).first()
    
    if not task:
        flash("Task not found")
        return redirect(url_for("dashboard"))
    
    task_title = task.title
    
    # Permanently delete from Task table
    # DailyTask.task_id becomes NULL (SET NULL constraint)
    # DailyTask snapshot fields preserve all data
    db.session.delete(task)
    db.session.commit()
    
    flash(f"Task '{task_title}' permanently deleted. Historical progress still visible on past dates.")
    return redirect(url_for("dashboard"))


def get_deleted_tasks_route():
    """
    Get recently deleted tasks (Recently Deleted feature).
    
    Route: GET /tasks/deleted
    Returns: JSON list
    """
    retention_days = current_user.deleted_tasks_retention or 7
    
    deleted_tasks = Task.get_deleted_tasks(current_user.id, retention_days)
    
    tasks_data = []
    for task in deleted_tasks:
        days_ago = (datetime.utcnow() - task.deleted_at).days
        days_left = retention_days - days_ago
        
        tasks_data.append({
            'id': task.id,
            'title': task.title,
            'category': task.category.name,
            'deleted_at': task.deleted_at.strftime('%Y-%m-%d %H:%M'),
            'days_until_permanent': max(0, days_left)
        })
    
    return jsonify(tasks_data)


def update_retention_settings_route():
    """
    Update retention period for deleted tasks.
    
    Route: POST /settings/retention
    """
    retention = request.form.get("retention", type=int)
    
    if retention not in [7, 30]:
        flash("Invalid retention period")
        return redirect(url_for("dashboard"))
    
    current_user.deleted_tasks_retention = retention
    db.session.commit()
    
    flash(f"Deleted tasks kept for {retention} days")
    return redirect(url_for("dashboard"))


# ====================
# CLEANUP BACKGROUND JOB
# ====================

def cleanup_expired_deleted_tasks():
    """
    Background job to permanently delete expired tasks from Task table.
    
    DailyTask records are NEVER deleted - they're permanent history.
    
    Add to scheduler:
        scheduler.add_job(
            cleanup_expired_deleted_tasks,
            trigger="interval",
            hours=24,
            id="cleanup_deleted_tasks"
        )
    """
    from models import User, Task
    from datetime import datetime, timedelta
    
    users = User.query.all()
    total_cleaned = 0
    
    for user in users:
        retention = user.deleted_tasks_retention or 7
        cutoff = datetime.utcnow() - timedelta(days=retention)
        
        # Find expired deleted tasks
        expired = Task.query.filter(
            Task.user_id == user.id,
            Task.deleted_at.isnot(None),
            Task.deleted_at < cutoff
        ).all()
        
        # Permanently delete from Task table
        for task in expired:
            db.session.delete(task)
            total_cleaned += 1
    
    if total_cleaned > 0:
        db.session.commit()
        print(f"🗑️  Cleaned up {total_cleaned} expired tasks from Task table")
        print(f"   (DailyTask historical records preserved)")
