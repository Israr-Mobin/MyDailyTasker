"""
PDF Report Generator
====================
Generates visually appealing PDF reports for task tracking data.

This module creates three types of PDF reports:
1. Yearly - All 12 months in a calendar view
2. Monthly - Single month in a calendar view
3. Weekly - 7 days in a detailed grid view

Features:
- Color-coded categories for easy visual identification
- Task completion checkmarks
- Duration tracking
- Landscape and portrait layouts optimized for each report type
- Professional styling with reportlab library

Dependencies:
- reportlab: PDF generation library
- calendar: Month/week calculations
- datetime: Date handling
- random: Category color assignment

Author: Daily Tasker Team
Version: 1.0.0
"""

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import calendar
from datetime import datetime, timedelta
import random

# ======================
# CONFIGURATION CONSTANTS
# ======================

# Layout dimensions (in points)
CATEGORY_HEADER_HEIGHT = 16  # Height of category header bars
TASK_ROW_HEIGHT = 12         # Height of individual task rows
BASE_CELL_HEIGHT = 40        # Minimum height for day cells

# Color palette for categories - vibrant but professional
# Each category gets assigned a random color from this palette
CATEGORY_COLORS = [
    colors.HexColor('#3498DB'),  # Bright Blue
    colors.HexColor('#2ECC71'),  # Emerald Green
    colors.HexColor('#E74C3C'),  # Vibrant Red
    colors.HexColor('#9B59B6'),  # Purple
    colors.HexColor('#F39C12'),  # Orange
    colors.HexColor('#1ABC9C'),  # Turquoise
    colors.HexColor('#E67E22'),  # Carrot Orange
    colors.HexColor('#16A085'),  # Dark Turquoise
    colors.HexColor('#C0392B'),  # Dark Red
    colors.HexColor('#8E44AD'),  # Dark Purple
]


# ======================
# STYLE DEFINITIONS
# ======================

def get_styles():
    """
    Create and return all paragraph styles used in PDF generation.
    
    Defines custom styles for:
    - Date headers (day number and name)
    - Category section headers
    - Task text
    - Column headers
    - Page titles
    
    Returns:
        dict: Dictionary mapping style names to ParagraphStyle objects
    """
    styles = getSampleStyleSheet()
    
    # Style for date display in each calendar cell
    date_style = ParagraphStyle(
        'DateStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        alignment=1,  # Center alignment
        spaceAfter=6,
        textColor=colors.darkblue
    )

    # Style for category headers (e.g., "WORK", "PERSONAL")
    section_style = ParagraphStyle(
        'SectionStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        alignment=0,  # Left alignment
        spaceAfter=4,
        spaceBefore=8,
        textColor=colors.white  # White text on colored background
    )

    # Style for task titles and durations
    task_style = ParagraphStyle(
        'TaskStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7,
        leading=8,  # Line height
        alignment=0
    )

    # Style for table column headers
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        alignment=1,  # Center alignment
        textColor=colors.white
    )
    
    return {
        'date': date_style,
        'section': section_style,
        'task': task_style,
        'header': header_style,
        'title': styles['Title']
    }


# ======================
# DATA PREPARATION
# ======================

def get_tasks_and_data(user_id, db, Task, DailyTask, category_ids=None):
    """
    Fetch and organize task data for PDF generation.
    
    Retrieves all tasks for a user and builds lookup structures for:
    - Task completion status by (task_id, date)
    - Tasks grouped by category name
    
    Args:
        user_id (int): User's database ID
        db: SQLAlchemy database instance
        Task: Task model class
        DailyTask: DailyTask model class
        category_ids (list, optional): Filter to specific category IDs
    
    Returns:
        tuple: (tasks, daily_map, category_map) where:
            - tasks: List of Task objects
            - daily_map: Dict mapping (task_id, date) -> bool (completed)
            - category_map: Dict mapping category_name -> [(task_id, title, duration)]
    """
    # Build query with optional category filter
    query = Task.query.filter_by(user_id=user_id)
    if category_ids:
        query = query.filter(Task.category_id.in_(category_ids))
    
    tasks = query.all()
    
    # Build completion status lookup: (task_id, date) -> completed
    daily_map = {
        (dt.task_id, dt.date): dt.completed
        for dt in DailyTask.query.filter_by(user_id=user_id).all()
    }
    
    # Group tasks by category name
    category_map = {}
    for task in tasks:
        category_name = task.category.name
        category_map.setdefault(category_name, []).append(
            (task.id, task.title, task.duration or "")
        )
    
    return tasks, daily_map, category_map


