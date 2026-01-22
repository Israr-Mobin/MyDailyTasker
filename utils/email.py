"""
Email Reminder System
=====================
Handles sending daily task reminders via email to users who have
enabled notifications.

Requires SMTP configuration via environment variables.
"""

import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv
from datetime import date, datetime


def build_reminder_email(user, tasks):
    """
    Build email body for task reminder.
    
    Args:
        user: User object
        tasks: List of Task objects
    
    Returns:
        str: Formatted email body
    """
    lines = [
        f"Hello {user.name},",
        "",
        "Here are your tasks for today:",
        ""
    ]

    for task in tasks:
        duration_str = f" ({task.duration})" if task.duration else ""
        lines.append(f"- {task.title}{duration_str}")

    lines.append("")
    lines.append("Have a productive day!")

    return "\n".join(lines)


def is_email_configured():
    """
    Check if email configuration is complete.
    
    Returns:
        bool: True if all required email environment variables are set
    """
    load_dotenv()
    
    required_vars = [
        "MAIL_SERVER",
        "MAIL_PORT",
        "MAIL_USERNAME",
        "MAIL_PASSWORD",
        "MAIL_FROM"
    ]
    
    for var in required_vars:
        if not os.environ.get(var):
            return False
    
    return True


def send_daily_reminders():
    """
    Send email reminders to all eligible users.
    
    Checks for users who:
    - Have reminders enabled
    - Haven't received a reminder today
    - Current time is past their reminder time
    
    This function is called by the background scheduler.
    """
    # Check if email is configured
    if not is_email_configured():
        print("⚠️  Email reminders skipped: SMTP not configured. Set MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD, and MAIL_FROM environment variables.")
        return
    
    from models import User, Task
    from app import db
    
    today = date.today()
    now = datetime.now().time()

    users = User.query.filter_by(reminders_enabled=True).all()

    if not users:
        return  # No users with reminders enabled

    sent_count = 0
    for user in users:
        # Skip if already sent today
        if user.last_reminder_sent == today:
            continue

        # Respect user's preferred reminder time
        if user.reminder_time and now < user.reminder_time:
            continue

        # Get user's tasks
        tasks = Task.query.filter_by(user_id=user.id).all()
        if not tasks:
            continue

        # Build and send email
        body = build_reminder_email(user, tasks)
        try:
            send_email(
                to_email=user.email,
                subject="Your Daily Task Reminder",
                body=body
            )
            
            # Mark as sent
            user.last_reminder_sent = today
            sent_count += 1
        except Exception as e:
            print(f"Failed to send reminder to {user.email}: {e}")

    if sent_count > 0:
        db.session.commit()
        print(f"✅ Sent {sent_count} email reminder(s)")


def send_email(to_email, subject, body):
    """
    Send an email using SMTP.
    
    Requires environment variables:
    - MAIL_SERVER: SMTP server address
    - MAIL_PORT: SMTP port (usually 587)
    - MAIL_USERNAME: SMTP username
    - MAIL_PASSWORD: SMTP password
    - MAIL_FROM: From email address
    
    Args:
        to_email (str): Recipient email address
        subject (str): Email subject
        body (str): Email body text
    
    Raises:
        ValueError: If required environment variables are missing
        smtplib.SMTPException: If email sending fails
    """
    load_dotenv()
    
    # Validate environment variables
    mail_server = os.environ.get("MAIL_SERVER")
    mail_port = os.environ.get("MAIL_PORT")
    mail_username = os.environ.get("MAIL_USERNAME")
    mail_password = os.environ.get("MAIL_PASSWORD")
    mail_from = os.environ.get("MAIL_FROM")
    
    if not all([mail_server, mail_port, mail_username, mail_password, mail_from]):
        raise ValueError(
            "Email configuration incomplete. Required environment variables: "
            "MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD, MAIL_FROM"
        )
    
    try:
        mail_port = int(mail_port)
    except (ValueError, TypeError):
        raise ValueError(f"MAIL_PORT must be a valid integer, got: {mail_port}")
    
    msg = EmailMessage()
    msg["From"] = mail_from
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP(mail_server, mail_port) as server:
        server.starttls()
        server.login(mail_username, mail_password)
        server.send_message(msg)
