#!/usr/bin/env python3
"""
Script to create synthetic mock questions similar to existing questions but with different values
"""
import os
import sys
import uuid
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io
import textwrap

# Add the current directory to sys.path to ensure imports work
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import app, db
from models import Question, QuestionPaper, PaperCategory, ExamBoard, Subject

def create_triangle_problem():
    """
    Create a synthetic mock question similar to the triangle question (q1)
    but with different values
    """
    # Create a blank image (white background)
    width, height = 900, 400
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # Try to use a standard font, or default if not available
    try:
        # Try to find a suitable font
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
        if os.path.exists(font_path):
            question_font = ImageFont.truetype(font_path, 16)
            header_font = ImageFont.truetype(font_path, 18)
            question_number_font = ImageFont.truetype(font_path, 20)
        else:
            # On systems where specific fonts aren't available
            question_font = ImageFont.load_default()
            header_font = ImageFont.load_default()
            question_number_font = ImageFont.load_default()
    except Exception as e:
        print(f"Font error: {e}")
        question_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        question_number_font = ImageFont.load_default()
    
    # Draw question number
    draw.text((20, 20), "1", font=question_number_font, fill=(0, 0, 0))
    
    # New question text with different values
    question_text = "In the triangle PQR, the length PQ = 8 cm, the length PR = 12 cm and the angle QPR = 45°."
    
    # Draw the question text
    y = 20
    lines = textwrap.wrap(question_text, width=80)
    for line in lines:
        draw.text((50, y), line, font=question_font, fill=(0, 0, 0))
        y += 30
    
    # Draw part (a)
    y += 20
    draw.text((50, y), "(a) Calculate the length QR.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[2]", font=question_font, fill=(0, 0, 0))
    
    # Add second part with point S
    y += 40
    second_part = "S is the point on PR such that the length QS = 5 cm."
    draw.text((50, y), second_part, font=question_font, fill=(0, 0, 0))
    
    # Draw part (b)
    y += 40
    draw.text((50, y), "(b) Calculate the possible values of the angle PQS.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[3]", font=question_font, fill=(0, 0, 0))
    
    # Save the image
    os.makedirs("data/synthetic", exist_ok=True)
    image_path = f"data/synthetic/mock_triangle_question_{uuid.uuid4().hex[:8]}.png"
    image.save(image_path)
    print(f"Created synthetic question at: {image_path}")
    
    return image_path

def create_quadratic_problem():
    """
    Create a synthetic mock question about solving a quadratic equation
    """
    # Create a blank image (white background)
    width, height = 900, 300
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # Try to use a standard font, or default if not available
    try:
        # Try to find a suitable font
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
        if os.path.exists(font_path):
            question_font = ImageFont.truetype(font_path, 16)
            header_font = ImageFont.truetype(font_path, 18)
            question_number_font = ImageFont.truetype(font_path, 20)
        else:
            # On systems where specific fonts aren't available
            question_font = ImageFont.load_default()
            header_font = ImageFont.load_default()
            question_number_font = ImageFont.load_default()
    except Exception as e:
        print(f"Font error: {e}")
        question_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        question_number_font = ImageFont.load_default()
    
    # Draw question number
    draw.text((20, 20), "2", font=question_number_font, fill=(0, 0, 0))
    
    # Question text
    question_text = "Solve the quadratic equation 2x² + 5x - 3 = 0, giving your answers to 3 significant figures where appropriate."
    
    # Draw the question text
    y = 20
    lines = textwrap.wrap(question_text, width=80)
    for line in lines:
        draw.text((50, y), line, font=question_font, fill=(0, 0, 0))
        y += 30
    
    # Add marks
    draw.text((850, 20), "[3]", font=question_font, fill=(0, 0, 0))
    
    # Save the image
    os.makedirs("data/synthetic", exist_ok=True)
    image_path = f"data/synthetic/mock_quadratic_question_{uuid.uuid4().hex[:8]}.png"
    image.save(image_path)
    print(f"Created synthetic question at: {image_path}")
    
    return image_path