def assign_category_colors(category_map):
    """
    Assign a random color to each category from the color palette.
    
    Shuffles the available colors and assigns them sequentially to categories.
    If there are more categories than colors, colors will be reused.
    
    Args:
        category_map (dict): Dictionary with category names as keys
    
    Returns:
        dict: Mapping of category_name -> Color object
    """
    category_colors = {}
    available_colors = CATEGORY_COLORS.copy()
    random.shuffle(available_colors)
    
    for i, category_name in enumerate(category_map.keys()):
        category_colors[category_name] = available_colors[i % len(available_colors)]
    
    return category_colors


# ======================
# CELL BUILDERS
# ======================

def build_day_cell(date_obj, category_map, daily_map, col_width, styles, category_colors):
    """
    Build a single day cell containing all categories and tasks.
    
    Creates a nested table structure:
    - Date header (day number + day name)
    - For each category:
      - Colored header bar
      - Table with task name, duration, and completion checkmark
    
    Args:
        date_obj (datetime): Date for this cell
        category_map (dict): Tasks grouped by category
        daily_map (dict): Task completion status lookup
        col_width (float): Width of the cell in points
        styles (dict): Paragraph styles
        category_colors (dict): Category color assignments
    
    Returns:
        Table: Reportlab Table object containing the day's content
    """
    # Build date header (e.g., "15\nMon")
    day_name = date_obj.strftime("%A")[:3]  # First 3 letters of day name
    date_text = f"{date_obj.day}<br/>{day_name}"
    date_cell = Paragraph(date_text, styles['date'])
    
    day_sections = []
    
    # Build each category section
    for category_name, category_tasks in category_map.items():
        category_color = category_colors[category_name]
        
        # Category header with background color
        category_header = Paragraph(
            f"<b>{category_name.upper()}</b>", 
            styles['section']
        )
        category_header_table = Table([[category_header]], colWidths=[col_width - 10])
        category_header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), category_color),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        day_sections.append([category_header_table])
        
        # Task table with header row
        category_table_data = [[
            Paragraph("<b>Task</b>", styles['task']),
            Paragraph("<b>Time</b>", styles['task']),
            Paragraph("<b>✓</b>", styles['task'])
        ]]
        
        # Add task rows
        for task_id, task_title, time in category_tasks:
            completed = daily_map.get((task_id, date_obj.date()), False)
            check = "✓" if completed else ""
            category_table_data.append([
                Paragraph(task_title, styles['task']),
                Paragraph(time, styles['task']),
                Paragraph(check, styles['task'])
            ])
        
        # Create and style task table
        category_table = Table(
            category_table_data,
            colWidths=[col_width * 0.35, col_width * 0.28, col_width * 0.15]
        )
        
        category_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.95, 0.95, 0.95)),  # Light gray header
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),
            ('LEFTPADDING', (0, 0), (-1, -1), 2),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        
        day_sections.append([category_table])
    
    # Combine date header and all category sections into day cell
    day_cell_data = [[date_cell]] + day_sections
    day_cell_table = Table(day_cell_data, colWidths=[col_width - 10])
    day_cell_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    return day_cell_table


def create_calendar_table(table_data, col_width):
    """
    Create and style the main calendar table.
    
    Applies professional styling to the calendar grid including:
    - Dark header row
    - Grid lines between cells
    - Border around entire table
    - Consistent padding
    
    Args:
        table_data (list): 2D list of table cells
        col_width (float): Width of each column in points
    
    Returns:
        Table: Styled calendar table
    """
    calendar_table = Table(table_data, colWidths=[col_width] * 7)
    
    calendar_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1.5, colors.black),
        ('LINEBEFORE', (1, 0), (6, -1), 0.5, colors.grey),
        ('LINEABOVE', (0, 1), (-1, 6), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),  # Dark blue-gray header
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
    ]))
    
    return calendar_table


# ======================
# PDF GENERATORS
# ======================

