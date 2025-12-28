import sqlite3
import bcrypt
from datetime import datetime, date
from typing import List, Dict, Optional

class Database:
    def __init__(self, db_path: str = 'pocket_tracker.db'):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Initialize database with tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(80) UNIQUE NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(128) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Categories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(50) NOT NULL,
                icon VARCHAR(20) DEFAULT '💰',
                is_default BOOLEAN DEFAULT 0
            )
        ''')
        
        # Transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                type VARCHAR(10) NOT NULL CHECK (type IN ('income', 'expense')),
                category_id INTEGER NOT NULL,
                payment_mode VARCHAR(20) NOT NULL,
                description TEXT,
                transaction_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        ''')
        
        # Budgets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                category_id INTEGER NOT NULL,
                monthly_limit DECIMAL(10,2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (category_id) REFERENCES categories (id),
                UNIQUE(user_id, category_id)
            )
        ''')
        
        # Insert default categories
        default_categories = [
            ('Food', '🍽️', 1),
            ('Travel', '🚗', 1),
            ('Rent', '🏠', 1),
            ('Shopping', '🛒', 1),
            ('Entertainment', '🎬', 1),
            ('Healthcare', '🏥', 1),
            ('Education', '📚', 1),
            ('Other', '📦', 1),
            ('Salary', '💼', 1),
            ('Freelance', '💻', 1)
        ]
        
        cursor.executemany(
            'INSERT OR IGNORE INTO categories (name, icon, is_default) VALUES (?, ?, ?)',
            default_categories
        )
        
        conn.commit()
        conn.close()

class User:
    def __init__(self, db: Database):
        self.db = db
    
    def create_user(self, username: str, email: str, password: str) -> bool:
        """Create new user with hashed password"""
        try:
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                (username, email, password_hash)
            )
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def authenticate(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user and return user data"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM users WHERE username = ? AND is_active = 1',
            (username,)
        )
        user = cursor.fetchone()
        conn.close()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            return dict(user)
        return None
    
    def get_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None

class Transaction:
    def __init__(self, db: Database):
        self.db = db
    
    def add_transaction(self, user_id: int, amount: float, trans_type: str, 
                       category_id: int, payment_mode: str, description: str, 
                       transaction_date: str) -> bool:
        """Add new transaction"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO transactions 
                (user_id, amount, type, category_id, payment_mode, description, transaction_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, amount, trans_type, category_id, payment_mode, description, transaction_date))
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False
    
    def get_user_transactions(self, user_id: int, limit: int = 50) -> List[Dict]:
        """Get user transactions with category info"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT t.*, c.name as category_name, c.icon as category_icon
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.user_id = ?
            ORDER BY t.transaction_date DESC, t.created_at DESC
            LIMIT ?
        ''', (user_id, limit))
        transactions = cursor.fetchall()
        conn.close()
        return [dict(t) for t in transactions]
    
    def get_monthly_summary(self, user_id: int, year: int, month: int) -> Dict:
        """Get monthly income/expense summary"""
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
        
        summary['balance'] = summary['income'] - summary['expense']
        return summary
    
    def get_category_expenses(self, user_id: int, year: int, month: int) -> List[Dict]:
        """Get category-wise expenses for charts"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                c.name,
                c.icon,
                SUM(t.amount) as total
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.user_id = ? 
            AND t.type = 'expense'
            AND strftime('%Y', t.transaction_date) = ? 
            AND strftime('%m', t.transaction_date) = ?
            GROUP BY c.id, c.name, c.icon
            ORDER BY total DESC
        ''', (user_id, str(year), f"{month:02d}"))
        
        results = cursor.fetchall()
        conn.close()
        return [dict(r) for r in results]

class Category:
    def __init__(self, db: Database):
        self.db = db
    
    def get_all_categories(self) -> List[Dict]:
        """Get all categories"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM categories ORDER BY name')
        categories = cursor.fetchall()
        conn.close()
        return [dict(c) for c in categories]

class Budget:
    def __init__(self, db: Database):
        self.db = db
    
    def set_budget(self, user_id: int, category_id: int, monthly_limit: float) -> bool:
        """Set or update budget for category"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO budgets (user_id, category_id, monthly_limit)
                VALUES (?, ?, ?)
            ''', (user_id, category_id, monthly_limit))
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False
    
    def get_user_budgets(self, user_id: int) -> List[Dict]:
        """Get user budgets with category info"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT b.*, c.name as category_name, c.icon as category_icon
            FROM budgets b
            JOIN categories c ON b.category_id = c.id
            WHERE b.user_id = ?
        ''', (user_id,))
        budgets = cursor.fetchall()
        conn.close()
        return [dict(b) for b in budgets]