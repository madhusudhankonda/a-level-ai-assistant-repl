#!/usr/bin/env python
"""
Script to set a user as admin in the database
Usage: python make_admin.py <username or email>
"""

import sys
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
db.init_app(app)

# Import the User model
from models import User

def make_user_admin(identifier):
    """
    Make a user an admin by username or email
    """
    with app.app_context():
        # Try to find the user by username or email
        user = User.query.filter(
            (User.username == identifier) | (User.email == identifier)
        ).first()
        
        if not user:
            print(f"Error: No user found with username or email '{identifier}'")
            return False
        
        # Make user an admin
        user.is_admin = True
        db.session.commit()
        
        print(f"Success: User '{user.username}' (email: {user.email}) is now an admin")
        return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python make_admin.py <username or email>")
        sys.exit(1)
    
    identifier = sys.argv[1]
    if not make_user_admin(identifier):
        sys.exit(1)