def generate_year_pdf(filename, user_id, year, db, Task, DailyTask, category_ids=None):
    """
    Generate a yearly PDF report with all 12 months.
    
    Creates a multi-page PDF with one month per page in landscape orientation.
    Each month is displayed in a calendar grid (Mon-Sun) with all tasks visible.
    
    Args:
        filename (str): Output filename for PDF
        user_id (int): User's database ID
        year (int): Year to generate (e.g., 2024)
        db: SQLAlchemy database instance
        Task: Task model class
        DailyTask: DailyTask model class
        category_ids (list, optional): Filter to specific categories
    
    Returns:
        str: Filename of generated PDF
    
    Layout:
        - Page orientation: Landscape letter (11" x 8.5")
        - One month per page
        - 7 columns (Mon-Sun)
        - Up to 6 rows for weeks
    """
    styles_dict = get_styles()
    tasks, daily_map, category_map = get_tasks_and_data(user_id, db, Task, DailyTask, category_ids)
    category_colors = assign_category_colors(category_map)
    
    story = []  # Reportlab story: list of flowable elements
    doc = SimpleDocTemplate(
        filename, 
        pagesize=landscape(letter), 
        leftMargin=15, 
        rightMargin=15, 
        topMargin=20, 
        bottomMargin=20
    )
    
    # Setup calendar and calculate dimensions
    cal = calendar.Calendar(firstweekday=calendar.MONDAY)
    page_width = 792  # Letter landscape width in points
    available_width = page_width - 30  # Subtract margins
    col_width = available_width / 7
    week_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    
    # Generate each month
    for month in range(1, 13):
        month_name = calendar.month_name[month]
        
        # Month title
        story.append(Paragraph(f"<b>{month_name} {year} - Task Tracker</b>", styles_dict['title']))
        story.append(Spacer(1, 10))
        
        # Build calendar grid
        month_days = cal.monthdayscalendar(year, month)
        table_data = []
        
        # Header row with day names
        header_row = [Paragraph(f"<b>{day}</b>", styles_dict['header']) for day in week_days]
        table_data.append(header_row)
        
        # Week rows
        for week in month_days:
            week_row = []
            for day in week:
                if day == 0:  # Empty cell (day from previous/next month)
                    cell_content = ""
                else:
                    date_obj = datetime(year, month, day)
                    cell_content = build_day_cell(date_obj, category_map, daily_map, col_width, styles_dict, category_colors)
                week_row.append(cell_content)
            table_data.append(week_row)
        
        # Create styled calendar table
        calendar_table = create_calendar_table(table_data, col_width)
        story.append(calendar_table)
        
        # Add page break except for last month
        if month < 12:
            story.append(PageBreak())
            story.append(Spacer(1, 10))
    
    # Build PDF
    doc.build(story)
    return filename


def generate_month_pdf(filename, user_id, year, month, db, Task, DailyTask, category_ids=None):
    """
    Generate a monthly PDF report for a single month.
    
    Creates a one-page PDF showing the entire month in a calendar grid.
    Identical layout to the yearly PDF but for just one month.
    
    Args:
        filename (str): Output filename for PDF
        user_id (int): User's database ID
        year (int): Year (e.g., 2024)
        month (int): Month (1-12)
        db: SQLAlchemy database instance
        Task: Task model class
        DailyTask: DailyTask model class
        category_ids (list, optional): Filter to specific categories
    
    Returns:
        str: Filename of generated PDF
    
    Layout:
        - Page orientation: Landscape letter (11" x 8.5")
        - 7 columns (Mon-Sun)
        - 4-6 rows depending on month
    """
    styles_dict = get_styles()
    tasks, daily_map, category_map = get_tasks_and_data(user_id, db, Task, DailyTask, category_ids)
    category_colors = assign_category_colors(category_map)
    
    story = []
    doc = SimpleDocTemplate(
        filename,
        pagesize=landscape(letter),
        leftMargin=15,
        rightMargin=15,
        topMargin=20,
        bottomMargin=20
    )
    
    # Setup calendar and calculate dimensions
    cal = calendar.Calendar(firstweekday=calendar.MONDAY)
    page_width = 792
    available_width = page_width - 30
    col_width = available_width / 7
    week_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    
    # Month title
    month_name = calendar.month_name[month]
    story.append(Paragraph(f"<b>{month_name} {year} - Task Tracker</b>", styles_dict['title']))
    story.append(Spacer(1, 10))
    
    # Build calendar grid
    month_days = cal.monthdayscalendar(year, month)
    table_data = []
    
    # Header row
    header_row = [Paragraph(f"<b>{day}</b>", styles_dict['header']) for day in week_days]
    table_data.append(header_row)
    
    # Week rows
    for week in month_days:
        week_row = []
        for day in week:
            if day == 0:
                cell_content = ""
            else:
                date_obj = datetime(year, month, day)
                cell_content = build_day_cell(date_obj, category_map, daily_map, col_width, styles_dict, category_colors)
            week_row.append(cell_content)
        table_data.append(week_row)
    
    # Create styled calendar table
    calendar_table = create_calendar_table(table_data, col_width)
    story.append(calendar_table)
    
    # Build PDF
    doc.build(story)
    return filename


