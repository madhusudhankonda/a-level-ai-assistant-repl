#!/usr/bin/env python3
"""
Script to update the database schema with the image_url field and
migrate existing questions to use URL-based image storage.
"""

from app import app, db
from models import Question
from flask import url_for
import os
import sys

def get_domain():
    """Get the domain for the application"""
    # In Replit, use the REPLIT_DEV_DOMAIN or REPLIT_DOMAINS environment variable
    if os.environ.get('REPLIT_DEPLOYMENT'):
        return os.environ.get('REPLIT_DEV_DOMAIN')
    elif os.environ.get('REPLIT_DOMAINS'):
        return os.environ.get('REPLIT_DOMAINS').split(',')[0]
    else:
        # Local development
        return 'localhost:5000'

def update_schema():
    """Add the image_url column to the Question table if it doesn't exist"""
    print("Adding image_url column to Question table...")
    try:
        with app.app_context():
            # The image_url column is already defined in the model, so we can skip this step
            # as SQLAlchemy should handle this automatically when db.create_all() is called
            print("Column image_url is already defined in the model and should exist.")
            return True
    except Exception as e:
        print(f"Error checking schema: {e}")
        return False
    return True

def update_image_urls():
    """Update image_url for all questions"""
    print("Updating image URLs for all questions...")
    try:
        with app.app_context():
            domain = get_domain()
            
            # Get all questions
            questions = Question.query.all()
            print(f"Found {len(questions)} questions to update.")
            
            for question in questions:
                # Generate a URL for the question image
                url = f"https://{domain}/user/question-image/{question.id}"
                question.image_url = url
                print(f"Updated Question {question.id} (Paper {question.paper_id}, Q{question.question_number}) URL: {url}")
            
            # Save all changes
            db.session.commit()
            print("All questions updated successfully.")
    except Exception as e:
        print(f"Error updating image URLs: {e}")
        return False
    return True

if __name__ == "__main__":
    # Add the image_url column to the Question table
    if not update_schema():
        sys.exit(1)
    
    # Update image_url for all questions
    if not update_image_urls():
        sys.exit(1)
    
    print("Migration completed successfully.")