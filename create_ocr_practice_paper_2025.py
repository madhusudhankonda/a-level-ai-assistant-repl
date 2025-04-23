#!/usr/bin/env python3
"""
Script to create "OCR Pure Maths Practice Paper 2025-1" with original mock questions
based on the OCR Pure Mathematics paper style.
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

# Create directory for OCR practice paper
PAPER_DIR = "data/ocr_practice_2025"
os.makedirs(PAPER_DIR, exist_ok=True)

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

def create_q1_vector_geometry():
    """Create a question on vector geometry (replaces Q4 in original paper)"""
    # Create a blank image
    width, height = 900, 500
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # Get fonts
    question_font, header_font, question_number_font = get_fonts()
    
    # Draw question number
    draw.text((20, 20), "1", font=question_number_font, fill=(0, 0, 0))
    
    # Question text
    y = 20
    draw.text((50, y), "Consider a parallelogram PQRS. The position vector of P is 2i - 3j, and the position vector of Q is 5i + j.", font=question_font, fill=(0, 0, 0))
    
    # Draw part (a)
    y += 50
    draw.text((50, y), "(a) Find the length PQ.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[1]", font=question_font, fill=(0, 0, 0))
    
    # Draw part (b)
    y += 50
    draw.text((50, y), "(b) The position vector of R is 8i + 4j.", font=question_font, fill=(0, 0, 0))
    
    y += 30
    draw.text((75, y), "(i) Show that PQRS must be a parallelogram.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[2]", font=question_font, fill=(0, 0, 0))
    
    y += 30
    draw.text((75, y), "(ii) Find the position vector of S.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[2]", font=question_font, fill=(0, 0, 0))
    
    # Draw part (c)
    y += 50
    draw.text((50, y), "(c) The diagonals of the parallelogram intersect at point X.", font=question_font, fill=(0, 0, 0))
    
    y += 30
    draw.text((75, y), "Find the position vector of X.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[3]", font=question_font, fill=(0, 0, 0))
    
    # Draw part (d)
    y += 50
    draw.text((50, y), "(d) Calculate the area of the parallelogram PQRS.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[2]", font=question_font, fill=(0, 0, 0))
    
    # Save the image
    image_path = f"{PAPER_DIR}/q1_vector_geometry.png"
    image.save(image_path)
    print(f"Created Question 1 at: {image_path}")
    
    return image_path

def create_q2_differentiation():
    """Create a question on differentiation (inspired by original Q3)"""
    # Create a blank image
    width, height = 900, 500
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # Get fonts
    question_font, header_font, question_number_font = get_fonts()
    
    # Draw question number
    draw.text((20, 20), "2", font=question_number_font, fill=(0, 0, 0))
    
    # Draw part (a)
    y = 20
    draw.text((50, y), "(a) Given that g(x) = x³ - 3x, use differentiation from first principles to show that g'(x) = 3x² - 3.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[4]", font=question_font, fill=(0, 0, 0))
    
    # Draw part (b)
    y += 50
    draw.text((50, y), "(b) A curve has equation y = x³ - 3x + 5.", font=question_font, fill=(0, 0, 0))
    
    y += 30
    draw.text((75, y), "(i) Find the coordinates of all stationary points on the curve.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[3]", font=question_font, fill=(0, 0, 0))
    
    y += 30
    draw.text((75, y), "(ii) Determine whether each stationary point is a maximum or minimum.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[2]", font=question_font, fill=(0, 0, 0))
    
    # Draw part (c)
    y += 50
    draw.text((50, y), "(c) The normal to this curve at the point where x = 1 intersects the x-axis at point P.", font=question_font, fill=(0, 0, 0))
    
    y += 30
    draw.text((75, y), "Find the coordinates of P.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[3]", font=question_font, fill=(0, 0, 0))
    
    # Save the image
    image_path = f"{PAPER_DIR}/q2_differentiation.png"
    image.save(image_path)
    print(f"Created Question 2 at: {image_path}")
    
    return image_path

def create_q3_implicit_differentiation():
    """Create a question on implicit differentiation (new question type)"""
    # Create a blank image
    width, height = 900, 400
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # Get fonts
    question_font, header_font, question_number_font = get_fonts()
    
    # Draw question number
    draw.text((20, 20), "3", font=question_number_font, fill=(0, 0, 0))
    
    # Question text
    y = 20
    draw.text((50, y), "The curve C has equation x² + xy + y² = 12.", font=question_font, fill=(0, 0, 0))
    
    # Draw part (a)
    y += 50
    draw.text((50, y), "(a) Find dy/dx in terms of x and y.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[3]", font=question_font, fill=(0, 0, 0))
    
    # Draw part (b)
    y += 50
    draw.text((50, y), "(b) Find the coordinates of the points on the curve where the gradient of the curve is zero.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[3]", font=question_font, fill=(0, 0, 0))
    
    # Draw part (c)
    y += 50
    draw.text((50, y), "(c) The point (2, 2) lies on the curve C. Find the equation of the tangent to C at this point.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[3]", font=question_font, fill=(0, 0, 0))
    
    # Draw part (d)
    y += 50
    draw.text((50, y), "(d) The point (3, k) lies on the curve C. Find the value of k.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[2]", font=question_font, fill=(0, 0, 0))
    
    # Save the image
    image_path = f"{PAPER_DIR}/q3_implicit_differentiation.png"
    image.save(image_path)
    print(f"Created Question 3 at: {image_path}")
    
    return image_path

def create_q4_parametric_equations():
    """Create a question on parametric equations (new question type)"""
    # Create a blank image
    width, height = 900, 450
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # Get fonts
    question_font, header_font, question_number_font = get_fonts()
    
    # Draw question number
    draw.text((20, 20), "4", font=question_number_font, fill=(0, 0, 0))
    
    # Question text
    y = 20
    draw.text((50, y), "A curve C is defined by the parametric equations x = t² - 1, y = t³ - 3t, where t is a parameter.", font=question_font, fill=(0, 0, 0))
    
    # Draw part (a)
    y += 50
    draw.text((50, y), "(a) Find the value of t at the point on C where x = 3.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[2]", font=question_font, fill=(0, 0, 0))
    
    # Draw part (b)
    y += 50
    draw.text((50, y), "(b) Show that dy/dx = (3t² - 3)/(2t).", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[3]", font=question_font, fill=(0, 0, 0))
    
    # Draw part (c)
    y += 50
    draw.text((50, y), "(c) Find the coordinates of all points on the curve C where the tangent is horizontal.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[3]", font=question_font, fill=(0, 0, 0))
    
    # Draw part (d)
    y += 50
    draw.text((50, y), "(d) Find the exact coordinates of the point on curve C where t = 2, and find the equation", font=question_font, fill=(0, 0, 0))
    y += 30
    draw.text((75, y), "of the normal to the curve at this point.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[4]", font=question_font, fill=(0, 0, 0))
    
    # Save the image
    image_path = f"{PAPER_DIR}/q4_parametric_equations.png"
    image.save(image_path)
    print(f"Created Question 4 at: {image_path}")
    
    return image_path

def create_q5_trigonometric_equations():
    """Create a question on trigonometric equations (inspired by original Q7)"""
    # Create a blank image
    width, height = 900, 450
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # Get fonts
    question_font, header_font, question_number_font = get_fonts()
    
    # Draw question number
    draw.text((20, 20), "5", font=question_number_font, fill=(0, 0, 0))
    
    # Draw part (a)
    y = 20
    draw.text((50, y), "(a) Use the formula sin(A + B) = sin A cos B + cos A sin B to show that", font=question_font, fill=(0, 0, 0))
    
    y += 30
    draw.text((75, y), "sin(A - B) = sin A cos B - cos A sin B.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[2]", font=question_font, fill=(0, 0, 0))
    
    # Draw part (b)
    y += 50
    draw.text((50, y), "(b) The function g(θ) is defined as sin(θ + 45°)sin(θ - 45°), where θ is in degrees.", font=question_font, fill=(0, 0, 0))
    
    y += 30
    draw.text((75, y), "Show that g(θ) = sin²θ - 0.5.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[3]", font=question_font, fill=(0, 0, 0))
    
    # Draw part (c)
    y += 50
    draw.text((50, y), "(c) Solve the equation sin(θ + 45°)sin(θ - 45°) = 0 for 0° ≤ θ < 360°.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[3]", font=question_font, fill=(0, 0, 0))
    
    # Draw part (d)
    y += 50
    draw.text((50, y), "(d) Find the maximum value of g(θ) and state the smallest positive value of θ for which", font=question_font, fill=(0, 0, 0))
    y += 30
    draw.text((75, y), "this maximum value occurs.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[3]", font=question_font, fill=(0, 0, 0))
    
    # Save the image
    image_path = f"{PAPER_DIR}/q5_trigonometric_equations.png"
    image.save(image_path)
    print(f"Created Question 5 at: {image_path}")
    
    return image_path

def create_q6_integration_techniques():
    """Create a question on integration techniques"""
    # Create a blank image
    width, height = 900, 500
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # Get fonts
    question_font, header_font, question_number_font = get_fonts()
    
    # Draw question number
    draw.text((20, 20), "6", font=question_number_font, fill=(0, 0, 0))
    
    # Draw part (a)
    y = 20
    draw.text((50, y), "(a) Find ∫(3x² - 2x + 5)dx.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[3]", font=question_font, fill=(0, 0, 0))
    
    # Draw part (b)
    y += 50
    draw.text((50, y), "(b) Evaluate ∫(1 to 3) (3x² - 2x + 5)dx.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[2]", font=question_font, fill=(0, 0, 0))
    
    # Draw part (c)
    y += 50
    draw.text((50, y), "(c) Using the method of integration by parts, find ∫ xe^(2x) dx.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[4]", font=question_font, fill=(0, 0, 0))
    
    # Draw part (d)
    y += 50
    draw.text((50, y), "(d) The region R is bounded by the curve y = 3x² - 2x + 5, the x-axis, and the lines x = 0", font=question_font, fill=(0, 0, 0))
    y += 30
    draw.text((75, y), "and x = 2. Calculate the volume obtained when R is rotated through 360° about the", font=question_font, fill=(0, 0, 0))
    y += 30
    draw.text((75, y), "x-axis.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[4]", font=question_font, fill=(0, 0, 0))
    
    # Save the image
    image_path = f"{PAPER_DIR}/q6_integration_techniques.png"
    image.save(image_path)
    print(f"Created Question 6 at: {image_path}")
    
    return image_path

def create_q7_sequences_and_series():
    """Create a question on sequences and series"""
    # Create a blank image
    width, height = 900, 550
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # Get fonts
    question_font, header_font, question_number_font = get_fonts()
    
    # Draw question number
    draw.text((20, 20), "7", font=question_number_font, fill=(0, 0, 0))
    
    # Draw part (a)
    y = 20
    draw.text((50, y), "(a) Find the sum of the arithmetic series 5 + 11 + 17 + ... + 107.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[3]", font=question_font, fill=(0, 0, 0))
    
    # Draw part (b)
    y += 50
    draw.text((50, y), "(b) A geometric series has first term a and common ratio r, where 0 < r < 1.", font=question_font, fill=(0, 0, 0))
    
    y += 30
    draw.text((75, y), "(i) The sum to infinity of the series is 24 and the sum to infinity of the series obtained", font=question_font, fill=(0, 0, 0))
    y += 30
    draw.text((100, y), "by squaring each term is 16. Find the values of a and r.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[4]", font=question_font, fill=(0, 0, 0))
    
    y += 50
    draw.text((75, y), "(ii) For the values of a and r found in part (i), calculate the sum of the first 10 terms of", font=question_font, fill=(0, 0, 0))
    y += 30
    draw.text((100, y), "the original geometric series. Give your answer correct to 4 decimal places.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[2]", font=question_font, fill=(0, 0, 0))
    
    # Draw part (c)
    y += 50
    draw.text((50, y), "(c) Find the first 4 terms in the binomial expansion of (1 + 2x)^(1/2) in ascending powers of x.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[4]", font=question_font, fill=(0, 0, 0))
    
    # Draw part (d)
    y += 50
    draw.text((50, y), "(d) State the range of values of x for which the expansion in part (c) is valid.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[1]", font=question_font, fill=(0, 0, 0))
    
    # Save the image
    image_path = f"{PAPER_DIR}/q7_sequences_and_series.png"
    image.save(image_path)
    print(f"Created Question 7 at: {image_path}")
    
    return image_path

def create_q8_partial_fractions():
    """Create a question on partial fractions"""
    # Create a blank image
    width, height = 900, 450
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # Get fonts
    question_font, header_font, question_number_font = get_fonts()
    
    # Draw question number
    draw.text((20, 20), "8", font=question_number_font, fill=(0, 0, 0))
    
    # Draw part (a)
    y = 20
    draw.text((50, y), "(a) Express the following in partial fractions:", font=question_font, fill=(0, 0, 0))
    
    y += 30
    draw.text((75, y), "                4x - 5", font=question_font, fill=(0, 0, 0))
    y += 30
    draw.text((75, y), "               ________", font=question_font, fill=(0, 0, 0))
    y += 30
    draw.text((75, y), "               (x-2)(x+3)", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[3]", font=question_font, fill=(0, 0, 0))
    
    # Draw part (b)
    y += 50
    draw.text((50, y), "(b) Hence find ∫(4x - 5)/((x-2)(x+3)) dx, giving your answer in the form A ln|x-2| + B ln|x+3| + C", font=question_font, fill=(0, 0, 0))
    y += 30
    draw.text((75, y), "where A, B, and C are constants to be determined.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[4]", font=question_font, fill=(0, 0, 0))
    
    # Draw part (c)
    y += 50
    draw.text((50, y), "(c) Evaluate ∫(1 to 4) (4x - 5)/((x-2)(x+3)) dx, giving your answer as an exact expression in terms", font=question_font, fill=(0, 0, 0))
    y += 30
    draw.text((75, y), "of natural logarithms.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[3]", font=question_font, fill=(0, 0, 0))
    
    # Save the image
    image_path = f"{PAPER_DIR}/q8_partial_fractions.png"
    image.save(image_path)
    print(f"Created Question 8 at: {image_path}")
    
    return image_path

def create_q9_differential_equations():
    """Create a question on differential equations"""
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
    draw.text((50, y), "A model for the growth of a certain type of bacteria is given by the differential equation", font=question_font, fill=(0, 0, 0))
    
    y += 30
    draw.text((75, y), "dN/dt = kN(M-N)", font=question_font, fill=(0, 0, 0))
    
    y += 30
    draw.text((50, y), "where N is the population size at time t, M is the maximum sustainable population, and k is a positive", font=question_font, fill=(0, 0, 0))
    y += 30
    draw.text((50, y), "constant.", font=question_font, fill=(0, 0, 0))
    
    # Draw part (a)
    y += 50
    draw.text((50, y), "(a) Explain why the growth rate dN/dt is zero when N = 0 or N = M.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[2]", font=question_font, fill=(0, 0, 0))
    
    # Draw part (b)
    y += 50
    draw.text((50, y), "(b) Given that M = 1000 and k = 0.001, find the value of N when the growth rate is at its maximum.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[3]", font=question_font, fill=(0, 0, 0))
    
    # Draw part (c)
    y += 50
    draw.text((50, y), "(c) By separating the variables, or otherwise, solve the differential equation for N in terms of t,", font=question_font, fill=(0, 0, 0))
    y += 30
    draw.text((75, y), "given that N = 200 when t = 0.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[6]", font=question_font, fill=(0, 0, 0))
    
    # Draw part (d)
    y += 50
    draw.text((50, y), "(d) Find the population size when t = 5.", font=question_font, fill=(0, 0, 0))
    draw.text((850, y), "[2]", font=question_font, fill=(0, 0, 0))
    
    # Save the image
    image_path = f"{PAPER_DIR}/q9_differential_equations.png"
    image.save(image_path)
    print(f"Created Question 9 at: {image_path}")
    
    return image_path

def create_ocr_practice_paper():
    """Create a complete OCR Pure Maths Practice Paper 2025-1"""
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
        
        # Find or create "Pure Mathematics" category for OCR
        pure_category = PaperCategory.query.filter_by(name='Pure Mathematics', board_id=ocr_board.id).first()
        if not pure_category:
            print("Creating Pure Mathematics category...")
            pure_category = PaperCategory(name='Pure Mathematics', board_id=ocr_board.id, description='Pure Mathematics papers for OCR')
            db.session.add(pure_category)
            db.session.commit()
        
        # Create the practice paper
        paper_title = "OCR Pure Maths Practice Paper 2025-1"
        practice_paper = QuestionPaper(
            title=paper_title,
            category_id=pure_category.id,
            subject='Mathematics',
            exam_period="Practice 2025",
            paper_type='QP',
            description='Practice paper based on OCR Pure Mathematics style and format'
        )
        db.session.add(practice_paper)
        db.session.commit()
        
        print(f"Created practice paper: {paper_title}")
        
        # Create the various question types
        question_data = [
            {"number": "q1", "path": create_q1_vector_geometry(), "marks": 10},
            {"number": "q2", "path": create_q2_differentiation(), "marks": 12},
            {"number": "q3", "path": create_q3_implicit_differentiation(), "marks": 11},
            {"number": "q4", "path": create_q4_parametric_equations(), "marks": 12},
            {"number": "q5", "path": create_q5_trigonometric_equations(), "marks": 11},
            {"number": "q6", "path": create_q6_integration_techniques(), "marks": 13},
            {"number": "q7", "path": create_q7_sequences_and_series(), "marks": 14},
            {"number": "q8", "path": create_q8_partial_fractions(), "marks": 10},
            {"number": "q9", "path": create_q9_differential_equations(), "marks": 13}
        ]
        
        # Add questions to the paper
        for q_data in question_data:
            new_question = Question(
                paper_id=practice_paper.id,
                question_number=q_data["number"],
                image_path=q_data["path"],
                marks=q_data["marks"]
            )
            db.session.add(new_question)
        
        db.session.commit()
        print(f"Successfully added {len(question_data)} questions to the OCR Practice Paper")
        
        return practice_paper.id, len(question_data)

if __name__ == "__main__":
    paper_id, question_count = create_ocr_practice_paper()
    print(f"OCR Practice Paper 2025-1 created with ID {paper_id} containing {question_count} questions")