def create_differentiation_problem():
    """
    Create a synthetic mock question about differentiation
    """
    # Create a blank image (white background)
    width, height = 900, 350
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # Try to use a standard font, or default if not available
    try:
        # Try to find a suitable font
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
        if os.path.exists(font_path):
            question_font = ImageFont.truetype(font_path, 16)
            header_font = ImageFont.truetype(font_path, 18)
            question_number_font = ImageFont.truetype(font_path, 20)
        else:
            # On systems where specific fonts aren't available
            question_font = ImageFont.load_default()
            header_font = ImageFont.load_default()
            question_number_font = ImageFont.load_default()
    except Exception as e:
        print(f"Font error: {e}")
        question_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        question_number_font = ImageFont.load_default()
    
    # Draw question number
    draw.text((20, 20), "3", font=question_number_font, fill=(0, 0, 0))
    
    # Question text
    question_text = "A curve has equation y = 3x³ - 12x² + 15x - 7"
    
    # Draw the question text
    y = 20
    draw.text((50, y), question_text, font=question_font, fill=(0, 0, 0))
    
    # Draw part (a)
    y += 40
    draw.text((50, y), "(a) Find the coordinates of the stationary points on the curve.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[5]", font=question_font, fill=(0, 0, 0))
    
    # Draw part (b)
    y += 40
    draw.text((50, y), "(b) Determine the nature of each stationary point.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[2]", font=question_font, fill=(0, 0, 0))
    
    # Draw part (c)
    y += 40
    draw.text((50, y), "(c) Find the equation of the normal to the curve at the point where x = 1.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[4]", font=question_font, fill=(0, 0, 0))
    
    # Save the image
    os.makedirs("data/synthetic", exist_ok=True)
    image_path = f"data/synthetic/mock_differentiation_{uuid.uuid4().hex[:8]}.png"
    image.save(image_path)
    print(f"Created synthetic question at: {image_path}")
    
    return image_path

def create_mock_paper():
    """Create a new mock paper with synthetic questions"""
    with app.app_context():
        # Find the Mathematics subject
        math_subject = Subject.query.filter_by(name='Mathematics').first()
        if not math_subject:
            print("Mathematics subject not found, creating it...")
            math_subject = Subject(name='Mathematics', description='A-Level Mathematics')
            db.session.add(math_subject)
            db.session.commit()
        
        # Find or create the "Mock Exams" exam board
        mock_board = ExamBoard.query.filter_by(name='Mock Exams', subject_id=math_subject.id).first()
        if not mock_board:
            print("Creating Mock Exams board...")
            mock_board = ExamBoard(name='Mock Exams', subject_id=math_subject.id, description='Practice and Mock Examinations')
            db.session.add(mock_board)
            db.session.commit()
        
        # Find or create "Synthetic Papers" category
        mock_category = PaperCategory.query.filter_by(name='Synthetic Papers', board_id=mock_board.id).first()
        if not mock_category:
            print("Creating Synthetic Papers category...")
            mock_category = PaperCategory(name='Synthetic Papers', board_id=mock_board.id, description='Computer-generated practice questions')
            db.session.add(mock_category)
            db.session.commit()
        
        # Create a new paper
        paper_title = f"Mock Mathematics Paper {datetime.now().strftime('%B %Y')}"
        mock_paper = QuestionPaper(
            title=paper_title,
            category_id=mock_category.id,
            subject='Mathematics',
            exam_period=f"Practice {datetime.now().strftime('%B %Y')}",
            paper_type='Mock QP',
            description='This paper contains synthetic questions for practice'
        )
        db.session.add(mock_paper)
        db.session.commit()
        
        print(f"Created mock paper: {paper_title}")
        
        # Create synthetic questions
        question_paths = []
        
        # Create a triangle problem (similar to the one shown)
        triangle_path = create_triangle_problem()
        question_paths.append({"number": "q1", "path": triangle_path, "marks": 5})
        
        # Create a quadratic equation problem
        quadratic_path = create_quadratic_problem()
        question_paths.append({"number": "q2", "path": quadratic_path, "marks": 3})
        
        # Create a differentiation problem
        diff_path = create_differentiation_problem()
        question_paths.append({"number": "q3", "path": diff_path, "marks": 11})
        
        # Add questions to the paper
        for q_data in question_paths:
            new_question = Question(
                paper_id=mock_paper.id,
                question_number=q_data["number"],
                image_path=q_data["path"],
                marks=q_data["marks"]
            )
            db.session.add(new_question)
        
        db.session.commit()
        print(f"Successfully added {len(question_paths)} questions to the mock paper")
        
        return mock_paper.id, len(question_paths)

if __name__ == "__main__":
    paper_id, question_count = create_mock_paper()
    print(f"Mock paper created with ID {paper_id} containing {question_count} questions")