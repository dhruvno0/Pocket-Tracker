from datetime import datetime, timedelta
from typing import List, Dict
import calendar

class InsightsEngine:
    def __init__(self, db):
        self.db = db
    
    def generate_insights(self, user_id: int) -> List[str]:
        """Generate smart insights based on spending patterns"""
        insights = []
        
        # Current and previous month data
        now = datetime.now()
        current_month = now.month
        current_year = now.year
        
        prev_month = current_month - 1 if current_month > 1 else 12
        prev_year = current_year if current_month > 1 else current_year - 1
        
        # Get monthly summaries
        current_summary = self._get_monthly_summary(user_id, current_year, current_month)
        prev_summary = self._get_monthly_summary(user_id, prev_year, prev_month)
        
        # Spending trend analysis
        if prev_summary['expense'] > 0:
            expense_change = ((current_summary['expense'] - prev_summary['expense']) / prev_summary['expense']) * 100
            
            if expense_change > 20:
                insights.append(f"⚠️ Your expenses increased by {expense_change:.1f}% this month. Consider reviewing your spending.")
            elif expense_change < -10:
                insights.append(f"✅ Great job! You reduced expenses by {abs(expense_change):.1f}% this month.")
        
        # Category-wise insights
        category_insights = self._analyze_category_spending(user_id, current_year, current_month)
        insights.extend(category_insights)
        
        # Budget alerts
        budget_alerts = self._check_budget_alerts(user_id, current_year, current_month)
        insights.extend(budget_alerts)
        
        # Savings insights
        savings_insights = self._analyze_savings_pattern(user_id)
        insights.extend(savings_insights)
        
        return insights[:5]  # Return top 5 insights
    
    def _get_monthly_summary(self, user_id: int, year: int, month: int) -> Dict:
        """Get monthly summary for analysis"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                type,
                SUM(amount) as total
            FROM transactions 
            WHERE user_id = ? 
            AND strftime('%Y', transaction_date) = ? 
            AND strftime('%m', transaction_date) = ?
            GROUP BY type
        ''', (user_id, str(year), f"{month:02d}"))
        
        results = cursor.fetchall()
        conn.close()
        
        summary = {'income': 0, 'expense': 0}
        for row in results:
            summary[row['type']] = float(row['total'])
        
        return summary
    
    def _analyze_category_spending(self, user_id: int, year: int, month: int) -> List[str]:
        """Analyze category-wise spending patterns"""
        insights = []
        
        # Get current month category expenses
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                c.name,
                SUM(t.amount) as current_total
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.user_id = ? 
            AND t.type = 'expense'
            AND strftime('%Y', t.transaction_date) = ? 
            AND strftime('%m', t.transaction_date) = ?
            GROUP BY c.id, c.name
        ''', (user_id, str(year), f"{month:02d}"))
        
        current_expenses = {row['name']: float(row['current_total']) for row in cursor.fetchall()}
        
        # Get previous month for comparison
        prev_month = month - 1 if month > 1 else 12
        prev_year = year if month > 1 else year - 1
        
        cursor.execute('''
            SELECT 
                c.name,
                SUM(t.amount) as prev_total
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.user_id = ? 
            AND t.type = 'expense'
            AND strftime('%Y', t.transaction_date) = ? 
            AND strftime('%m', t.transaction_date) = ?
            GROUP BY c.id, c.name
        ''', (user_id, str(prev_year), f"{prev_month:02d}"))
        
        prev_expenses = {row['name']: float(row['prev_total']) for row in cursor.fetchall()}
        conn.close()
        
        # Analyze changes
        for category, current_amount in current_expenses.items():
            if category in prev_expenses and prev_expenses[category] > 0:
                change = ((current_amount - prev_expenses[category]) / prev_expenses[category]) * 100
                
                if change > 30:
                    insights.append(f"📈 {category} expenses increased by {change:.1f}% this month")
                elif change < -20:
                    insights.append(f"📉 You saved {abs(change):.1f}% on {category} this month")
        
        # Find highest expense category
        if current_expenses:
            top_category = max(current_expenses, key=current_expenses.get)
            top_amount = current_expenses[top_category]
            total_expenses = sum(current_expenses.values())
            
            if total_expenses > 0:
                percentage = (top_amount / total_expenses) * 100
                if percentage > 40:
                    insights.append(f"💡 {top_category} accounts for {percentage:.1f}% of your expenses")
        
        return insights
    
    def _check_budget_alerts(self, user_id: int, year: int, month: int) -> List[str]:
        """Check for budget limit violations"""
        alerts = []
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Get budgets with current spending
        cursor.execute('''
            SELECT 
                b.monthly_limit,
                c.name as category_name,
                COALESCE(SUM(t.amount), 0) as spent
            FROM budgets b
            JOIN categories c ON b.category_id = c.id
            LEFT JOIN transactions t ON (
                t.category_id = b.category_id 
                AND t.user_id = b.user_id 
                AND t.type = 'expense'
                AND strftime('%Y', t.transaction_date) = ?
                AND strftime('%m', t.transaction_date) = ?
            )
            WHERE b.user_id = ?
            GROUP BY b.id, b.monthly_limit, c.name
        ''', (str(year), f"{month:02d}", user_id))
        
        results = cursor.fetchall()
        conn.close()
        
        for row in results:
            limit = float(row['monthly_limit'])
            spent = float(row['spent'])
            category = row['category_name']
            
            if spent > limit:
                overspent = spent - limit
                alerts.append(f"🚨 You exceeded {category} budget by ₹{overspent:.0f}")
            elif spent > limit * 0.8:
                remaining = limit - spent
                alerts.append(f"⚠️ Only ₹{remaining:.0f} left in {category} budget")
        
        return alerts
    
    def _analyze_savings_pattern(self, user_id: int) -> List[str]:
        """Analyze savings patterns and provide tips"""
        insights = []
        
        # Get last 3 months data
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                strftime('%Y-%m', transaction_date) as month,
                type,
                SUM(amount) as total
            FROM transactions 
            WHERE user_id = ? 
            AND transaction_date >= date('now', '-3 months')
            GROUP BY month, type
            ORDER BY month DESC
        ''', (user_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        monthly_data = {}
        for row in results:
            month = row['month']
            if month not in monthly_data:
                monthly_data[month] = {'income': 0, 'expense': 0}
            monthly_data[month][row['type']] = float(row['total'])
        
        # Calculate savings rate
        savings_rates = []
        for month_data in monthly_data.values():
            if month_data['income'] > 0:
                savings_rate = ((month_data['income'] - month_data['expense']) / month_data['income']) * 100
                savings_rates.append(savings_rate)
        
        if savings_rates:
            avg_savings_rate = sum(savings_rates) / len(savings_rates)
            
            if avg_savings_rate < 10:
                insights.append("💡 Try to save at least 10% of your income each month")
            elif avg_savings_rate > 20:
                insights.append(f"🎉 Excellent! You're saving {avg_savings_rate:.1f}% of your income")
        
        return insights
    
    def get_spending_tips(self, user_id: int) -> List[str]:
        """Generate personalized spending tips"""
        tips = [
            "💡 Track every expense, no matter how small",
            "🎯 Set realistic budgets for each category",
            "📱 Review your expenses weekly",
            "🛒 Make a shopping list before going out",
            "☕ Consider making coffee at home instead of buying",
            "🚗 Use public transport or carpool to save on travel",
            "🍽️ Cook meals at home more often",
            "💳 Use cash for discretionary spending to stay mindful"
        ]
        
        # Get user's top expense category for personalized tip
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.name, SUM(t.amount) as total
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.user_id = ? AND t.type = 'expense'
            AND t.transaction_date >= date('now', '-1 month')
            GROUP BY c.id, c.name
            ORDER BY total DESC
            LIMIT 1
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            category = result['name'].lower()
            if 'food' in category:
                tips.insert(0, "🍽️ Plan your meals weekly to reduce food expenses")
            elif 'travel' in category:
                tips.insert(0, "🚗 Consider carpooling or public transport for daily commute")
            elif 'shopping' in category:
                tips.insert(0, "🛒 Wait 24 hours before making non-essential purchases")
        
        return tips[:4]