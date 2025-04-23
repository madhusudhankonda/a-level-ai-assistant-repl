"""
Script to update the database with the new is_active field for QuestionPaper model.
This script will:
1. Add the is_active column to the question_paper table if it doesn't exist
2. Set OCR papers to inactive (except Practice/Mock papers)
"""
from app import app, db
from models import QuestionPaper
import sqlalchemy as sa
from sqlalchemy import inspect

def update_papers_active():
    """
    Update QuestionPaper model with is_active field and set OCR papers to inactive
    """
    print("Updating QuestionPaper table...")
    
    # Check if is_active column exists
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns('question_paper')]
    
    if 'is_active' not in columns:
        print("Adding is_active column to question_paper table...")
        # Add the column
        with db.engine.connect() as conn:
            conn.execute(sa.text("ALTER TABLE question_paper ADD COLUMN is_active BOOLEAN DEFAULT TRUE"))
            conn.commit()
        print("Column added successfully.")
    else:
        print("is_active column already exists.")
    
    # Set OCR papers to inactive except for Practice/Mock papers
    with app.app_context():
        ocr_papers = QuestionPaper.query.filter(
            QuestionPaper.title.like('%OCR%')
        ).all()
        
        inactive_count = 0
        active_count = 0
        for paper in ocr_papers:
            if 'Practice Paper' in paper.title or 'Mock Paper' in paper.title:
                # Ensure practice/mock papers are active
                if not paper.is_active:
                    paper.is_active = True
                    active_count += 1
                    print(f"Setting active: {paper.title}")
            else:
                # Set regular OCR papers to inactive
                if paper.is_active:
                    paper.is_active = False
                    inactive_count += 1
                    print(f"Setting inactive: {paper.title}")
        
        db.session.commit()
        print(f"Updated {inactive_count} OCR papers to inactive and {active_count} practice/mock papers to active.")

if __name__ == "__main__":
    with app.app_context():
        update_papers_active()