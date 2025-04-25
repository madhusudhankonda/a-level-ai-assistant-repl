#!/usr/bin/env python
"""
Script to add questions to empty papers by generating mock questions
based on existing papers with questions.

Usage:
    python add_questions_to_empty_papers.py
"""

import os
import sys
import logging
import uuid
import random
from flask import current_app
from app import app, db
from models import QuestionPaper, Question, Subject, ExamBoard, PaperCategory
from generate_mock_questions import create_mock_question, create_mock_mark_scheme, get_fonts
from PIL import Image, ImageDraw, ImageFont

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_data_folder():
    """Get or create the data folder for storing papers and questions"""
    data_folder = os.path.join(os.getcwd(), 'data')
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
    return data_folder

def find_empty_papers():
    """Find all papers that don't have any questions"""
    with app.app_context():
        # Find all papers
        all_papers = QuestionPaper.query.all()
        empty_papers = []
        
        # Check each paper for questions
        for paper in all_papers:
            question_count = Question.query.filter_by(paper_id=paper.id).count()
            if question_count == 0:
                empty_papers.append(paper)
                logger.info(f"Found empty paper: {paper.title} (ID: {paper.id})")
        
        return empty_papers

def find_papers_with_questions():
    """Find all papers that have questions to use as templates"""
    with app.app_context():
        results = []
        # Find papers with questions
        papers_with_questions = db.session.query(
            QuestionPaper, db.func.count(Question.id).label('question_count')
        ).join(
            Question, Question.paper_id == QuestionPaper.id
        ).group_by(
            QuestionPaper.id
        ).having(
            db.func.count(Question.id) > 0
        ).order_by(
            db.func.count(Question.id).desc()
        ).all()
        
        for paper, question_count in papers_with_questions:
            results.append((paper, question_count))
            logger.info(f"Found paper with {question_count} questions: {paper.title} (ID: {paper.id})")
        
        return results

def get_question_templates(paper_id, limit=10):
    """Get question templates from a paper to use for generating new questions"""
    with app.app_context():
        questions = Question.query.filter_by(paper_id=paper_id).order_by(Question.question_number).limit(limit).all()
        return questions

def add_questions_to_paper(target_paper, source_questions, num_questions=5, include_mark_scheme=True):
    """Add generated questions to a paper that doesn't have any"""
    with app.app_context():
        # Create folder for the paper if it doesn't exist
        paper_dir = os.path.join(get_data_folder(), f'paper_{target_paper.id}')
        if not os.path.exists(paper_dir):
            os.makedirs(paper_dir)
            logger.info(f"Created directory: {paper_dir}")
        
        # Track created items
        questions_created = 0
        mark_schemes_created = 0
        
        # Generate a domain for URLs
        domain = os.environ.get('REPLIT_DEV_DOMAIN') or os.environ.get('REPLIT_DOMAINS', 'localhost:5000').split(',')[0]
        
        # Determine how many source questions we have
        num_source_questions = len(source_questions)
        num_to_generate = min(num_questions, 10)  # Limit to 10 questions max
        
        logger.info(f"Generating {num_to_generate} questions for paper: {target_paper.title} (ID: {target_paper.id})")
        
        # Generate each question
        for i in range(num_to_generate):
            # Use modulo to cycle through available questions if we need more than exist
            source_question = source_questions[i % num_source_questions]
            question_number = i + 1
            
            # Generate unique filenames
            q_filename = f"q{question_number}_{uuid.uuid4().hex}.png"
            q_path = os.path.join(paper_dir, q_filename)
            
            logger.info(f"Creating question {question_number} based on template {source_question.question_number} "
                       f"from paper {source_question.paper_id}")
            
            # Make sure the source file exists
            if not os.path.exists(source_question.image_path):
                logger.warning(f"Source question file doesn't exist: {source_question.image_path}")
                # Skip this question
                continue
            
            # Create mock question
            question_path = create_mock_question(
                source_question.image_path,
                question_number,
                q_path,
                transform_level=3
            )
            
            if question_path:
                # Create entry in database
                marks = random.randint(3, 7) if source_question.marks is None else source_question.marks
                difficulty = random.randint(1, 5) if source_question.difficulty_level is None else source_question.difficulty_level
                
                new_question = Question(
                    question_number=f"q{question_number}",
                    image_path=q_path,
                    image_url=f"https://{domain}/user/question-image/",  # Will be updated with ID
                    paper_id=target_paper.id,
                    marks=marks,
                    difficulty_level=difficulty
                )
                db.session.add(new_question)
                db.session.commit()
                
                # Update image URL with question ID
                new_question.image_url = f"{new_question.image_url}{new_question.id}"
                db.session.commit()
                
                questions_created += 1
                logger.info(f"Created question {question_number} for paper {target_paper.id}")
                
                # Generate mark scheme if requested
                if include_mark_scheme:
                    ms_filename = f"ms{question_number}_{uuid.uuid4().hex}.png"
                    ms_path = os.path.join(paper_dir, ms_filename)
                    
                    # Create mark scheme
                    ms_path = create_mock_mark_scheme(
                        source_ms_path=None,
                        question_number=question_number,
                        output_path=ms_path,
                        transform_level=3
                    )
                    
                    if ms_path:
                        # Add mark scheme as another "question" with MS prefix
                        ms_question = Question(
                            question_number=f"MS{question_number}",
                            image_path=ms_path,
                            image_url=f"https://{domain}/user/question-image/",
                            paper_id=target_paper.id,
                            marks=marks  # Same marks as the question
                        )
                        db.session.add(ms_question)
                        db.session.commit()
                        
                        # Update image URL with question ID
                        ms_question.image_url = f"{ms_question.image_url}{ms_question.id}"
                        db.session.commit()
                        
                        mark_schemes_created += 1
                        logger.info(f"Created mark scheme for question {question_number}")
        
        logger.info(f"Added {questions_created} questions and {mark_schemes_created} mark schemes to paper {target_paper.id}")
        return questions_created, mark_schemes_created

def main():
    """Main function to add questions to empty papers"""
    try:
        # Find empty papers
        empty_papers = find_empty_papers()
        if not empty_papers:
            logger.info("No empty papers found.")
            return
        
        # Find papers with questions to use as templates
        papers_with_questions = find_papers_with_questions()
        if not papers_with_questions:
            logger.error("No papers with questions found to use as templates.")
            return
        
        # Use the paper with the most questions as a template source
        template_paper, template_question_count = papers_with_questions[0]
        logger.info(f"Using paper '{template_paper.title}' with {template_question_count} questions as template source.")
        
        # Get question templates
        source_questions = get_question_templates(template_paper.id)
        if not source_questions:
            logger.error(f"No template questions found in paper {template_paper.id}.")
            return
        
        # Add questions to each empty paper
        total_questions_added = 0
        total_mark_schemes_added = 0
        
        for empty_paper in empty_papers:
            logger.info(f"Processing empty paper: {empty_paper.title} (ID: {empty_paper.id})")
            questions_added, mark_schemes_added = add_questions_to_paper(
                empty_paper, source_questions, num_questions=5, include_mark_scheme=True
            )
            total_questions_added += questions_added
            total_mark_schemes_added += mark_schemes_added
        
        logger.info(f"Complete! Added a total of {total_questions_added} questions and {total_mark_schemes_added} "
                   f"mark schemes to {len(empty_papers)} papers.")
        
    except Exception as e:
        logger.exception(f"Error adding questions to empty papers: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())