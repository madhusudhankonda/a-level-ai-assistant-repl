#!/usr/bin/env python
"""
Script to list all users in the database
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def list_users():
    """
    List all users in the database
    """
    # Connect directly to the database to avoid circular imports
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("Error: DATABASE_URL environment variable not set")
        return False
        
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Get all users
        query = text("SELECT id, username, email, is_admin, credits FROM \"user\" ORDER BY id")
        results = session.execute(query).fetchall()
        
        if not results:
            print("No users found in the database")
            return False
            
        print(f"Total users: {len(results)}")
        print("-" * 80)
        print(f"{'ID':<5} {'Username':<20} {'Email':<30} {'Admin':<6} {'Credits':<8}")
        print("-" * 80)
        
        for user_id, username, email, is_admin, credits in results:
            print(f"{user_id:<5} {username:<20} {email:<30} {is_admin!s:<6} {credits:<8}")
            
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False
    finally:
        session.close()

if __name__ == "__main__":
    list_users()