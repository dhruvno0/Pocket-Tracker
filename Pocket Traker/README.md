# 💰 Pocket Expense Tracker

A smart, production-ready expense tracking web application built with Flask. Track your income, expenses, and budgets with intelligent insights and beautiful analytics.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

- 🔐 **Secure Authentication** - User registration and login with bcrypt encryption
- 💸 **Transaction Management** - Add income and expenses with categories
- 📊 **Interactive Dashboard** - Real-time financial overview with charts
- 🎯 **Budget Tracking** - Set monthly limits with smart alerts
- 📱 **Mobile Responsive** - Perfect experience on all devices
- 🧠 **Smart Insights** - AI-like spending pattern analysis
- 📈 **Analytics & Reports** - Detailed financial analytics with Chart.js

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd pocket-tracker
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize database**
   ```bash
   python init_db.py
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   ```
   http://localhost:5000
   ```

## 🏗️ Tech Stack

- **Backend**: Python Flask with Blueprint architecture
- **Database**: SQLite (PostgreSQL-ready design)
- **Frontend**: HTML5, CSS3, Bootstrap 5
- **Charts**: Chart.js for interactive visualizations
- **Authentication**: Flask sessions with bcrypt password hashing

## 📱 Screenshots

### Dashboard
- Real-time financial overview
- Interactive expense charts
- Smart spending insights
- Quick action buttons

### Transaction Management
- Easy income/expense entry
- Category-based organization
- Payment mode tracking
- Transaction history

### Budget Management
- Monthly budget limits
- Real-time spending tracking
- Visual progress indicators
- Over-budget alerts

### Analytics
- Monthly trend analysis
- Category-wise breakdowns
- Financial health scoring
- Savings rate tracking

## 🎯 Core Features

### Transaction Management
- Add income and expenses with detailed information
- Categorize transactions (Food, Travel, Rent, Shopping, etc.)
- Multiple payment modes (UPI, Card, Cash, Bank Transfer)
- Add descriptions and notes
- Date-based organization

### Budget Control
- Set monthly limits for each category
- Real-time spending tracking
- Visual progress bars with color coding
- Smart alerts when approaching limits
- Over-budget notifications

### Smart Analytics
- Monthly income vs expense trends
- Category-wise spending analysis
- Financial health scoring
- Savings rate calculations
- Spending pattern insights

### Intelligent Insights
- "Your food expenses increased by 20% this month"
- "You exceeded Shopping budget by ₹500"
- "Great job! You reduced expenses by 15%"
- Personalized spending tips
- Budget recommendations

## 🔒 Security Features

- **Password Security**: bcrypt hashing with salt
- **Session Management**: Secure session cookies
- **CSRF Protection**: Flask-WTF form protection
- **Input Validation**: Server-side validation for all inputs
- **SQL Injection Prevention**: Parameterized queries
- **XSS Protection**: Template auto-escaping

## 📊 Database Schema

### Users
- User authentication and profile information
- Secure password storage with bcrypt

### Categories
- Predefined and custom expense categories
- Icon support for visual identification

### Transactions
- Income and expense records
- Category and payment mode tracking
- Date-based organization

### Budgets
- Monthly spending limits per category
- User-specific budget management

## 🎨 User Interface

- **Mobile-First Design**: Optimized for smartphones
- **Bootstrap 5**: Modern, responsive components
- **Interactive Charts**: Chart.js visualizations
- **Clean Layout**: Intuitive navigation and design
- **Color-Coded Elements**: Visual spending indicators

## 🚀 Deployment

### Local Development
```bash
python app.py
# Runs on http://localhost:5000
```

### Production Deployment

**Heroku**
```bash
# Create Procfile
echo "web: python app.py" > Procfile

# Deploy
heroku create your-app-name
git push heroku main
```

**Railway**
```bash
railway login
railway init
railway up
```

**Docker**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

## 📁 Project Structure

```
pocket-tracker/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── models.py              # Database models
├── auth.py                # Authentication routes
├── main.py                # Main application routes
├── insights.py            # Smart insights engine
├── init_db.py             # Database initialization
├── requirements.txt       # Dependencies
├── static/
│   ├── css/style.css      # Custom styles
│   └── js/app.js          # JavaScript functionality
└── templates/
    ├── base.html          # Base template
    ├── auth/              # Login/signup pages
    └── main/              # Dashboard, analytics, etc.
```

## 🔧 Configuration

### Environment Variables
```bash
FLASK_ENV=production
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///pocket_tracker.db
```

### Development vs Production
- **Development**: Debug mode, detailed errors
- **Production**: Secure cookies, environment secrets

## 🧪 Testing

```bash
# Run application tests
python test_app.py

# Test database operations
python -c "from models import Database; Database().init_db(); print('Database OK')"
```

## 🔮 Future Enhancements

### Planned Features
- [ ] Export data (CSV, PDF)
- [ ] Recurring transactions
- [ ] Mobile app (React Native)
- [ ] Bank API integration
- [ ] Multi-currency support
- [ ] Investment tracking
- [ ] Tax calculations
- [ ] Family expense sharing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Flask framework for the robust backend
- Bootstrap for the responsive UI components
- Chart.js for beautiful data visualizations
- bcrypt for secure password hashing

## 📞 Support

If you encounter any issues or have questions:

1. Check the troubleshooting section in `SETUP.md`
2. Review the project documentation
3. Open an issue on GitHub

---

**Built with ❤️ for smart expense management**