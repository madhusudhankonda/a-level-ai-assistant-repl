"""
Script to create initial data for hierarchical paper structure:
- Subjects (Maths, Physics, Chemistry, Biology)
- Exam Boards (AQA, Edexcel, OCR)
- Paper Categories (Pure Maths, Pure and Statistics, Pure and Mechanics)
- Sample papers
"""

import os
import sys

# Add parent directory to path so we can import from main app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import Subject, ExamBoard, PaperCategory, QuestionPaper


def create_initial_data():
    with app.app_context():
        # Only create data if tables are empty
        if Subject.query.count() == 0:
            print("Creating initial subjects...")
            # Create subjects
            subjects = [
                Subject(name="Mathematics", description="A-Level Mathematics"),
                Subject(name="Physics", description="A-Level Physics"),
                Subject(name="Chemistry", description="A-Level Chemistry"),
                Subject(name="Biology", description="A-Level Biology")
            ]
            db.session.add_all(subjects)
            db.session.commit()
            
            # Get the subjects we just created
            maths = Subject.query.filter_by(name="Mathematics").first()
            physics = Subject.query.filter_by(name="Physics").first()
            
            # Create exam boards
            print("Creating exam boards...")
            boards = [
                ExamBoard(name="AQA", subject_id=maths.id, description="Assessment and Qualifications Alliance"),
                ExamBoard(name="Edexcel", subject_id=maths.id, description="Edexcel (Pearson)"),
                ExamBoard(name="OCR", subject_id=maths.id, description="Oxford, Cambridge and RSA Examinations"),
                ExamBoard(name="AQA", subject_id=physics.id, description="Assessment and Qualifications Alliance"),
                ExamBoard(name="Edexcel", subject_id=physics.id, description="Edexcel (Pearson)"),
                ExamBoard(name="OCR", subject_id=physics.id, description="Oxford, Cambridge and RSA Examinations")
            ]
            db.session.add_all(boards)
            db.session.commit()
            
            # Get the math boards we just created
            aqa_maths = ExamBoard.query.filter_by(name="AQA", subject_id=maths.id).first()
            edexcel_maths = ExamBoard.query.filter_by(name="Edexcel", subject_id=maths.id).first()
            
            # Create paper categories for maths
            print("Creating paper categories...")
            categories = [
                PaperCategory(name="Pure Mathematics", board_id=aqa_maths.id, description="Pure Mathematics Papers"),
                PaperCategory(name="Pure and Statistics", board_id=aqa_maths.id, description="Pure Mathematics and Statistics Papers"),
                PaperCategory(name="Pure and Mechanics", board_id=aqa_maths.id, description="Pure Mathematics and Mechanics Papers"),
                PaperCategory(name="Pure Mathematics", board_id=edexcel_maths.id, description="Pure Mathematics Papers"),
                PaperCategory(name="Pure and Statistics", board_id=edexcel_maths.id, description="Pure Mathematics and Statistics Papers"),
                PaperCategory(name="Pure and Mechanics", board_id=edexcel_maths.id, description="Pure Mathematics and Mechanics Papers")
            ]
            db.session.add_all(categories)
            db.session.commit()
            
            # Get some categories we just created
            pure_aqa = PaperCategory.query.filter_by(name="Pure Mathematics", board_id=aqa_maths.id).first()
            stats_aqa = PaperCategory.query.filter_by(name="Pure and Statistics", board_id=aqa_maths.id).first()
            
            # Create sample papers
            print("Creating sample papers...")
            papers = [
                QuestionPaper(
                    title="AQA Pure Mathematics June 2023", 
                    category_id=pure_aqa.id,
                    exam_period="June 2023",
                    paper_type="QP",
                    description="AQA A-Level Pure Mathematics Paper (June 2023)"
                ),
                QuestionPaper(
                    title="AQA Pure Mathematics June 2022", 
                    category_id=pure_aqa.id,
                    exam_period="June 2022",
                    paper_type="QP",
                    description="AQA A-Level Pure Mathematics Paper (June 2022)"
                ),
                QuestionPaper(
                    title="AQA Pure Mathematics November 2022", 
                    category_id=pure_aqa.id,
                    exam_period="November 2022",
                    paper_type="QP",
                    description="AQA A-Level Pure Mathematics Paper (November 2022)"
                ),
                QuestionPaper(
                    title="AQA Pure and Statistics June 2023", 
                    category_id=stats_aqa.id,
                    exam_period="June 2023",
                    paper_type="QP",
                    description="AQA A-Level Pure Mathematics and Statistics Paper (June 2023)"
                ),
                QuestionPaper(
                    title="AQA Pure and Statistics June 2022", 
                    category_id=stats_aqa.id,
                    exam_period="June 2022",
                    paper_type="QP",
                    description="AQA A-Level Pure Mathematics and Statistics Paper (June 2022)"
                )
            ]
            db.session.add_all(papers)
            db.session.commit()
            
            print("Initial data creation complete!")
        else:
            print("Data already exists, skipping initial data creation.")


if __name__ == "__main__":
    create_initial_data()