def generate_week_pdf(filename, user_id, start_date, db, Task, DailyTask, category_ids=None):
    """
    Generate a weekly PDF report for 7 consecutive days.
    
    Creates a one-page PDF with a 2x4 grid showing Mon-Sun.
    Larger cells than monthly view allow for more detail per day.
    
    Args:
        filename (str): Output filename for PDF
        user_id (int): User's database ID
        start_date (date): Start date (typically Monday)
        db: SQLAlchemy database instance
        Task: Task model class
        DailyTask: DailyTask model class
        category_ids (list, optional): Filter to specific categories
    
    Returns:
        str: Filename of generated PDF
    
    Layout:
        - Page orientation: Portrait letter (8.5" x 11")
        - 4 columns x 2 rows
        - Top row: Mon-Thu
        - Bottom row: Fri-Sun + empty cell
        - Larger cells provide more space for task details
    """
    styles_dict = get_styles()
    tasks, daily_map, category_map = get_tasks_and_data(user_id, db, Task, DailyTask, category_ids)
    category_colors = assign_category_colors(category_map)
    
    story = []
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,  # Portrait orientation
        leftMargin=20,
        rightMargin=20,
        topMargin=30,
        bottomMargin=30
    )
    
    # Title
    story.append(Paragraph(f"<b>Week of {start_date.strftime('%B %d, %Y')}</b>", styles_dict['title']))
    story.append(Spacer(1, 12))
    
    # Calculate column width for 4-column layout
    cols = 4
    col_width = doc.width / cols
    
    # Header rows for each set of days
    header_row_1 = [Paragraph(d, styles_dict['header']) for d in ["Mon", "Tue", "Wed", "Thu"]]
    header_row_2 = [Paragraph(d, styles_dict['header']) for d in ["Fri", "Sat", "Sun", ""]]
    
    # Build day cells
    day_cells = []
    for i in range(7):
        date_obj = start_date + timedelta(days=i)
        date_cell = Paragraph(f"{date_obj.day}<br/>{date_obj.strftime('%A')[:3]}", styles_dict['date'])
        
        day_sections = []
        
        # Build category sections for this day
        for category_name, category_tasks in category_map.items():
            category_color = category_colors[category_name]
            
            # Category header with background color
            category_header = Paragraph(
                f"<b>{category_name.upper()}</b>", 
                styles_dict['section']
            )
            category_header_table = Table([[category_header]], colWidths=[col_width - 10])
            category_header_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), category_color),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ]))
            day_sections.append([category_header_table])
            
            # Task table
            category_table_data = [[
                Paragraph("<b>Task</b>", styles_dict['task']),
                Paragraph("<b>Time</b>", styles_dict['task']),
                Paragraph("<b>✓</b>", styles_dict['task'])
            ]]
            
            for task_id, title, duration in category_tasks:
                completed = daily_map.get((task_id, date_obj), False)
                category_table_data.append([
                    Paragraph(title, styles_dict['task']),
                    Paragraph(duration, styles_dict['task']),
                    Paragraph("✓" if completed else "", styles_dict['task'])
                ])
            
            category_table = Table(
                category_table_data,
                colWidths=[col_width * 0.40, col_width * 0.30, col_width * 0.15]
            )
            
            category_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.95, 0.95, 0.95)),
                ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
                ('FONTSIZE', (0, 0), (-1, -1), 7),
                ('LEFTPADDING', (0, 0), (-1, -1), 2),
                ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ]))
            
            day_sections.append([category_table])
        
        # Combine into day cell
        day_cell = Table([[date_cell]] + day_sections, colWidths=[col_width])
        day_cell.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 2),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        day_cells.append(day_cell)
    
    # Split into two rows: Mon-Thu, Fri-Sun+empty
    row1 = day_cells[:4]
    row2 = day_cells[4:]
    while len(row2) < 4:  # Pad with empty cell
        row2.append(Spacer(1, 1))
    
    # Build final table
    table_data = [header_row_1, row1, header_row_2, row2]
    
    week_table = Table(table_data, colWidths=[col_width] * 4)
    week_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1.5, colors.black),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),  # Dark blue-gray header
        ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#2C3E50')),  # Dark blue-gray header
        ('VALIGN', (0, 1), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0)
    ]))
    
    story.append(week_table)
    
    # Build PDF
    doc.build(story)
    
    return filename