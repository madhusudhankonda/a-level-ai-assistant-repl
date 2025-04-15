#!/usr/bin/env python
"""
Script to clear all papers and questions from the database
"""

import os
import shutil
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def clear_papers():
    """
    Clear all papers and questions from the database
    """
    # Connect directly to the database
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("Error: DATABASE_URL environment variable not set")
        return False
        
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Count papers first
        count_query = text("SELECT COUNT(*) FROM question_paper")
        paper_count = session.execute(count_query).scalar()
        
        # Count questions
        count_query = text("SELECT COUNT(*) FROM question")
        question_count = session.execute(count_query).scalar()
        
        # Count explanations
        count_query = text("SELECT COUNT(*) FROM explanation")
        explanation_count = session.execute(count_query).scalar()
        
        # Count user queries
        count_query = text("SELECT COUNT(*) FROM user_query")
        user_query_count = session.execute(count_query).scalar()
        
        # Count student answers
        count_query = text("SELECT COUNT(*) FROM student_answer")
        student_answer_count = session.execute(count_query).scalar()
        
        print(f"Found {paper_count} papers, {question_count} questions, {explanation_count} explanations, {user_query_count} user queries, and {student_answer_count} student answers to remove")
        
        # Delete dependent records first (due to foreign key constraints)
        delete_query = text("DELETE FROM explanation")
        result = session.execute(delete_query)
        
        delete_query = text("DELETE FROM student_answer WHERE question_id IS NOT NULL")
        result = session.execute(delete_query)
        
        delete_query = text("DELETE FROM user_query WHERE question_id IS NOT NULL")
        result = session.execute(delete_query)
        
        delete_query = text("DELETE FROM question_topic")
        result = session.execute(delete_query)
        
        # Now delete all questions
        delete_query = text("DELETE FROM question")
        result = session.execute(delete_query)
        session.commit()
        print(f"Deleted {question_count} questions and related records from the database")
        
        # Delete all papers
        delete_query = text("DELETE FROM question_paper")
        result = session.execute(delete_query)
        session.commit()
        print(f"Deleted {paper_count} papers from the database")
        
        # Clear the paper directories
        data_dir = os.path.join(os.getcwd(), 'data')
        if os.path.exists(data_dir):
            paper_dirs = [d for d in os.listdir(data_dir) if d.startswith('paper_')]
            
            for paper_dir in paper_dirs:
                dir_path = os.path.join(data_dir, paper_dir)
                if os.path.isdir(dir_path):
                    shutil.rmtree(dir_path)
                    print(f"Removed directory: {dir_path}")
            
            print(f"Cleared {len(paper_dirs)} paper directories")
        
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        session.rollback()
        return False
    finally:
        session.close()

if __name__ == "__main__":
    print("WARNING: This will permanently delete ALL papers and questions from the database!")
    confirm = input("Are you sure you want to continue? (y/n): ").lower()
    
    if confirm == 'y':
        if clear_papers():
            print("Successfully cleared all papers and questions")
        else:
            print("Failed to clear papers")
    else:
        print("Operation cancelled")