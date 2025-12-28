#!/usr/bin/env python3
"""
Simple test script to verify Pocket Tracker functionality
Run this after setting up the application to ensure everything works
"""

import os
import sys
from models import Database, User, Transaction, Category, Budget

def test_database_setup():
    """Test database initialization"""
    print("🔍 Testing database setup...")
    
    try:
        db = Database('test_pocket_tracker.db')
        print("✅ Database created successfully")
        
        # Test categories
        category_model = Category(db)
        categories = category_model.get_all_categories()
        print(f"✅ Found {len(categories)} default categories")
        
        return db
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return None

def test_user_operations(db):
    """Test user creation and authentication"""
    print("\n🔍 Testing user operations...")
    
    try:
        user_model = User(db)
        
        # Create test user
        success = user_model.create_user("testuser", "test@example.com", "password123")
        if success:
            print("✅ User created successfully")
        else:
            print("⚠️ User already exists or creation failed")
        
        # Test authentication
        user = user_model.authenticate("testuser", "password123")
        if user:
            print("✅ User authentication successful")
            return user['id']
        else:
            print("❌ User authentication failed")
            return None
            
    except Exception as e:
        print(f"❌ User operations failed: {e}")
        return None

def test_transaction_operations(db, user_id):
    """Test transaction creation and retrieval"""
    print("\n🔍 Testing transaction operations...")
    
    try:
        transaction_model = Transaction(db)
        category_model = Category(db)
        
        # Get a category for testing
        categories = category_model.get_all_categories()
        if not categories:
            print("❌ No categories found")
            return False
        
        test_category = categories[0]
        
        # Add test transactions
        transactions_added = 0
        
        # Add income
        if transaction_model.add_transaction(
            user_id, 50000, 'income', test_category['id'], 
            'Bank Transfer', 'Test salary', '2024-01-01'
        ):
            transactions_added += 1
        
        # Add expense
        if transaction_model.add_transaction(
            user_id, 1500, 'expense', test_category['id'], 
            'UPI', 'Test expense', '2024-01-02'
        ):
            transactions_added += 1
        
        print(f"✅ Added {transactions_added} test transactions")
        
        # Retrieve transactions
        user_transactions = transaction_model.get_user_transactions(user_id, limit=10)
        print(f"✅ Retrieved {len(user_transactions)} transactions")
        
        # Test monthly summary
        summary = transaction_model.get_monthly_summary(user_id, 2024, 1)
        print(f"✅ Monthly summary: Income ₹{summary['income']}, Expense ₹{summary['expense']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Transaction operations failed: {e}")
        return False

def test_budget_operations(db, user_id):
    """Test budget creation and retrieval"""
    print("\n🔍 Testing budget operations...")
    
    try:
        budget_model = Budget(db)
        category_model = Category(db)
        
        # Get a category for testing
        categories = category_model.get_all_categories()
        if not categories:
            print("❌ No categories found")
            return False
        
        test_category = categories[0]
        
        # Set budget
        if budget_model.set_budget(user_id, test_category['id'], 5000):
            print("✅ Budget set successfully")
        else:
            print("❌ Budget setting failed")
            return False
        
        # Retrieve budgets
        user_budgets = budget_model.get_user_budgets(user_id)
        print(f"✅ Retrieved {len(user_budgets)} budgets")
        
        return True
        
    except Exception as e:
        print(f"❌ Budget operations failed: {e}")
        return False

def test_insights_engine(db, user_id):
    """Test insights generation"""
    print("\n🔍 Testing insights engine...")
    
    try:
        from insights import InsightsEngine
        
        insights_engine = InsightsEngine(db)
        insights = insights_engine.generate_insights(user_id)
        tips = insights_engine.get_spending_tips(user_id)
        
        print(f"✅ Generated {len(insights)} insights")
        print(f"✅ Generated {len(tips)} spending tips")
        
        return True
        
    except Exception as e:
        print(f"❌ Insights engine failed: {e}")
        return False

def cleanup_test_db():
    """Clean up test database"""
    try:
        if os.path.exists('test_pocket_tracker.db'):
            os.remove('test_pocket_tracker.db')
            print("🧹 Test database cleaned up")
    except Exception as e:
        print(f"⚠️ Cleanup warning: {e}")

def main():
    """Run all tests"""
    print("🚀 Starting Pocket Tracker Tests")
    print("=" * 50)
    
    # Test database setup
    db = test_database_setup()
    if not db:
        print("\n❌ Database tests failed. Exiting.")
        return False
    
    # Test user operations
    user_id = test_user_operations(db)
    if not user_id:
        print("\n❌ User tests failed. Exiting.")
        cleanup_test_db()
        return False
    
    # Test transaction operations
    if not test_transaction_operations(db, user_id):
        print("\n❌ Transaction tests failed.")
        cleanup_test_db()
        return False
    
    # Test budget operations
    if not test_budget_operations(db, user_id):
        print("\n❌ Budget tests failed.")
        cleanup_test_db()
        return False
    
    # Test insights engine
    if not test_insights_engine(db, user_id):
        print("\n❌ Insights tests failed.")
        cleanup_test_db()
        return False
    
    # All tests passed
    print("\n" + "=" * 50)
    print("🎉 All tests passed! Your Pocket Tracker is ready to use.")
    print("\nNext steps:")
    print("1. Run: python app.py")
    print("2. Open: http://localhost:5000")
    print("3. Create your account and start tracking!")
    
    cleanup_test_db()
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)