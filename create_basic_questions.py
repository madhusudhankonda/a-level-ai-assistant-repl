#!/usr/bin/env python
"""
Script to create basic text questions for empty papers without relying on matplotlib.
"""

import os
import sys
import logging
import uuid
import random
from flask import current_app
from app import app, db
from models import QuestionPaper, Question, Subject, ExamBoard, PaperCategory
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

def get_empty_papers():
    """Get all papers without questions"""
    with app.app_context():
        all_papers = QuestionPaper.query.all()
        empty_papers = []
        
        for paper in all_papers:
            question_count = Question.query.filter_by(paper_id=paper.id).count()
            if question_count == 0:
                empty_papers.append(paper)
                logger.info(f"Found empty paper: {paper.title} (ID: {paper.id})")
        
        return empty_papers

def get_fonts():
    """Get appropriate fonts for drawing text"""
    try:
        # Try to load system fonts if available
        title_font = ImageFont.truetype("Arial", 36)
        regular_font = ImageFont.truetype("Arial", 20)
        math_font = ImageFont.truetype("Arial", 24)
    except IOError:
        # Fall back to default fonts if system fonts not available
        title_font = ImageFont.load_default()
        regular_font = ImageFont.load_default()
        math_font = ImageFont.load_default()
    
    return title_font, regular_font, math_font

