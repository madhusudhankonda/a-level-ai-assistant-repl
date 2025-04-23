#!/usr/bin/env python3
"""
Script to create a mock OCR Pure Mathematics paper similar to the June 2023 version
but with different questions and values
"""
import os
import sys
import uuid
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io
import textwrap
import math

# Add the current directory to sys.path to ensure imports work
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import app, db
from models import Question, QuestionPaper, PaperCategory, ExamBoard, Subject

# Create directory for mock OCR paper
MOCK_DIR = "data/mock_ocr"
os.makedirs(MOCK_DIR, exist_ok=True)

def get_fonts():
    """Try to load appropriate fonts, or use default if not available"""
    try:
        # Try to find a suitable font
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                question_font = ImageFont.truetype(font_path, 16)
                header_font = ImageFont.truetype(font_path, 18)
                question_number_font = ImageFont.truetype(font_path, 20)
                return question_font, header_font, question_number_font
                
        # If none of the specific fonts are available
        question_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        question_number_font = ImageFont.load_default()
        return question_font, header_font, question_number_font
    except Exception as e:
        print(f"Font error: {e}")
        question_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        question_number_font = ImageFont.load_default()
        return question_font, header_font, question_number_font

def create_trigonometry_question():
    """Create a question on trigonometry (Question 1)"""
    # Create a blank image
    width, height = 900, 400
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # Get fonts
    question_font, header_font, question_number_font = get_fonts()
    
    # Draw question number
    draw.text((20, 20), "1", font=question_number_font, fill=(0, 0, 0))
    
    # Question text
    question_text = "In the triangle DEF, the length DE = 7 cm, the length DF = 10 cm and the angle EDF = 60°."
    
    # Draw the question text
    y = 20
    lines = textwrap.wrap(question_text, width=80)
    for line in lines:
        draw.text((50, y), line, font=question_font, fill=(0, 0, 0))
        y += 30
    
    # Draw part (a)
    y += 20
    draw.text((50, y), "(a) Calculate the length EF.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[2]", font=question_font, fill=(0, 0, 0))
    
    # Add second part with point G
    y += 40
    second_part = "G is the point on DF such that the length EG = 5 cm."
    draw.text((50, y), second_part, font=question_font, fill=(0, 0, 0))
    
    # Draw part (b)
    y += 40
    draw.text((50, y), "(b) Calculate the possible values of the angle DEG.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[3]", font=question_font, fill=(0, 0, 0))
    
    # Save the image
    image_path = f"{MOCK_DIR}/q1_trigonometry.png"
    image.save(image_path)
    print(f"Created OCR mock question 1 at: {image_path}")
    
    return image_path

def create_algebraic_fractions_question():
    """Create a question on algebraic fractions (Question 2)"""
    # Create a blank image
    width, height = 900, 450
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # Get fonts
    question_font, header_font, question_number_font = get_fonts()
    
    # Draw question number
    draw.text((20, 20), "2", font=question_number_font, fill=(0, 0, 0))
    
    # Draw part (a)
    y = 20
    draw.text((50, y), "(a) (i) Show that", font=question_font, fill=(0, 0, 0))
    
    # Special math expression - we'll describe it in text due to font limitations
    y += 35
    draw.text((100, y), "1           1           a", font=question_font, fill=(0, 0, 0))
    y += 25
    draw.text((90, y), "──────── + ──────── = ─────", font=question_font, fill=(0, 0, 0))
    y += 25
    draw.text((90, y), "4 - 3√x     4 + 3√x     b + cx", font=question_font, fill=(0, 0, 0))
    
    y += 35
    draw.text((100, y), "where a, b and c are constants to be determined.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[2]", font=question_font, fill=(0, 0, 0))
    
    # Draw part (ii)
    y += 40
    draw.text((75, y), "(ii) Hence solve the equation", font=question_font, fill=(0, 0, 0))
    
    y += 35
    draw.text((100, y), "1           1", font=question_font, fill=(0, 0, 0))
    y += 25
    draw.text((90, y), "──────── + ──────── = 3", font=question_font, fill=(0, 0, 0))
    y += 25
    draw.text((90, y), "4 - 3√x     4 + 3√x", font=question_font, fill=(0, 0, 0))
    
    draw.text((850, y - 20), "[2]", font=question_font, fill=(0, 0, 0))
    
    # Draw part (b)
    y += 40
    draw.text((50, y), "(b) In this question you must show detailed reasoning.", font=question_font, fill=(0, 0, 0))
    
    y += 35
    draw.text((75, y), "Solve the equation 3ˣ - 5 × 3ˣ⁻¹ - 6 = 0.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[4]", font=question_font, fill=(0, 0, 0))
    
    # Save the image
    image_path = f"{MOCK_DIR}/q2_algebraic_fractions.png"
    image.save(image_path)
    print(f"Created OCR mock question 2 at: {image_path}")
    
    return image_path

