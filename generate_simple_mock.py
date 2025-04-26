"""
Script to generate simple mock questions based on an existing paper
This is a lighter-weight version that doesn't rely on heavy image generation
"""
import os
import random
import uuid
import logging
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

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

def create_simple_question(question_number, output_path, topic="Mathematics", transform_level=2):
    """
    Create a simple question image without relying on heavy matplotlib operations
    
    Args:
        question_number: The question number
        output_path: Path to save the new question image
        topic: Math topic for the question
        transform_level: Level of complexity (1-5)
        
    Returns:
        Path to the new question image
    """
    try:
        # Create a blank image
        width, height = 800, 800
        img = Image.new('RGB', (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        # Get fonts
        title_font, regular_font, math_font = get_fonts()
        
        # Add question number
        draw.text((30, 30), f"Question {question_number}", fill=(0, 0, 0), font=title_font)
        
        # Math topics and questions
        math_topics = {
            "Algebra": [
                "Solve the equation: {}x² + {}x + {} = 0",
                "Simplify the expression: {}x² + {}x + {} - {}x - {}",
                "Factor the expression: {}x² - {}",
                "Find the value of x that satisfies: {}x + {} = {}x - {}"
            ],
            "Calculus": [
                "Find the derivative of f(x) = {}x³ + {}x² + {}x + {}",
                "Calculate the integral of f(x) = {}x² + {}x + {} with respect to x",
                "Find the stationary points of f(x) = {}x² - {}x + {}",
                "Determine the nature of the stationary point at x = {} for f(x) = {}x² + {}x + {}"
            ],
            "Trigonometry": [
                "Solve the equation: sin(x) = {} for 0 ≤ x < 2π",
                "Prove the identity: sin²(x) + cos²(x) = 1 using the value x = {}π/{}",
                "Find the value of tan({}) in terms of sin and cos",
                "Calculate the exact value of sin({}π/{})"
            ],
            "Vectors": [
                "Given vectors a = ({}, {}, {}) and b = ({}, {}, {}), find a + b",
                "Calculate the dot product of a = ({}, {}) and b = ({}, {})",
                "Find the magnitude of the vector ({}, {}, {})",
                "Determine if the vectors ({}, {}) and ({}, {}) are parallel"
            ]
        }
        
        # If topic not in our list, default to Algebra
        if topic not in math_topics:
            topic = "Algebra"
            
        # Select a question template
        questions = math_topics[topic]
        question_template = random.choice(questions)
        
        # Generate random values based on transform level
        values = []
        num_placeholders = question_template.count("{}")
        
        for i in range(num_placeholders):
            if transform_level <= 2:
                # Simple numbers for lower transform levels
                values.append(random.randint(1, 10))
            elif transform_level <= 4:
                # More complex numbers for higher transform levels
                values.append(random.randint(-20, 20))
            else:
                # Potentially fractional or more complex for highest level
                if random.random() < 0.3:  # 30% chance of fraction
                    values.append(f"{random.randint(1, 5)}/{random.randint(2, 6)}")
                else:
                    values.append(random.randint(-30, 30))
        
        # Format the question with random values
        question_text = question_template.format(*values)
        
        # Draw the question text
        draw.text((30, 80), f"Topic: {topic}", fill=(0, 0, 150), font=regular_font)
        
        # Break up long questions into multiple lines
        words = question_text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line) + len(word) + 1 <= 60:  # Max 60 chars per line
                if current_line:
                    current_line += " " + word
                else:
                    current_line = word
            else:
                lines.append(current_line)
                current_line = word
                
        if current_line:
            lines.append(current_line)
            
        # Draw each line of the question
        y_pos = 120
        for line in lines:
            draw.text((30, y_pos), line, fill=(0, 0, 0), font=math_font)
            y_pos += 30
        
        # Add marks based on transform level
        marks = transform_level + 1
        draw.text((30, y_pos + 20), f"[{marks} marks]", fill=(0, 0, 0), font=regular_font)
        
        # Add a disclaimer
        disclaimer_text = (
            "Note: This is an AI-generated mock question for educational purposes. "
            "It may contain errors and should be reviewed by a qualified teacher."
        )
        draw.text((30, height - 40), disclaimer_text, fill=(150, 150, 150), font=regular_font)
        
        # Save the image
        img.save(output_path)
        return output_path
    
    except Exception as e:
        logger.error(f"Error creating simple question: {str(e)}")
        return None

def create_simple_mark_scheme(question_number, output_path, topic="Mathematics", transform_level=2):
    """
    Create a simple mark scheme image without relying on heavy matplotlib operations
    
    Args:
        question_number: The question number
        output_path: Path to save the new mark scheme image
        topic: Math topic for the mark scheme
        transform_level: Level of complexity (1-5)
        
    Returns:
        Path to the new mark scheme image
    """
    try:
        # Create a blank image
        width, height = 800, 800
        img = Image.new('RGB', (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        # Get fonts
        title_font, regular_font, math_font = get_fonts()
        
        # Add mark scheme title
        draw.text((30, 30), f"Mark Scheme for Question {question_number}", fill=(0, 0, 0), font=title_font)
        
        # Math topics and mark schemes
        math_topics = {
            "Algebra": [
                "M1: Correct application of quadratic formula",
                "A1: First correct solution x = {:.2f}",
                "A1: Second correct solution x = {:.2f}",
                "M1: Clear logical working shown",
                "Total: {} marks"
            ],
            "Calculus": [
                "M1: Correct use of differentiation rules",
                "A1: Correct derivative found",
                "M1: Setting derivative equal to zero",
                "A1: Correct stationary point(s) at x = {:.2f}",
                "Total: {} marks"
            ],
            "Trigonometry": [
                "M1: Correct approach to solving trigonometric equation",
                "A1: First solution x = {:.2f}",
                "A1: Second solution x = {:.2f}",
                "B1: Correct domain consideration",
                "Total: {} marks"
            ],
            "Vectors": [
                "M1: Correct method for vector calculation",
                "A1: Correct components found",
                "A1: Correct final answer",
                "C1: Clear presentation of working",
                "Total: {} marks"
            ]
        }
        
        # If topic not in our list, default to Algebra
        if topic not in math_topics:
            topic = "Algebra"
            
        # Select a mark scheme template
        mark_scheme_templates = math_topics[topic]
        
        # Generate random values for the template
        x1 = random.uniform(-5, 5)
        x2 = random.uniform(-5, 5)
        
        # Marks based on transform level
        marks = transform_level + 1
        
        # Draw the mark scheme content
        draw.text((30, 80), f"Topic: {topic}", fill=(0, 0, 150), font=regular_font)
        
        y_pos = 120
        for i, template in enumerate(mark_scheme_templates[:-1]):  # Exclude the "Total" line
            if i < marks:  # Only show as many marking points as there are marks
                if "{:.2f}" in template:
                    if i == 1:
                        line = template.format(x1)
                    else:
                        line = template.format(x2)
                else:
                    line = template
                    
                draw.text((30, y_pos), line, fill=(0, 0, 0), font=regular_font)
                y_pos += 30
        
        # Add the total marks line
        draw.text((30, y_pos + 20), mark_scheme_templates[-1].format(marks), fill=(0, 0, 0), font=title_font)
        
        # Add a disclaimer
        disclaimer_text = (
            "Note: This is an AI-generated mock mark scheme for educational purposes. "
            "It may contain errors and should be reviewed by a qualified teacher."
        )
        draw.text((30, height - 40), disclaimer_text, fill=(150, 150, 150), font=regular_font)
        
        # Save the image
        img.save(output_path)
        return output_path
    
    except Exception as e:
        logger.error(f"Error creating simple mark scheme: {str(e)}")
        return None

def generate_simple_mock_paper(source_paper_id, mock_paper_name, num_questions=5, transform_level=2, 
                      include_mark_scheme=True, target_subject="Mathematics", 
                      target_board="Mock Exams", target_category="Synthetic Papers"):
    """
    Generate a simple mock paper without relying on source questions for templates
    
    Args:
        source_paper_id: ID of the source paper (used only for metadata)
        mock_paper_name: Name for the new mock paper
        num_questions: Number of questions to generate
        transform_level: Level of transformation (1-5)
        include_mark_scheme: Whether to generate mark schemes
        target_subject: Subject for the new paper
        target_board: Exam board for the new paper
        target_category: Category for the new paper
        
    Returns:
        Dictionary with new paper info and paths to all generated files
    """
    from models import db, QuestionPaper, Question, Subject, ExamBoard, PaperCategory
    
    try:
        # Get the source paper for metadata only
        source_paper = QuestionPaper.query.get(source_paper_id)
        
        if not source_paper:
            logger.error(f"Source paper ID {source_paper_id} not found")
            return {"success": False, "error": f"Source paper ID {source_paper_id} not found"}
        
        # Topic selection for questions
        math_topics = ["Algebra", "Calculus", "Trigonometry", "Vectors"]
        
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
        
        for question_number in range(1, num_questions + 1):
            # Select a random topic
            topic = random.choice(math_topics)
            
            # Generate unique filenames
            q_filename = f"mock_q{question_number}_{uuid.uuid4().hex}.png"
            q_path = os.path.join(paper_dir, q_filename)
            
            # Create mock question (simple version)
            question_path = create_simple_question(
                question_number, 
                q_path,
                topic,
                transform_level
            )
            
            if question_path:
                # Create entry in database
                marks = transform_level + 1  # Marks based on transform level
                difficulty = transform_level  # Difficulty matches transform level
                
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
                    
                    # Create mark scheme (simple version)
                    ms_path = create_simple_mark_scheme(
                        question_number,
                        ms_path,
                        topic,
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
        logger.error(f"Error generating simple mock paper: {str(e)}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    print("This script is intended to be imported, not run directly.")