def create_basic_question(question_number, output_path, title, question_text):
    """Create a basic text question image"""
    try:
        # Create a blank image
        width, height = 800, 1000
        image = Image.new('RGB', (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # Get fonts
        title_font, regular_font, math_font = get_fonts()
        
        # Draw the question number and title
        draw.text((30, 30), f"Question {question_number}", fill=(0, 0, 0), font=title_font)
        
        # Draw the question title
        y_pos = 100
        draw.text((30, y_pos), title, fill=(0, 0, 0), font=math_font)
        
        # Draw the question text with line wrapping
        y_pos = 160
        lines = question_text.split('\n')
        for line in lines:
            # Simple word wrapping
            words = line.split()
            if not words:
                y_pos += 30
                continue
                
            current_line = words[0]
            for word in words[1:]:
                # Check if adding this word would exceed the width
                test_line = current_line + " " + word
                # Approximate width check
                if len(test_line) * 12 > width - 60:  # Rough estimation of text width
                    draw.text((30, y_pos), current_line, fill=(0, 0, 0), font=regular_font)
                    y_pos += 30
                    current_line = word
                else:
                    current_line += " " + word
            
            draw.text((30, y_pos), current_line, fill=(0, 0, 0), font=regular_font)
            y_pos += 30
        
        # Draw a box for the answer
        box_top = max(y_pos + 50, 400)
        draw.rectangle([(30, box_top), (width - 30, box_top + 300)], outline=(0, 0, 0), width=2)
        draw.text((30, box_top + 10), "Answer:", fill=(0, 0, 0), font=regular_font)
        
        # Add marks
        marks = random.randint(3, 8)
        draw.text((width - 80, 30), f"[{marks} marks]", fill=(0, 0, 0), font=regular_font)
        
        # Add a disclaimer
        disclaimer_text = (
            "Note: This is an AI-generated question for educational purposes. "
            "It may contain errors and should be reviewed by a qualified teacher."
        )
        draw.text((30, height - 40), disclaimer_text, fill=(150, 150, 150), font=ImageFont.load_default())
        
        # Save the image
        image.save(output_path)
        return output_path, marks
        
    except Exception as e:
        logger.error(f"Error creating question: {str(e)}")
        return None, 0

def create_basic_mark_scheme(question_number, output_path, title, answer_text, marks):
    """Create a basic text mark scheme image"""
    try:
        # Create a blank image
        width, height = 800, 1000
        image = Image.new('RGB', (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # Get fonts
        title_font, regular_font, math_font = get_fonts()
        
        # Draw the mark scheme header
        draw.text((30, 30), f"Mark Scheme - Question {question_number}", fill=(0, 0, 0), font=title_font)
        
        # Draw the question title
        y_pos = 100
        draw.text((30, y_pos), title, fill=(0, 0, 0), font=math_font)
        
        # Draw the answer with line wrapping
        y_pos = 160
        lines = answer_text.split('\n')
        for line in lines:
            words = line.split()
            if not words:
                y_pos += 30
                continue
                
            current_line = words[0]
            for word in words[1:]:
                test_line = current_line + " " + word
                if len(test_line) * 12 > width - 60:
                    draw.text((30, y_pos), current_line, fill=(0, 0, 0), font=regular_font)
                    y_pos += 30
                    current_line = word
                else:
                    current_line += " " + word
            
            draw.text((30, y_pos), current_line, fill=(0, 0, 0), font=regular_font)
            y_pos += 30
        
        # Add marking scheme
        y_pos = max(y_pos + 50, 500)
        draw.text((30, y_pos), "Mark Allocation:", fill=(0, 0, 0), font=title_font)
        y_pos += 50
        
        # Create mark allocation based on total marks
        mark_allocation = []
        remaining_marks = marks
        
        while remaining_marks > 0:
            if remaining_marks >= 2:
                mark = 2
            else:
                mark = 1
                
            if mark == 2:
                mark_allocation.append(("Method:", "M2", "Correct approach with working shown"))
            elif random.choice([True, False]):
                mark_allocation.append(("Accuracy:", "A1", "Correct final answer"))
            else:
                mark_allocation.append(("Method:", "M1", "Partial approach shown"))
                
            remaining_marks -= mark
        
        for mark_type, mark, description in mark_allocation:
            draw.text((30, y_pos), mark_type, fill=(0, 0, 150), font=regular_font)
            draw.text((110, y_pos), mark, fill=(150, 0, 0), font=regular_font)
            draw.text((160, y_pos), description, fill=(0, 0, 0), font=regular_font)
            y_pos += 30
        
        # Add total marks
        y_pos += 20
        draw.text((30, y_pos), f"Total: {marks} marks", fill=(0, 0, 0), font=math_font)
        
        # Add a disclaimer
        disclaimer_text = (
            "Note: This is an AI-generated mark scheme for educational purposes. "
            "It may contain errors and should be reviewed by a qualified teacher."
        )
        draw.text((30, height - 40), disclaimer_text, fill=(150, 150, 150), font=ImageFont.load_default())
        
        # Save the image
        image.save(output_path)
        return output_path
        
    except Exception as e:
        logger.error(f"Error creating mark scheme: {str(e)}")
        return None

def create_question_set(paper_id, num_questions=5):
    """Create a set of basic questions for a paper"""
    with app.app_context():
        paper = QuestionPaper.query.get(paper_id)
        if not paper:
            logger.error(f"Paper with ID {paper_id} not found")
            return 0, 0
        
        # Create folder for the paper if it doesn't exist
        paper_dir = os.path.join(get_data_folder(), f'paper_{paper_id}')
        if not os.path.exists(paper_dir):
            os.makedirs(paper_dir)
            logger.info(f"Created directory: {paper_dir}")
        
        # Generate a domain for URLs
        domain = os.environ.get('REPLIT_DEV_DOMAIN') or os.environ.get('REPLIT_DOMAINS', 'localhost:5000').split(',')[0]
        
        # Generate questions
        questions_created = 0
        mark_schemes_created = 0
        
        # Define some question templates based on paper subjects
        math_questions = [
            {
                "title": "Differentiation",
                "text": "Find the derivative of the following function with respect to x:\n\nf(x) = 3x^2 + 2x - 5\n\nShow all steps of your working."
            },
            {
                "title": "Algebraic Fractions",
                "text": "Simplify the following algebraic fraction:\n\n(x^2 - 4) / (x - 2)\n\nState any restrictions on the values of x."
            },
            {
                "title": "Trigonometry",
                "text": "Solve the equation:\n\n2sin(x) = cos(x) for 0° ≤ x ≤ 360°\n\nGive your answers in degrees, correct to 1 decimal place."
            },
            {
                "title": "Integration",
                "text": "Evaluate the following integral:\n\n∫(2x + 3)dx between the limits x = 1 and x = 4\n\nShow all steps of your working."
            },
            {
                "title": "Sequences",
                "text": "Consider the arithmetic sequence:\n\n5, 8, 11, 14, ...\n\nFind the 20th term of this sequence and the sum of the first 20 terms."
            },
            {
                "title": "Quadratic Equations",
                "text": "Solve the quadratic equation:\n\n2x^2 - 5x - 3 = 0\n\nGive your answers in exact form."
            },
            {
                "title": "Vectors",
                "text": "Given vectors a = (2, 3, -1) and b = (1, -2, 4):\n\n(a) Find a + b\n(b) Find the magnitude of a\n(c) Find the scalar product a·b"
            },
            {
                "title": "Binomial Expansion",
                "text": "Expand (1 + 2x)^4 and simplify your answer.\n\nState the range of values of x for which the expansion is valid."
            },
            {
                "title": "Logarithms",
                "text": "Solve the equation:\n\nlog₂(x) + log₂(x+3) = 3\n\nGive your answer as an exact value."
            },
            {
                "title": "Functions",
                "text": "The function f is defined by f: x → 2x - 3, for x ∈ ℝ.\n\n(a) Find the range of f.\n(b) Find an expression for f⁻¹(x).\n(c) State the domain of f⁻¹."
            }
        ]
        
        # Answer templates
        math_answers = [
            {
                "title": "Differentiation",
                "text": "To find the derivative of f(x) = 3x^2 + 2x - 5, we apply the differentiation rules:\n\nFor 3x^2, the power rule gives us: 3 × 2x^(2-1) = 6x\nFor 2x, the power rule gives us: 2 × 1x^(1-1) = 2\nFor -5, the derivative of a constant is 0\n\nTherefore, f'(x) = 6x + 2"
            },
            {
                "title": "Algebraic Fractions",
                "text": "For (x^2 - 4) / (x - 2), we can factorize the numerator:\nx^2 - 4 = (x + 2)(x - 2)\n\nSo we have: (x + 2)(x - 2) / (x - 2)\n\nCanceling the common factor (x - 2):\n(x^2 - 4) / (x - 2) = x + 2\n\nRestriction: x ≠ 2 (as this would make the denominator zero)"
            },
            {
                "title": "Trigonometry",
                "text": "For 2sin(x) = cos(x):\n\nRearranging to standard form: 2sin(x) - cos(x) = 0\n\nWe can use the identity: cos(x) = sin(x + 90°)\nSo: 2sin(x) - sin(x + 90°) = 0\n\nThis can be solved using the formula R sin(x - α) where:\nR = √(2^2 + 1^2) = √5\nα = tan^-1(1/2) ≈ 26.6°\n\nSo we get: √5 sin(x - 26.6°) = 0\n\nThis is satisfied when x - 26.6° = 0° or 180°\nTherefore x = 26.6° or x = 206.6°\n\nWithin the range 0° ≤ x ≤ 360°, the solutions are x = 26.6° and x = 206.6°"
            },
            {
                "title": "Integration",
                "text": "To evaluate ∫(2x + 3)dx between x = 1 and x = 4:\n\nIntegrating 2x: ∫2x dx = x^2 + C\nIntegrating 3: ∫3 dx = 3x + C\n\nSo ∫(2x + 3)dx = x^2 + 3x + C\n\nEvaluating between limits:\n[x^2 + 3x]_1^4\n= (4^2 + 3×4) - (1^2 + 3×1)\n= (16 + 12) - (1 + 3)\n= 28 - 4\n= 24"
            },
            {
                "title": "Sequences",
                "text": "For the arithmetic sequence 5, 8, 11, 14, ...\n\nWe identify that the common difference d = 3\nThe first term a = 5\n\nFor the nth term formula: a_n = a + (n-1)d\nThe 20th term a_20 = 5 + (20-1)×3 = 5 + 19×3 = 5 + 57 = 62\n\nFor the sum of the first n terms of an arithmetic sequence: S_n = n/2 × (a + l)\nwhere l is the last term (in this case a_20 = 62)\n\nS_20 = 20/2 × (5 + 62) = 10 × 67 = 670"
            }
        ]
        
        # Use appropriate question templates
        questions = math_questions
        answers = math_answers
        
        # Generate each question
        for i in range(1, num_questions + 1):
            # Select a random question template
            question_template = random.choice(questions)
            title = question_template["title"]
            text = question_template["text"]
            
            # Create unique question number
            qnum = f"{i}"
            
            # Generate filenames
            q_filename = f"q{qnum}_{uuid.uuid4().hex[:8]}.png"
            q_path = os.path.join(paper_dir, q_filename)
            
            logger.info(f"Creating question {i} for paper {paper_id}: {title}")
            
            # Create the question image
            question_path, marks = create_basic_question(i, q_path, title, text)
            
            if question_path:
                # Create entry in database
                new_question = Question(
                    question_number=f"q{i}",
                    image_path=q_path,
                    image_url=f"https://{domain}/user/question-image/",  # Will be updated with ID
                    paper_id=paper_id,
                    marks=marks,
                    difficulty_level=random.randint(1, 5)
                )
                db.session.add(new_question)
                db.session.commit()
                
                # Update image URL with question ID
                new_question.image_url = f"{new_question.image_url}{new_question.id}"
                db.session.commit()
                
                questions_created += 1
                logger.info(f"Created question {i} for paper {paper_id}")
                
                # Create mark scheme
                # Find a matching answer if possible, otherwise use a generic one
                answer_template = next(
                    (a for a in answers if a["title"] == title),
                    random.choice(answers)
                )
                
                ms_filename = f"ms{qnum}_{uuid.uuid4().hex[:8]}.png"
                ms_path = os.path.join(paper_dir, ms_filename)
                
                ms_path = create_basic_mark_scheme(
                    i, ms_path, title, answer_template["text"], marks
                )
                
                if ms_path:
                    # Add mark scheme as another "question" with MS prefix
                    ms_question = Question(
                        question_number=f"MS{i}",
                        image_path=ms_path,
                        image_url=f"https://{domain}/user/question-image/",
                        paper_id=paper_id,
                        marks=marks  # Same marks as the question
                    )
                    db.session.add(ms_question)
                    db.session.commit()
                    
                    # Update image URL with question ID
                    ms_question.image_url = f"{ms_question.image_url}{ms_question.id}"
                    db.session.commit()
                    
                    mark_schemes_created += 1
                    logger.info(f"Created mark scheme for question {i}")
        
        logger.info(f"Added {questions_created} questions and {mark_schemes_created} mark schemes to paper {paper_id}")
        return questions_created, mark_schemes_created

def main():
    """Main function to add questions to empty papers"""
    try:
        # Find empty papers
        empty_papers = get_empty_papers()
        if not empty_papers:
            logger.info("No empty papers found.")
            return
        
        # Add questions to each empty paper
        total_questions_added = 0
        total_mark_schemes_added = 0
        
        for paper in empty_papers:
            logger.info(f"Processing empty paper: {paper.title} (ID: {paper.id})")
            questions_added, mark_schemes_added = create_question_set(paper.id, num_questions=5)
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