def create_differentiation_question():
    """Create a question on differentiation (Question 3)"""
    # Create a blank image
    width, height = 900, 350
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # Get fonts
    question_font, header_font, question_number_font = get_fonts()
    
    # Draw question number
    draw.text((20, 20), "3", font=question_number_font, fill=(0, 0, 0))
    
    # Question text
    y = 20
    draw.text((50, y), "A curve has equation y = 2x³ - 9x² + 12x - 4", font=question_font, fill=(0, 0, 0))
    
    # Draw part (a)
    y += 40
    draw.text((50, y), "(a) Find the equation of the tangent to the curve at the point where x = 2.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[4]", font=question_font, fill=(0, 0, 0))
    
    # Draw part (b)
    y += 40
    draw.text((50, y), "(b) Find the coordinates of the stationary points of the curve.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[3]", font=question_font, fill=(0, 0, 0))
    
    # Draw part (c)
    y += 40
    draw.text((50, y), "(c) Determine the nature of each stationary point.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[2]", font=question_font, fill=(0, 0, 0))
    
    # Save the image
    image_path = f"{MOCK_DIR}/q3_differentiation.png"
    image.save(image_path)
    print(f"Created OCR mock question 3 at: {image_path}")
    
    return image_path

def create_integration_question():
    """Create a question on integration (Question 4)"""
    # Create a blank image
    width, height = 900, 400
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # Get fonts
    question_font, header_font, question_number_font = get_fonts()
    
    # Draw question number
    draw.text((20, 20), "4", font=question_number_font, fill=(0, 0, 0))
    
    # Draw part (a)
    y = 20
    draw.text((50, y), "(a) Find ∫(2x³ - 5x² + 3x - 1)dx.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[3]", font=question_font, fill=(0, 0, 0))
    
    # Draw part (b)
    y += 40
    draw.text((50, y), "(b) Find the exact value of ∫(0 to 1) (2x³ - 5x² + 3x - 1)dx.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[2]", font=question_font, fill=(0, 0, 0))
    
    # Draw part (c)
    y += 40
    draw.text((50, y), "(c) The shaded region R is bounded by the curve y = 2x³ - 5x² + 3x - 1, the x-axis, and", font=question_font, fill=(0, 0, 0))
    y += 30
    draw.text((75, y), "the lines x = 0 and x = 2. Calculate the volume obtained when R is rotated", font=question_font, fill=(0, 0, 0))
    y += 30
    draw.text((75, y), "through 360° about the x-axis.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[4]", font=question_font, fill=(0, 0, 0))
    
    # Save the image
    image_path = f"{MOCK_DIR}/q4_integration.png"
    image.save(image_path)
    print(f"Created OCR mock question 4 at: {image_path}")
    
    return image_path

