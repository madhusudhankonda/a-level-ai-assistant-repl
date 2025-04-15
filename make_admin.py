#!/usr/bin/env python
"""
Script to set a user as admin in the database
Usage: python make_admin.py <username or email>
"""

import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def make_user_admin(identifier):
    """
    Make a user an admin by username or email
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
        # Check if user exists
        query = text("SELECT id, username, email FROM \"user\" WHERE username = :identifier OR email = :identifier")
        result = session.execute(query, {"identifier": identifier}).fetchone()
        
        if not result:
            print(f"Error: No user found with username or email '{identifier}'")
            return False
            
        user_id, username, email = result
        
        # Update the user to be an admin
        update_query = text("UPDATE \"user\" SET is_admin = TRUE WHERE id = :user_id")
        session.execute(update_query, {"user_id": user_id})
        session.commit()
        
        print(f"Success: User '{username}' (email: {email}) is now an admin")
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        session.rollback()
        return False
    finally:
        session.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python make_admin.py <username or email>")
        sys.exit(1)
    
    identifier = sys.argv[1]
    if not make_user_admin(identifier):
        sys.exit(1)