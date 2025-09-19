#!/usr/bin/env python3
"""
Database setup script for Interview Agent
"""

import os
import sys
from dotenv import load_dotenv
import pymysql

# Load environment variables
load_dotenv()

def create_database():
    """Create the MySQL database if it doesn't exist"""
    try:
        # Connect to MySQL server (without specifying database)
        connection = pymysql.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', ''),
            charset='utf8mb4'
        )
        
        database_name = os.getenv('MYSQL_DATABASE', 'interview_agent')
        
        with connection.cursor() as cursor:
            # Create database if it doesn't exist
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"Database '{database_name}' created successfully or already exists.")
        
        connection.commit()
        connection.close()
        return True
        
    except Exception as e:
        print(f"Error creating database: {e}")
        return False

def setup_tables():
    """Create tables using Flask-SQLAlchemy"""
    try:
        from app import app, db
        
        with app.app_context():
            # Create all tables
            db.create_all()
            print("Tables created successfully.")
        
        return True
        
    except Exception as e:
        print(f"Error creating tables: {e}")
        return False

if __name__ == '__main__':
    print("Setting up Interview Agent Database...")
    
    # Check if required environment variables are set
    required_vars = ['MYSQL_HOST', 'MYSQL_USER', 'MYSQL_PASSWORD', 'MYSQL_DATABASE']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please create a .env file based on .env.example")
        sys.exit(1)
    
    # Create database
    if create_database():
        print("✓ Database setup complete")
    else:
        print("✗ Database setup failed")
        sys.exit(1)
    
    # Create tables
    if setup_tables():
        print("✓ Tables setup complete")
    else:
        print("✗ Tables setup failed")
        sys.exit(1)
    
    print("\n🎉 Database setup completed successfully!")
    print("You can now run the application with: python app.py")