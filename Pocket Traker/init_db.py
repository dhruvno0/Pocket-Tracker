#!/usr/bin/env python3
"""
Database initialization script for Pocket Expense Tracker
Run this script to set up the database with default categories
"""

from models import Database

def init_database():
    """Initialize the database with tables and default data"""
    print("Initializing Pocket Expense Tracker database...")
    
    try:
        db = Database()
        print("✅ Database initialized successfully!")
        print("✅ Default categories added")
        print("\nYou can now run the application with: python app.py")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False
    
    return True

if __name__ == '__main__':
    init_database()