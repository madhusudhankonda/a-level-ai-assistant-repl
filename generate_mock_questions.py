"""
Script to generate mock questions based on an existing paper
"""
import os
import random
import shutil
import uuid
import logging
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_data_folder():
    """Get the data folder for storing papers and questions"""
    data_dir = os.path.join(os.getcwd(), 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return data_dir

def get_fonts():
    """Try to load appropriate fonts, or use default if not available"""
    # Try to find system fonts or use default
    try:
        title_font = ImageFont.truetype("Arial.ttf", 24)
        regular_font = ImageFont.truetype("Arial.ttf", 16)
        math_font = ImageFont.truetype("Arial.ttf", 16)
    except IOError:
        # Use default font if Arial not available
        title_font = ImageFont.load_default()
        regular_font = ImageFont.load_default()
        math_font = ImageFont.load_default()
    
    return title_font, regular_font, math_font

def create_mock_question(source_question_path, question_number, output_path, transform_level=2):
    """
    Create a mock question image based on an existing question but with different values.
    
    Args:
        source_question_path: Path to the source question image
        question_number: The question number for the new mock question
        output_path: Path to save the new mock question
        transform_level: How much to transform the question (1=minimal, 5=maximum)
        
    Returns:
        Path to the new mock question image
    """
    try:
        # Load the source question image
        source_img = Image.open(source_question_path)
        width, height = source_img.size
        
        # Create a new blank image with padding
        new_img = Image.new('RGB', (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(new_img)
        
        # Get fonts
        title_font, regular_font, math_font = get_fonts()
        
        # Add question number and a modified version of original content
        draw.text((30, 30), f"Question {question_number}", fill=(0, 0, 0), font=title_font)
        
        # Add a disclaimer
        disclaimer_text = (
            "Note: This is an AI-generated mock question for educational purposes. "
            "It may contain errors and should be reviewed by a qualified teacher."
        )
        draw.text((30, height - 40), disclaimer_text, fill=(150, 150, 150), font=regular_font)
        
        # Generate some mathematical content based on transform level
        if transform_level >= 3:
            # Draw some mathematical content
            fig = Figure(figsize=(5, 3), dpi=100)
            ax = fig.add_subplot(111)
            
            # Example: Plot a function (more complex for higher transform levels)
            x = np.linspace(-5, 5, 100)
            
            # Vary the function based on transform level
            if transform_level >= 4:
                # More complex function for higher levels
                a = random.uniform(0.5, 2.0)
                b = random.uniform(0, 2)
                c = random.uniform(-2, 2)
                y = a * np.sin(b * x + c) + 0.1 * x**2
                ax.plot(x, y, 'b-')
                eq_text = f"f(x) = {a:.1f}sin({b:.1f}x + {c:.1f}) + 0.1x²"
            else:
                # Simpler function for lower levels
                a = random.uniform(1, 3)
                b = random.uniform(-2, 2)
                y = a * x + b
                ax.plot(x, y, 'b-')
                eq_text = f"f(x) = {a:.1f}x + {b:.1f}"
            
            # Add grid and labels
            ax.grid(True, linestyle='--', alpha=0.7)
            ax.set_xlabel('x')
            ax.set_ylabel('y')
            ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
            ax.axvline(x=0, color='k', linestyle='-', alpha=0.3)
            
            # Draw equation on the image
            draw.text((30, 80), eq_text, fill=(0, 0, 0), font=math_font)
            
            # Convert matplotlib figure to Image
            canvas = FigureCanvas(fig)
            canvas.draw()
            graph_img = Image.frombytes('RGB', canvas.get_width_height(), canvas.tostring_rgb())
            
            # Resize graph if needed
            graph_width = min(width - 60, 400)
            graph_height = int(graph_width * graph_img.height / graph_img.width)
            graph_img = graph_img.resize((graph_width, graph_height), Image.Resampling.LANCZOS)
            
            # Paste the graph into the image
            new_img.paste(graph_img, (30, 120))
            
            # Add a question related to the graph
            question_y_pos = 120 + graph_height + 20
            
            if transform_level >= 4:
                questions = [
                    f"Find the derivative of f(x) with respect to x.",
                    f"Find the coordinates of all stationary points of f(x).",
                    f"Calculate the area bounded by f(x), the x-axis, and the lines x = 1 and x = 4."
                ]
            else:
                questions = [
                    f"Find the slope of the line f(x).",
                    f"Calculate the y-intercept of f(x).",
                    f"For what value of x does f(x) = 0?"
                ]
            
            # Add 1-3 questions based on transform level
            num_questions = min(transform_level, 3)
            for i in range(num_questions):
                draw.text((30, question_y_pos + i*30), 
                          f"{chr(97+i)}) {random.choice(questions)}", 
                          fill=(0, 0, 0), 
                          font=regular_font)
        else:
            # For lower transform levels, just modify some text or numbers from original
            # Add some basic text
            draw.text((30, 80), "Consider the following expression:", fill=(0, 0, 0), font=regular_font)
            
            # Add a basic equation with random coefficients
            a = random.randint(1, 10)
            b = random.randint(1, 10)
            c = random.randint(1, 10)
            
            equation = f"{a}x² + {b}x + {c} = 0"
            draw.text((30, 120), equation, fill=(0, 0, 0), font=math_font)
            
            # Add a question
            draw.text((30, 180), f"a) Solve the equation {equation}", fill=(0, 0, 0), font=regular_font)
            draw.text((30, 220), f"b) Find the coordinates of the vertex of the graph of y = {a}x² + {b}x + {c}", 
                      fill=(0, 0, 0), font=regular_font)
        
        # Save the new image
        new_img.save(output_path)
        return output_path
        
    except Exception as e:
        logger.error(f"Error creating mock question: {str(e)}")
        return None

def create_mock_mark_scheme(source_ms_path=None, question_number=1, output_path=None, transform_level=2):
    """
    Create a mock mark scheme for a question
    
    Args:
        source_ms_path: Optional path to source mark scheme image
        question_number: The question number for the mark scheme
        output_path: Path to save the new mark scheme
        transform_level: How much to transform (1=minimal, 5=maximum)
        
    Returns:
        Path to the new mark scheme image
    """
    try:
        # Create dimensions
        width, height = 800, 1000
        
        if source_ms_path and os.path.exists(source_ms_path):
            # If we have a source, use its dimensions
            source_img = Image.open(source_ms_path)
            width, height = source_img.size
        
        # Create a new blank image
        new_img = Image.new('RGB', (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(new_img)
        
        # Get fonts
        title_font, regular_font, math_font = get_fonts()
        
        # Add mark scheme title
        draw.text((30, 30), f"Mark Scheme for Question {question_number}", fill=(0, 0, 0), font=title_font)
        
        # Add marking notes based on transform level
        y_pos = 100
        
        # Generate random marks based on transform level
        max_marks = 4 + transform_level  # 5-9 marks based on level
        
        # Different mark scheme content based on transform level
        if transform_level >= 3:
            # For higher transform levels, create a more complex mark scheme
            mark_allocation = [
                ("Method:", "M1", "Correct approach to differentiation"),
                ("Method:", "M1", "Setting derivative equal to zero"),
                ("Accuracy:", "A1", "Correct derivative found"),
                ("Accuracy:", "A1", "Correct stationary points identified"),
                ("Benefit of doubt:", "B1", "Correct justification of nature of stationary points")
            ]
            
            # Use a subset based on max_marks
            mark_allocation = mark_allocation[:max_marks]
            
            for mark_type, mark, description in mark_allocation:
                draw.text((30, y_pos), mark_type, fill=(0, 0, 150), font=regular_font)
                draw.text((110, y_pos), mark, fill=(150, 0, 0), font=regular_font)
                draw.text((160, y_pos), description, fill=(0, 0, 0), font=regular_font)
                y_pos += 40
                
            # Add some worked solution
            y_pos += 20
            draw.text((30, y_pos), "Worked Solution:", fill=(0, 0, 0), font=title_font)
            y_pos += 40
            
            # Add some example calculations
            calculations = [
                "f(x) = asin(bx + c) + 0.1x²",
                "f'(x) = abcos(bx + c) + 0.2x",
                "For stationary points, f'(x) = 0:",
                "abcos(bx + c) + 0.2x = 0",
                "abcos(bx + c) = -0.2x",
                "Solving numerically gives x ≈ 1.42 and x ≈ -2.31"
            ]
            
            for calc in calculations:
                draw.text((30, y_pos), calc, fill=(0, 0, 0), font=math_font)
                y_pos += 30
        else:
            # For lower transform levels, create a simpler mark scheme
            mark_allocation = [
                ("Method:", "M1", "Correct use of quadratic formula"),
                ("Accuracy:", "A1", "Correct values of x"),
                ("Method:", "M1", "Correct approach to finding vertex"),
                ("Accuracy:", "A1", "Correct coordinates of vertex")
            ]
            
            # Use a subset based on max_marks
            mark_allocation = mark_allocation[:max_marks]
            
            for mark_type, mark, description in mark_allocation:
                draw.text((30, y_pos), mark_type, fill=(0, 0, 150), font=regular_font)
                draw.text((110, y_pos), mark, fill=(150, 0, 0), font=regular_font)
                draw.text((160, y_pos), description, fill=(0, 0, 0), font=regular_font)
                y_pos += 40
                
            # Add some worked solution
            y_pos += 20
            draw.text((30, y_pos), "Worked Solution:", fill=(0, 0, 0), font=title_font)
            y_pos += 40
            
            # Add some example calculations
            a = random.randint(1, 5)
            b = random.randint(1, 10)
            c = random.randint(1, 10)
            
            discriminant = b**2 - 4*a*c
            x1 = (-b + discriminant**0.5) / (2*a)
            x2 = (-b - discriminant**0.5) / (2*a)
            
            calculations = [
                f"For {a}x² + {b}x + {c} = 0:",
                f"Using the quadratic formula: x = (-{b} ± √({b}² - 4×{a}×{c})) / (2×{a})",
                f"x = (-{b} ± √{discriminant}) / {2*a}",
                f"x₁ ≈ {x1:.2f}, x₂ ≈ {x2:.2f}"
            ]
            
            for calc in calculations:
                draw.text((30, y_pos), calc, fill=(0, 0, 0), font=math_font)
                y_pos += 30
        
        # Add total marks
        draw.text((30, height - 80), f"Total: {max_marks} marks", fill=(0, 0, 0), font=title_font)
        
        # Add a disclaimer
        disclaimer_text = (
            "Note: This is an AI-generated mock mark scheme for educational purposes. "
            "It may contain errors and should be reviewed by a qualified teacher."
        )
        draw.text((30, height - 40), disclaimer_text, fill=(150, 150, 150), font=regular_font)
        
        # Save the new image
        new_img.save(output_path)
        return output_path
        
    except Exception as e:
        logger.error(f"Error creating mock mark scheme: {str(e)}")
        return None

def generate_mock_paper(source_paper_id, mock_paper_name, num_questions=5, transform_level=2, 
                       include_mark_scheme=True, target_subject="Mathematics", 
                       target_board="Mock Exams", target_category="Synthetic Papers",
                       source_mark_scheme_paper_id=None):
    """
    Generate a complete mock paper based on an existing paper
    
    Args:
        source_paper_id: ID of the source paper
        mock_paper_name: Name for the new mock paper
        num_questions: Number of questions to generate
        transform_level: Level of transformation (1-5)
        include_mark_scheme: Whether to generate mark schemes
        target_subject: Subject for the new paper
        target_board: Exam board for the new paper
        target_category: Category for the new paper
        source_mark_scheme_paper_id: Optional ID of paper containing mark schemes
        
    Returns:
        Dictionary with new paper info and paths to all generated files
    """
    from models import db, QuestionPaper, Question, Subject, ExamBoard, PaperCategory
    
    try:
        # Get the source paper
        source_paper = QuestionPaper.query.get(source_paper_id)
        
        if not source_paper:
            logger.error(f"Source paper ID {source_paper_id} not found")
            return {"success": False, "error": f"Source paper ID {source_paper_id} not found"}
        
        # Get source questions
        source_questions = Question.query.filter_by(paper_id=source_paper_id).order_by(Question.question_number).all()
        
        if not source_questions:
            logger.error(f"No source questions found for paper ID {source_paper_id}")
            return {"success": False, "error": f"No source questions found for paper ID {source_paper_id}"}
        
        # If specified, get source mark scheme paper and questions
        source_ms_questions = []
        if source_mark_scheme_paper_id:
            source_ms_paper = QuestionPaper.query.get(source_mark_scheme_paper_id)
            if source_ms_paper:
                source_ms_questions = Question.query.filter_by(paper_id=source_mark_scheme_paper_id).order_by(Question.question_number).all()
        
        # Find or create the target subject
        subject = Subject.query.filter_by(name=target_subject).first()
        if not subject:
            logger.warning(f"Subject '{target_subject}' not found, creating it")
            subject = Subject(name=target_subject)
            db.session.add(subject)
            db.session.commit()
        
        # Find or create the target exam board
        board = ExamBoard.query.filter_by(name=target_board, subject_id=subject.id).first()
        if not board:
            logger.warning(f"Exam board '{target_board}' not found for subject {subject.id}, creating it")
            board = ExamBoard(name=target_board, subject_id=subject.id)
            db.session.add(board)
            db.session.commit()
        
        # Find or create the target category
        category = PaperCategory.query.filter_by(name=target_category, board_id=board.id).first()
        if not category:
            logger.warning(f"Category '{target_category}' not found for board {board.id}, creating it")
            category = PaperCategory(name=target_category, board_id=board.id)
            db.session.add(category)
            db.session.commit()
        
        # Create a new mock paper
        current_year = datetime.now().year
        mock_paper = QuestionPaper(
            title=mock_paper_name,
            subject=subject.name,
            exam_period=f"Mock {current_year}",
            paper_type="Mock",
            description=f"AI-generated mock paper based on {source_paper.title}",
            category_id=category.id
        )
        db.session.add(mock_paper)
        db.session.commit()
        
        # Create folder for the new paper
        paper_dir = os.path.join(get_data_folder(), f'paper_{mock_paper.id}')
        if not os.path.exists(paper_dir):
            os.makedirs(paper_dir)
        
        # Generate questions
        questions_created = 0
        generated_items = {"questions": [], "mark_schemes": []}
        domain = os.environ.get('REPLIT_DEV_DOMAIN') or os.environ.get('REPLIT_DOMAINS', 'localhost:5000').split(',')[0]

        # Determine how many source questions we have and can use
        num_source_questions = len(source_questions)
        num_to_generate = min(num_questions, num_source_questions)
        
        for i in range(num_to_generate):
            # Use modulo to cycle through available questions if we need more than exist
            source_question = source_questions[i % num_source_questions]
            question_number = i + 1
            
            # Generate unique filenames
            q_filename = f"mock_q{question_number}_{uuid.uuid4().hex}.png"
            q_path = os.path.join(paper_dir, q_filename)
            
            # Create mock question
            question_path = create_mock_question(
                source_question.image_path, 
                question_number, 
                q_path,
                transform_level
            )
            
            if question_path:
                # Create entry in database
                marks = random.randint(3, 7) if source_question.marks is None else source_question.marks
                difficulty = random.randint(1, 5) if source_question.difficulty_level is None else source_question.difficulty_level
                
                new_question = Question(
                    question_number=question_number,
                    image_path=q_path,
                    image_url=f"https://{domain}/user/question-image/",  # Will be updated with ID
                    paper_id=mock_paper.id,
                    marks=marks,
                    difficulty_level=difficulty
                )
                db.session.add(new_question)
                db.session.commit()
                
                # Update image URL with question ID
                new_question.image_url = f"{new_question.image_url}{new_question.id}"
                db.session.commit()
                
                questions_created += 1
                generated_items["questions"].append({
                    "id": new_question.id,
                    "number": question_number,
                    "path": q_path,
                    "url": new_question.image_url
                })
                
                # Generate mark scheme if requested
                if include_mark_scheme:
                    ms_filename = f"mock_ms{question_number}_{uuid.uuid4().hex}.png"
                    ms_path = os.path.join(paper_dir, ms_filename)
                    
                    # Find corresponding mark scheme from source if available
                    source_ms_path = None
                    if source_ms_questions:
                        # Try to find mark scheme with matching question number
                        for ms_q in source_ms_questions:
                            if ms_q.question_number == source_question.question_number:
                                source_ms_path = ms_q.image_path
                                break
                    
                    # Create mark scheme
                    ms_path = create_mock_mark_scheme(
                        source_ms_path,
                        question_number,
                        ms_path,
                        transform_level
                    )
                    
                    if ms_path:
                        # Add mark scheme as another "question" with MS prefix
                        ms_question = Question(
                            question_number=f"MS{question_number}",
                            image_path=ms_path,
                            image_url=f"https://{domain}/user/question-image/",
                            paper_id=mock_paper.id,
                            marks=marks  # Same marks as the question
                        )
                        db.session.add(ms_question)
                        db.session.commit()
                        
                        # Update image URL with question ID
                        ms_question.image_url = f"{ms_question.image_url}{ms_question.id}"
                        db.session.commit()
                        
                        generated_items["mark_schemes"].append({
                            "id": ms_question.id,
                            "number": f"MS{question_number}",
                            "path": ms_path,
                            "url": ms_question.image_url
                        })
        
        # Return results
        return {
            "success": True,
            "paper_id": mock_paper.id,
            "paper_title": mock_paper.title,
            "questions_created": questions_created,
            "mark_schemes_created": len(generated_items["mark_schemes"]),
            "generated_items": generated_items
        }
        
    except Exception as e:
        logger.error(f"Error generating mock paper: {str(e)}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    print("This script is intended to be imported, not run directly.")