# Daily Tasker 📋

A modern, minimalist daily task management application built with Flask. Track your recurring tasks, monitor your progress, and build consistent habits with streaks and achievements.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0+-green.svg)

## ✨ Features

### 🎯 Core Functionality
- **Daily Task Tracking**: Create recurring tasks and track completion daily
- **Category Organization**: Organize tasks into custom categories (Work, Personal, Health, etc.)
- **Progress Monitoring**: Real-time daily, weekly, and monthly completion percentages
- **Streak Tracking**: Monitor consecutive days of task completion
- **Achievement Badges**: Earn badges for milestones (First Step, 7-Day Streak, Perfect Week, etc.)

### 📊 Advanced Features
- **PDF Export**: Generate beautiful PDF reports (weekly, monthly, yearly)
- **Shareable Links**: Create time-limited share links for PDF exports
- **Email Reminders**: Optional daily email notifications for your tasks
- **Light/Dark Theme**: Toggle between themes with **cross-device sync**
- **Mobile Responsive**: Fully optimized for mobile and desktop use

### 👤 User Experience
- **User Profile**: View and edit your name, email, and password
- **First-Time Tutorial**: Interactive guide for new users
- **Today Button**: Quick navigation back to current date from any date
- **Long-press Delete**: Easy task deletion on mobile and desktop
- **Daily Tasker Branding**: Clean, professional login/register pages

### 🔒 Security Features
- **Rate Limiting**: Protection against brute force attacks
- **Input Validation**: XSS prevention and sanitization
- **Security Headers**: XSS, clickjacking, and content-type protection
- **Password Hashing**: Secure password storage with Werkzeug
- **Session Management**: Secure sessions with Flask-Login

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Israr-Mobin/daily-tasker.git
cd daily-tasker
```

2. **Create a virtual environment**
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your settings
```

5. **Run the application**
```bash
python app.py
```

6. **Open in browser**
```
http://localhost:5000
```

## 📁 Project Structure

```
daily-tasker/
├── app.py                 # Main Flask application
├── models.py              # Database models
├── requirements.txt       # Python dependencies
├── Procfile               # Deployment configuration
├── runtime.txt            # Python version
├── .env.example           # Environment template
├── .gitignore             # Git ignore rules
├── LICENSE                # MIT License
├── README.md              # This file
│
├── templates/             # HTML templates
│   ├── dashboard.html     # Main dashboard (profile, tutorial, today button)
│   ├── login.html         # Login page with branding
│   ├── register.html      # Registration page with branding
│   └── share_link.html    # Share PDF page
│
├── static/                # Static assets
│   ├── css/
│   │   └── main.css       # Styles, themes, today button
│   └── js/
│       └── main.js        # Theme sync, tutorial, modals
│
├── utils/                 # Utility modules
│   ├── __init__.py
│   ├── badges.py          # Achievement system
│   ├── dashboard_stats.py # Statistics calculation
│   ├── email.py           # Email reminder system
│   ├── stats.py           # Legacy stats functions
│   ├── streaks.py         # Streak calculation
│   └── tasks.py           # Daily task management
│
└── pdf/                   # PDF generation
    ├── __init__.py
    └── pdf_generator.py   # PDF export functionality
```

## 🎮 Usage

### Getting Started

1. **Register an Account**
   - Click "Create an account" on the login page
   - Enter your name, email, and password (min 8 characters)
   - Default categories are created automatically
   - First-time tutorial guides you through the app

2. **Add Your First Task**
   - Click the floating "+" button
   - Select "Add Task"
   - Enter task name, optional duration, and choose a category

3. **Track Your Progress**
   - Check off tasks as you complete them
   - Click "Save Progress" to update
   - View your daily, weekly, and monthly stats

### User Profile

Access your profile from the menu (⋮):
- **View/Edit Name**: Change your display name
- **Change Email**: Update your email address
- **Change Password**: Update your password (requires current password)

### Theme Switching

1. Click the menu (⋮) → Themes
2. Select Light or Dark
3. Theme syncs across all your devices automatically!

### Navigation

- **Arrow Buttons**: Navigate between days
- **Today Button**: Appears when viewing past/future dates - click to return to today

### Deleting Tasks

- **Desktop**: Right-click on a task → Confirm deletion
- **Mobile**: Long-press (600ms) on a task → Confirm deletion

### Exporting PDFs

1. Click "Export PDF" in the top bar
2. Select which categories to include
3. Choose export type: Weekly, Monthly, or Yearly

### Email Reminders (Optional)

1. Click the menu (⋮) → Settings
2. Enable "Daily reminders"
3. Set your preferred reminder time
4. Save settings

## 🏆 Achievements

Earn badges by completing these milestones:
- **First Step**: Complete your first task
- **7-Day Streak**: Maintain a 7-day completion streak
- **Perfect Week**: Complete 100% of tasks in a week
- **Consistency**: Maintain a 30-day streak

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Flask secret key | Yes |
| `FLASK_ENV` | Environment (development/production) | Yes |
| `DATABASE_URL` | PostgreSQL URL (auto-set by Railway/Render) | Production |
| `MAIL_SERVER` | SMTP server | For email |
| `MAIL_PORT` | SMTP port (usually 587) | For email |
| `MAIL_USERNAME` | Email username | For email |
| `MAIL_PASSWORD` | Email app password | For email |
| `MAIL_FROM` | From email address | For email |

### Generate SECRET_KEY

```python
python -c "import secrets; print(secrets.token_hex(32))"
```

## 🚀 Deployment

### Deploy to Railway (Recommended)

1. Create account at [railway.app](https://railway.app)
2. Create new project → Deploy from GitHub
3. Add PostgreSQL database
4. Set environment variables:
   - `SECRET_KEY` (generate new one!)
   - `FLASK_ENV=production`
5. Deploy!

### Deploy to Render

1. Create account at [render.com](https://render.com)
2. Create new Web Service from GitHub
3. Add PostgreSQL database
4. Set environment variables
5. Deploy!

See `docs/DEPLOYMENT_GUIDE.md` for detailed instructions.

## 📦 Dependencies

- **Flask 3.0**: Web framework
- **Flask-SQLAlchemy**: Database ORM
- **Flask-Login**: User authentication
- **Flask-Limiter**: Rate limiting
- **APScheduler**: Background tasks
- **ReportLab**: PDF generation
- **Gunicorn**: Production server
- **psycopg2-binary**: PostgreSQL support

## 🤝 Contributing

Contributions are welcome! See `docs/CONTRIBUTING.md` for guidelines.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Israr Mobin**
- GitHub: [@Israr-Mobin](https://github.com/Israr-Mobin)
- Email: israrmobin@gmail.com

## 🙏 Acknowledgments

- Flask documentation and community
- ReportLab for PDF generation
- All contributors and users

---

**Built with ❤️ using Flask**
