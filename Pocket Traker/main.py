from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from datetime import datetime, date
from models import Database, Transaction, Category, Budget
from insights import InsightsEngine
from auth import login_required

main_bp = Blueprint('main', __name__)
db = Database()
transaction_model = Transaction(db)
category_model = Category(db)
budget_model = Budget(db)
insights_engine = InsightsEngine(db)

@main_bp.route('/')
@login_required
def dashboard():
    user_id = session['user_id']
    now = datetime.now()
    
    # Get current month summary
    monthly_summary = transaction_model.get_monthly_summary(user_id, now.year, now.month)
    
    # Get recent transactions
    recent_transactions = transaction_model.get_user_transactions(user_id, limit=10)
    
    # Get category expenses for chart
    category_expenses = transaction_model.get_category_expenses(user_id, now.year, now.month)
    
    # Get insights
    insights = insights_engine.generate_insights(user_id)
    spending_tips = insights_engine.get_spending_tips(user_id)
    
    return render_template('main/dashboard.html',
                         summary=monthly_summary,
                         transactions=recent_transactions,
                         category_expenses=category_expenses,
                         insights=insights,
                         tips=spending_tips,
                         current_month=now.strftime('%B %Y'))

@main_bp.route('/add_transaction', methods=['GET', 'POST'])
@login_required
def add_transaction():
    if request.method == 'POST':
        user_id = session['user_id']
        
        try:
            amount = float(request.form.get('amount', 0))
            trans_type = request.form.get('type')
            category_id = int(request.form.get('category_id'))
            payment_mode = request.form.get('payment_mode')
            description = request.form.get('description', '').strip()
            transaction_date = request.form.get('transaction_date')
            
            # Validation
            if amount <= 0:
                flash('Amount must be greater than 0', 'error')
                return redirect(url_for('main.add_transaction'))
            
            if trans_type not in ['income', 'expense']:
                flash('Invalid transaction type', 'error')
                return redirect(url_for('main.add_transaction'))
            
            if not transaction_date:
                transaction_date = date.today().isoformat()
            
            # Add transaction
            if transaction_model.add_transaction(user_id, amount, trans_type, 
                                               category_id, payment_mode, 
                                               description, transaction_date):
                flash(f'{trans_type.title()} of ₹{amount:.2f} added successfully!', 'success')
                return redirect(url_for('main.dashboard'))
            else:
                flash('Error adding transaction', 'error')
                
        except (ValueError, TypeError):
            flash('Please enter valid values', 'error')
    
    categories = category_model.get_all_categories()
    return render_template('main/add_transaction.html', categories=categories)

@main_bp.route('/transactions')
@login_required
def transactions():
    user_id = session['user_id']
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    all_transactions = transaction_model.get_user_transactions(user_id, limit=per_page * page)
    
    return render_template('main/transactions.html', transactions=all_transactions)

@main_bp.route('/budgets', methods=['GET', 'POST'])
@login_required
def budgets():
    user_id = session['user_id']
    
    if request.method == 'POST':
        try:
            category_id = int(request.form.get('category_id'))
            monthly_limit = float(request.form.get('monthly_limit'))
            
            if monthly_limit <= 0:
                flash('Budget limit must be greater than 0', 'error')
            elif budget_model.set_budget(user_id, category_id, monthly_limit):
                flash('Budget updated successfully!', 'success')
            else:
                flash('Error updating budget', 'error')
                
        except (ValueError, TypeError):
            flash('Please enter valid values', 'error')
    
    categories = category_model.get_all_categories()
    user_budgets = budget_model.get_user_budgets(user_id)
    
    # Get current month spending by category
    now = datetime.now()
    category_spending = transaction_model.get_category_expenses(user_id, now.year, now.month)
    spending_lookup = {cat['name']: cat['total'] for cat in category_spending}
    
    # Create budget lookup with spending data
    budget_lookup = {}
    for budget in user_budgets:
        category_name = next((cat['name'] for cat in categories if cat['id'] == budget['category_id']), '')
        budget['current_spending'] = spending_lookup.get(category_name, 0)
        budget_lookup[budget['category_id']] = budget
    
    return render_template('main/budgets.html', 
                         categories=categories, 
                         budgets=budget_lookup)

@main_bp.route('/analytics')
@login_required
def analytics():
    user_id = session['user_id']
    
    # Get month/year from query params or use current
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', datetime.now().month, type=int)
    
    # Get monthly summary
    monthly_summary = transaction_model.get_monthly_summary(user_id, year, month)
    
    # Get category expenses
    category_expenses = transaction_model.get_category_expenses(user_id, year, month)
    
    # Get last 6 months data for trend chart
    monthly_trends = []
    current_date = datetime(year, month, 1)
    
    for i in range(6):
        month_data = transaction_model.get_monthly_summary(user_id, current_date.year, current_date.month)
        monthly_trends.append({
            'month': current_date.strftime('%b %Y'),
            'income': month_data['income'],
            'expense': month_data['expense']
        })
        
        # Go to previous month
        if current_date.month == 1:
            current_date = current_date.replace(year=current_date.year - 1, month=12)
        else:
            current_date = current_date.replace(month=current_date.month - 1)
    
    monthly_trends.reverse()
    
    return render_template('main/analytics.html',
                         summary=monthly_summary,
                         category_expenses=category_expenses,
                         monthly_trends=monthly_trends,
                         current_month=f"{datetime(year, month, 1).strftime('%B %Y')}")

@main_bp.route('/api/category_chart_data')
@login_required
def category_chart_data():
    """API endpoint for category chart data"""
    user_id = session['user_id']
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', datetime.now().month, type=int)
    
    category_expenses = transaction_model.get_category_expenses(user_id, year, month)
    
    return jsonify({
        'labels': [cat['name'] for cat in category_expenses],
        'data': [float(cat['total']) for cat in category_expenses],
        'colors': ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF']
    })

@main_bp.route('/api/monthly_trend_data')
@login_required
def monthly_trend_data():
    """API endpoint for monthly trend chart data"""
    user_id = session['user_id']
    
    # Get last 6 months data
    monthly_data = []
    current_date = datetime.now()
    
    for i in range(6):
        month_summary = transaction_model.get_monthly_summary(user_id, current_date.year, current_date.month)
        monthly_data.append({
            'month': current_date.strftime('%b'),
            'income': month_summary['income'],
            'expense': month_summary['expense']
        })
        
        # Go to previous month
        if current_date.month == 1:
            current_date = current_date.replace(year=current_date.year - 1, month=12)
        else:
            current_date = current_date.replace(month=current_date.month - 1)
    
    monthly_data.reverse()
    
    return jsonify({
        'labels': [data['month'] for data in monthly_data],
        'income': [data['income'] for data in monthly_data],
        'expense': [data['expense'] for data in monthly_data]
    })