def create_modulus_function_question():
    """Create a question on modulus functions (Question 5)"""
    # Create a blank image
    width, height = 900, 500
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # Get fonts
    question_font, header_font, question_number_font = get_fonts()
    
    # Draw question number
    draw.text((20, 20), "5", font=question_number_font, fill=(0, 0, 0))
    
    # Draw part (a)
    y = 20
    draw.text((50, y), "(a) The function f(x) is defined for all values of x as f(x) = |mx - n|, where m and n are positive", font=question_font, fill=(0, 0, 0))
    y += 30
    draw.text((75, y), "constants.", font=question_font, fill=(0, 0, 0))
    
    y += 40
    draw.text((75, y), "(i) The graph of y = f(x) + k, where k is a constant, has a vertex at (4, 2) and crosses the", font=question_font, fill=(0, 0, 0))
    y += 30
    draw.text((90, y), "y-axis at (0, 6).", font=question_font, fill=(0, 0, 0))
    
    y += 40
    draw.text((90, y), "Find the values of m, n and k.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[3]", font=question_font, fill=(0, 0, 0))
    
    y += 40
    draw.text((75, y), "(ii) Explain why f⁻¹(x) does not exist.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[1]", font=question_font, fill=(0, 0, 0))
    
    # Draw part (b)
    y += 40
    draw.text((50, y), "(b) The function g(x) is defined for x ≥ r/s as g(x) = |sx - r|, where s and r are positive", font=question_font, fill=(0, 0, 0))
    y += 30
    draw.text((75, y), "constants.", font=question_font, fill=(0, 0, 0))
    
    y += 40
    draw.text((75, y), "(i) Find, in terms of s and r, an expression for g⁻¹(x), stating the domain of g⁻¹(x).", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[3]", font=question_font, fill=(0, 0, 0))
    
    y += 40
    draw.text((75, y), "(ii) State the set of values of s for which the equation g(x) = g⁻¹(x) has no solutions.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[1]", font=question_font, fill=(0, 0, 0))
    
    # Save the image
    image_path = f"{MOCK_DIR}/q5_modulus_functions.png"
    image.save(image_path)
    print(f"Created OCR mock question 5 at: {image_path}")
    
    return image_path

def create_ecology_modeling_question():
    """Create a question on mathematical modeling in ecology (Question 9)"""
    # Create a blank image
    width, height = 900, 500
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # Get fonts
    question_font, header_font, question_number_font = get_fonts()
    
    # Draw question number
    draw.text((20, 20), "9", font=question_number_font, fill=(0, 0, 0))
    
    # Question text
    y = 20
    draw.text((50, y), "Ecologists are studying how the population of butterflies in a nature reserve varies according", font=question_font, fill=(0, 0, 0))
    y += 30
    draw.text((50, y), "to the number of flowering plants. The study takes place over a series of weeks in the spring.", font=question_font, fill=(0, 0, 0))
    y += 30
    draw.text((50, y), "A model is suggested for the number of butterflies, B, and the number of flowering plants, P,", font=question_font, fill=(0, 0, 0))
    y += 30
    draw.text((50, y), "at time t weeks after the start of the study.", font=question_font, fill=(0, 0, 0))
    
    y += 40
    draw.text((50, y), "In the model B = 15 + 3t + sin 2t and P = 40e^(0.2t).", font=question_font, fill=(0, 0, 0))
    
    y += 40
    draw.text((50, y), "The model assumes that B and P can be treated as continuous variables.", font=question_font, fill=(0, 0, 0))
    
    # Draw part (a)
    y += 40
    draw.text((50, y), "(a) State the meaning of dB/dP.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[1]", font=question_font, fill=(0, 0, 0))
    
    # Draw part (b)
    y += 40
    draw.text((50, y), "(b) Determine dB/dP when t = 3.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[4]", font=question_font, fill=(0, 0, 0))
    
    # Draw part (c)
    y += 40
    draw.text((50, y), "(c) Suggest a reason why this model may not be valid for values of t greater than 10.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[1]", font=question_font, fill=(0, 0, 0))
    
    # Save the image
    image_path = f"{MOCK_DIR}/q9_ecology_modeling.png"
    image.save(image_path)
    print(f"Created OCR mock question 9 at: {image_path}")
    
    return image_path

def create_ocr_mock_paper():
    """Create a complete mock OCR Pure Mathematics paper similar to June 2023"""
    with app.app_context():
        # Find the Mathematics subject
        math_subject = Subject.query.filter_by(name='Mathematics').first()
        if not math_subject:
            print("Mathematics subject not found, creating it...")
            math_subject = Subject(name='Mathematics', description='A-Level Mathematics')
            db.session.add(math_subject)
            db.session.commit()
        
        # Find the OCR board
        ocr_board = ExamBoard.query.filter_by(name='OCR', subject_id=math_subject.id).first()
        if not ocr_board:
            print("OCR board not found, creating it...")
            ocr_board = ExamBoard(name='OCR', subject_id=math_subject.id, description='OCR Examination Board')
            db.session.add(ocr_board)
            db.session.commit()
        
        # Find or create "Mock Pure Mathematics" category for OCR
        mock_category = PaperCategory.query.filter_by(name='Mock Pure Mathematics', board_id=ocr_board.id).first()
        if not mock_category:
            print("Creating Mock Pure Mathematics category...")
            mock_category = PaperCategory(name='Mock Pure Mathematics', board_id=ocr_board.id, description='Mock Pure Mathematics papers')
            db.session.add(mock_category)
            db.session.commit()
        
        # Create the mock paper
        paper_title = f"OCR Mock Pure Mathematics {datetime.now().strftime('%B %Y')}"
        mock_paper = QuestionPaper(
            title=paper_title,
            category_id=mock_category.id,
            subject='Mathematics',
            exam_period=f"Mock {datetime.now().strftime('%B %Y')}",
            paper_type='Mock QP',
            description='This paper contains mock questions based on the OCR June 2023 style'
        )
        db.session.add(mock_paper)
        db.session.commit()
        
        print(f"Created mock paper: {paper_title}")
        
        # Create the various question types
        question_data = [
            {"number": "q1", "path": create_trigonometry_question(), "marks": 5},
            {"number": "q2", "path": create_algebraic_fractions_question(), "marks": 8},
            {"number": "q3", "path": create_differentiation_question(), "marks": 9},
            {"number": "q4", "path": create_integration_question(), "marks": 9},
            {"number": "q5", "path": create_modulus_function_question(), "marks": 8},
            {"number": "q9", "path": create_ecology_modeling_question(), "marks": 6}
        ]
        
        # Add questions to the paper
        for q_data in question_data:
            new_question = Question(
                paper_id=mock_paper.id,
                question_number=q_data["number"],
                image_path=q_data["path"],
                marks=q_data["marks"]
            )
            db.session.add(new_question)
        
        db.session.commit()
        print(f"Successfully added {len(question_data)} questions to the OCR mock paper")
        
        return mock_paper.id, len(question_data)

if __name__ == "__main__":
    paper_id, question_count = create_ocr_mock_paper()
    print(f"OCR mock paper created with ID {paper_id} containing {question_count} questions")