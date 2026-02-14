"""
Script to create a test user in the database
Run this ONCE to add a test user
"""

import os
import sqlite3

# Database path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "campusconnect.db")

def create_test_user():
    # Connect to database
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    
    cur = conn.cursor()
    
    # Test user credentials
    phone = "9876543210"
    password = "password123"
    
    try:
        # Check if user already exists
        cur.execute("SELECT id FROM users WHERE phone=?", (phone,))
        existing = cur.fetchone()
        
        if existing:
            print(f"✅ Test user already exists!")
            print(f"   Phone: {phone}")
            print(f"   Password: {password}")
        else:
            # Create new test user
            cur.execute("INSERT INTO users (phone, password) VALUES (?, ?)", (phone, password))
            conn.commit()
            print(f"✅ Test user created successfully!")
            print(f"   Phone: {phone}")
            print(f"   Password: {password}")
            print(f"\n   Use these credentials to login at: http://localhost:5000/login")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    create_test_user()
