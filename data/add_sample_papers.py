"""
Script to add sample papers to existing categories
"""

import os
import sys
from datetime import datetime

# Add parent directory to path so we can import from main app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import Subject, ExamBoard, PaperCategory, QuestionPaper


def add_sample_papers():
    with app.app_context():
        # Check if we have the base structure
        maths = Subject.query.filter_by(name="Mathematics").first()
        
        if not maths:
            print("Mathematics subject not found. Please run create_initial_data.py first.")
            return
        
        aqa = ExamBoard.query.filter_by(name="AQA", subject_id=maths.id).first()
        edexcel = ExamBoard.query.filter_by(name="Edexcel", subject_id=maths.id).first()
        
        if not aqa or not edexcel:
            print("Exam boards not found. Please run create_initial_data.py first.")
            return
        
        # Get the categories
        pure_aqa = PaperCategory.query.filter_by(name="Pure Mathematics", board_id=aqa.id).first()
        stats_aqa = PaperCategory.query.filter_by(name="Pure and Statistics", board_id=aqa.id).first()
        mechanics_aqa = PaperCategory.query.filter_by(name="Pure and Mechanics", board_id=aqa.id).first()
        
        pure_edexcel = PaperCategory.query.filter_by(name="Pure Mathematics", board_id=edexcel.id).first()
        stats_edexcel = PaperCategory.query.filter_by(name="Pure and Statistics", board_id=edexcel.id).first()
        mechanics_edexcel = PaperCategory.query.filter_by(name="Pure and Mechanics", board_id=edexcel.id).first()
        
        if not all([pure_aqa, stats_aqa, mechanics_aqa, pure_edexcel, stats_edexcel, mechanics_edexcel]):
            print("Paper categories not found. Please run create_initial_data.py first.")
            return
        
        # Create new papers
        print("Adding sample papers...")
        
        # AQA Papers
        aqa_papers = []
        
        # AQA Pure Mathematics
        for year in range(2018, 2024):
            # June papers
            aqa_papers.append(
                QuestionPaper(
                    title=f"AQA Pure Mathematics June {year}",
                    category_id=pure_aqa.id,
                    subject="Mathematics",
                    exam_period=f"June {year}",
                    paper_type="QP",
                    description=f"AQA A-Level Pure Mathematics Paper (June {year})"
                )
            )
            
            # November papers (not all years have November exams)
            if year >= 2020:
                aqa_papers.append(
                    QuestionPaper(
                        title=f"AQA Pure Mathematics November {year}",
                        category_id=pure_aqa.id,
                        subject="Mathematics",
                        exam_period=f"November {year}",
                        paper_type="QP",
                        description=f"AQA A-Level Pure Mathematics Paper (November {year})"
                    )
                )
        
        # AQA Pure and Statistics
        for year in range(2018, 2024):
            aqa_papers.append(
                QuestionPaper(
                    title=f"AQA Pure and Statistics June {year}",
                    category_id=stats_aqa.id,
                    subject="Mathematics",
                    exam_period=f"June {year}",
                    paper_type="QP",
                    description=f"AQA A-Level Pure Mathematics and Statistics Paper (June {year})"
                )
            )
            
            # November papers (not all years have November exams)
            if year >= 2020:
                aqa_papers.append(
                    QuestionPaper(
                        title=f"AQA Pure and Statistics November {year}",
                        category_id=stats_aqa.id,
                        subject="Mathematics",
                        exam_period=f"November {year}",
                        paper_type="QP",
                        description=f"AQA A-Level Pure Mathematics and Statistics Paper (November {year})"
                    )
                )
        
        # AQA Pure and Mechanics
        for year in range(2018, 2024):
            aqa_papers.append(
                QuestionPaper(
                    title=f"AQA Pure and Mechanics June {year}",
                    category_id=mechanics_aqa.id,
                    subject="Mathematics",
                    exam_period=f"June {year}",
                    paper_type="QP",
                    description=f"AQA A-Level Pure Mathematics and Mechanics Paper (June {year})"
                )
            )
            
            # November papers (not all years have November exams)
            if year >= 2020:
                aqa_papers.append(
                    QuestionPaper(
                        title=f"AQA Pure and Mechanics November {year}",
                        category_id=mechanics_aqa.id,
                        subject="Mathematics",
                        exam_period=f"November {year}",
                        paper_type="QP",
                        description=f"AQA A-Level Pure Mathematics and Mechanics Paper (November {year})"
                    )
                )
        
        # Edexcel Papers
        edexcel_papers = []
        
        # Edexcel Pure Mathematics
        for year in range(2018, 2024):
            edexcel_papers.append(
                QuestionPaper(
                    title=f"Edexcel Pure Mathematics June {year}",
                    category_id=pure_edexcel.id,
                    subject="Mathematics",
                    exam_period=f"June {year}",
                    paper_type="QP",
                    description=f"Edexcel A-Level Pure Mathematics Paper (June {year})"
                )
            )
            
            # November papers (not all years have November exams)
            if year >= 2020:
                edexcel_papers.append(
                    QuestionPaper(
                        title=f"Edexcel Pure Mathematics November {year}",
                        category_id=pure_edexcel.id,
                        subject="Mathematics",
                        exam_period=f"November {year}",
                        paper_type="QP",
                        description=f"Edexcel A-Level Pure Mathematics Paper (November {year})"
                    )
                )
        
        # Add papers to the database
        db.session.add_all(aqa_papers)
        db.session.add_all(edexcel_papers)
        db.session.commit()
        
        print(f"Added {len(aqa_papers) + len(edexcel_papers)} sample papers successfully!")


if __name__ == "__main__":
    add_sample_papers()