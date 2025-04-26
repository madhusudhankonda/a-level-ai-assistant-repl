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
    # Always use default font to avoid font loading issues in a server environment
    title_font = ImageFont.load_default()
    regular_font = ImageFont.load_default()
    math_font = ImageFont.load_default()
    
    # Log the font usage
    logger.info("Using default fonts for image generation")
    
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
        # Create a blank image with a slightly randomized size for visual diversity
        base_width, base_height = 800, 800
        width_variance = random.randint(-20, 20)
        height_variance = random.randint(-20, 20)
        width = base_width + width_variance
        height = base_height + height_variance
        
        # Create a very slight background color variation for each question
        bg_r = random.randint(250, 255)
        bg_g = random.randint(250, 255)
        bg_b = random.randint(250, 255)
        img = Image.new('RGB', (width, height), (bg_r, bg_g, bg_b))
        draw = ImageDraw.Draw(img)
        
        # Get fonts
        title_font, regular_font, math_font = get_fonts()
        
        # Add question number with a slightly randomized position
        x_pos = 30 + random.randint(-5, 5)
        y_pos = 30 + random.randint(-5, 5)
        draw.text((x_pos, y_pos), f"Question {question_number}", fill=(0, 0, 0), font=title_font)
        
        # Expanded math topics and questions for more variety
        math_topics = {
            "Algebra": [
                "Solve the equation: {}x² + {}x + {} = 0",
                "Simplify the expression: {}x² + {}x + {} - {}x - {}",
                "Factor the expression: {}x² - {}",
                "Find the value of x that satisfies: {}x + {} = {}x - {}",
                "Solve the inequality: {}x² - {}x + {} > 0",
                "Find all values of k for which the equation {}x² + kx + {} = 0 has exactly one solution",
                "If f(x) = {}x² + {}x and f({}) = {}, find the value of the constant term"
            ],
            "Calculus": [
                "Find the derivative of f(x) = {}x³ + {}x² + {}x + {}",
                "Calculate the integral of f(x) = {}x² + {}x + {} with respect to x",
                "Find the stationary points of f(x) = {}x² - {}x + {}",
                "Determine the nature of the stationary point at x = {} for f(x) = {}x² + {}x + {}",
                "Find the area enclosed between the curve y = {}x² - {} and the x-axis",
                "Calculate the volume generated when the area under y = {}√x between x = {} and x = {} is rotated about the x-axis",
                "For the function f(x) = {}e^({}x) + {}x, find f'({})"
            ],
            "Trigonometry": [
                "Solve the equation: sin(x) = {} for 0 ≤ x < 2π",
                "Prove the identity: sin²(x) + cos²(x) = 1 using the value x = {}π/{}",
                "Find the value of tan({}) in terms of sin and cos",
                "Calculate the exact value of sin({}π/{})",
                "Find all solutions to the equation: {}sin(x) + {}cos(x) = {} in the interval [0, 2π]",
                "Prove that tan(x+y) = (tan(x) + tan(y))/(1 - tan(x)tan(y)) for the case where x = {}π/{} and y = {}π/{}",
                "Find the area of the triangle with sides a = {}, b = {} and included angle C = {}°"
            ],
            "Vectors": [
                "Given vectors a = ({}, {}, {}) and b = ({}, {}, {}), find a + b",
                "Calculate the dot product of a = ({}, {}) and b = ({}, {})",
                "Find the magnitude of the vector ({}, {}, {})",
                "Determine if the vectors ({}, {}) and ({}, {}) are parallel",
                "Find the angle between vectors a = ({}, {}, {}) and b = ({}, {}, {})",
                "Find a unit vector perpendicular to both a = ({}, {}, {}) and b = ({}, {}, {})",
                "Find the equation of the plane passing through the points ({}, {}, {}), ({}, {}, {}), and ({}, {}, {})"
            ],
            "Functions": [
                "Find the domain of the function f(x) = √({}x - {})",
                "Find the range of the function f(x) = {}x² + {}",
                "Find the inverse of the function f(x) = {}x + {}",
                "For functions f(x) = {}x² - {} and g(x) = {}x + {}, find (f∘g)({})",
                "Find all values of x for which f(x) = 1/({} - {}x) is undefined",
                "Sketch the graph of the function f(x) = {}|x - {}| + {}",
                "For the function f(x) = {}x³ - {}x² + {}x - {}, find f({}) and f'({})"
            ],
            "Probability": [
                "The probability of event A is {}/{}. The probability of event B is {}/{}. If A and B are independent, find P(A ∩ B)",
                "A bag contains {} red balls and {} blue balls. If {} balls are drawn without replacement, find the probability that they are all the same color",
                "In a normal distribution with mean {} and standard deviation {}, find the probability that a randomly selected value is less than {}",
                "A biased coin has a probability of {} of landing heads. If the coin is tossed {} times, find the probability of getting exactly {} heads",
                "The random variable X follows a binomial distribution B({}, {}). Find P(X = {})",
                "A discrete random variable X has the following probability distribution: P(X=1)={}, P(X=2)={}, P(X=3)={}. Find E(X) and Var(X)"
            ]
        }
        
        # Ensure we have the target topic or pick a random one
        if topic not in math_topics:
            topic = random.choice(list(math_topics.keys()))
        
        # Select a question template - ensure different questions for adjacent numbers
        questions = math_topics[topic]
        question_index = (question_number + hash(topic)) % len(questions)
        question_template = questions[question_index]
        
        # Generate random values based on transform level and question number
        values = []
        num_placeholders = question_template.count("{}")
        
        # Use a combination of factors to ensure unique seeds for each question
        # Include question_number, output_path hash, and current timestamp to ensure uniqueness
        seed_value = question_number * 31 + hash(output_path) % 997 + int(datetime.now().timestamp()) % 10000
        random.seed(seed_value)
        
        for i in range(num_placeholders):
            # Use both i and question number in the value generation to create more unique patterns
            # Each placeholder gets a different range of values
            multiplier = (i + 1) * (question_number % 3 + 1)
            
            if transform_level <= 2:
                # Simple numbers for lower transform levels, but with more variety
                if i % 3 == 0:  # First value in each triplet
                    values.append(random.randint(1, 10 * multiplier))
                elif i % 3 == 1:  # Second value
                    values.append(random.randint(-5 * multiplier, 5 * multiplier))
                else:  # Third value
                    values.append(random.choice([2, 3, 5, 7, 11, 13]) * multiplier)
            elif transform_level <= 4:
                # More complex numbers for higher transform levels
                if i % 3 == 0:
                    values.append(random.randint(-20 * multiplier, 20 * multiplier))
                elif i % 3 == 1:
                    values.append(round(random.uniform(-10, 10) * multiplier, 1))
                else:
                    values.append(random.choice([-7, -5, -3, -2, -1, 1, 2, 3, 5, 7]) * multiplier)
            else:
                # Most complex numbers including varied decimals and fractions
                if i % 4 == 0:
                    values.append(round(random.uniform(-30, 30) * multiplier, 1))
                elif i % 4 == 1:
                    values.append(round(random.uniform(-15, 15) * multiplier, 2))
                elif i % 4 == 2 and random.random() < 0.4:  # 40% chance of fraction
                    values.append(f"{random.randint(1, 7)}/{random.randint(2, 9)}")
                else:
                    values.append(random.choice([-11, -9, -7, -5, -3, -1, 1, 3, 5, 7, 9, 11]) * multiplier)
        
        # Format the question with random values
        question_text = question_template.format(*values)
        
        # Draw the question text with a random slight color variation
        topic_color = (0, 0, random.randint(130, 170))
        draw.text((x_pos, y_pos + 50), f"Topic: {topic}", fill=topic_color, font=regular_font)
        
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
            
        # Draw each line of the question with slight position variations
        y_pos = 120 + random.randint(-10, 10)
        line_spacing = 30 + random.randint(-2, 2)
        
        for line in lines:
            x_offset = random.randint(-3, 3)
            draw.text((30 + x_offset, y_pos), line, fill=(0, 0, 0), font=math_font)
            y_pos += line_spacing
        
        # Add marks based on transform level
        marks = transform_level + 1
        draw.text((30, y_pos + 20), f"[{marks} marks]", fill=(0, 0, 0), font=regular_font)
        
        # Add a disclaimer with a random position at the bottom
        disclaimer_text = (
            "Note: This is an AI-generated mock question for educational purposes. "
            "It may contain errors and should be reviewed by a qualified teacher."
        )
        x_disclaimer = 30 + random.randint(-5, 5)
        y_disclaimer = height - 40 + random.randint(-5, 5)
        disclaimer_color = (random.randint(140, 160), random.randint(140, 160), random.randint(140, 160))
        draw.text((x_disclaimer, y_disclaimer), disclaimer_text, fill=disclaimer_color, font=regular_font)
        
        # Reset random seed after generating question
        random.seed()
        
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
        # Create a blank image with a slightly randomized size for visual diversity
        base_width, base_height = 800, 800
        width_variance = random.randint(-20, 20)
        height_variance = random.randint(-20, 20)
        width = base_width + width_variance
        height = base_height + height_variance
        
        # Create a very slight background color variation for each mark scheme
        bg_r = random.randint(250, 255)
        bg_g = random.randint(250, 255)
        bg_b = random.randint(250, 255)
        img = Image.new('RGB', (width, height), (bg_r, bg_g, bg_b))
        draw = ImageDraw.Draw(img)
        
        # Get fonts
        title_font, regular_font, math_font = get_fonts()
        
        # Add mark scheme title with a slightly randomized position
        x_pos = 30 + random.randint(-5, 5)
        y_pos = 30 + random.randint(-5, 5)
        draw.text((x_pos, y_pos), f"Mark Scheme for Question {question_number}", fill=(0, 0, 0), font=title_font)
        
        # Expanded math topics and mark schemes
        math_topics = {
            "Algebra": [
                ["M1: Correct application of quadratic formula", 
                 "A1: First correct solution x = {:.2f}", 
                 "A1: Second correct solution x = {:.2f}", 
                 "M1: Clear logical working shown"],
                
                ["M1: Method for solving quadratic equations", 
                 "A1: Factoring correctly as (x{:+.1f})(x{:+.1f})", 
                 "A1: Stating both zeros of the quadratic", 
                 "B1: Checking solutions in original equation"],
                
                ["M1: Setting up correct algebraic expression", 
                 "M1: Using appropriate identities", 
                 "A1: Simplifying to correct form", 
                 "A1: Final answer correctly stated as {:.2f}"]
            ],
            "Calculus": [
                ["M1: Correct use of differentiation rules", 
                 "A1: Correct derivative found", 
                 "M1: Setting derivative equal to zero", 
                 "A1: Correct stationary point(s) at x = {:.2f}"],
                
                ["M1: Using power rule correctly", 
                 "M1: Applying chain rule", 
                 "A1: Correct integration of terms", 
                 "A1: Correct constant of integration c = {:.2f}"],
                
                ["M1: Identifying critical points", 
                 "A1: Finding where f'(x) = 0", 
                 "M1: Second derivative test", 
                 "A1: Classifying critical point at x = {:.2f} as maximum/minimum"]
            ],
            "Trigonometry": [
                ["M1: Correct approach to solving trigonometric equation", 
                 "A1: First solution x = {:.2f}", 
                 "A1: Second solution x = {:.2f}", 
                 "B1: Correct domain consideration"],
                
                ["M1: Using correct trigonometric identity", 
                 "A1: Substituting values correctly", 
                 "M1: Algebraic manipulation", 
                 "A1: Final value sin({:.2f}) = {:.2f}"],
                
                ["B1: Recognition of angle in standard position", 
                 "M1: Using correct trigonometric ratios", 
                 "A1: Geometric interpretation", 
                 "A1: Final answer = {:.2f}π"]
            ],
            "Vectors": [
                ["M1: Correct method for vector calculation", 
                 "A1: Correct components found", 
                 "A1: Correct final answer", 
                 "C1: Clear presentation of working"],
                
                ["M1: Setting up vector equation", 
                 "M1: Finding direction vectors", 
                 "A1: Correct cross product calculation", 
                 "A1: Final answer r = ({:.1f}, {:.1f}, {:.1f}) + λ({:.1f}, {:.1f}, {:.1f})"],
                
                ["M1: Identifying vector properties", 
                 "A1: Computing magnitude |v| = {:.2f}", 
                 "M1: Finding unit vector", 
                 "A1: Final answer v̂ = ({:.2f}, {:.2f}, {:.2f})"]
            ],
            "Functions": [
                ["M1: Correct approach to finding domain", 
                 "M1: Finding critical values", 
                 "A1: Determining intervals", 
                 "A1: Domain = [{:.1f}, {:.1f}) ∪ ({:.1f}, ∞)"],
                
                ["M1: Analyzing function composition", 
                 "M1: Substituting g(x) into f(x)", 
                 "A1: Simplifying algebraic expression", 
                 "A1: Final answer (f∘g)(x) = {:.1f}x² + {:.1f}x + {:.1f}"],
                
                ["M1: Correct method for finding inverse", 
                 "M1: Swapping variables and solving for y", 
                 "A1: Rearranging to standard form", 
                 "A1: f⁻¹(x) = {:.2f}x + {:.2f}"]
            ],
            "Probability": [
                ["M1: Applying correct probability formula", 
                 "M1: Setting up appropriate model", 
                 "A1: Correct calculation P(A) = {:.3f}", 
                 "A1: Final answer P(A∪B) = {:.3f}"],
                
                ["B1: Recognizing binomial distribution", 
                 "M1: Using correct formula C(n,r)p^r(1-p)^(n-r)", 
                 "M1: Substituting values correctly", 
                 "A1: Final probability = {:.4f}"],
                
                ["M1: Finding mean μ = {:.2f}", 
                 "M1: Finding standard deviation σ = {:.2f}", 
                 "A1: Standardizing to z-value", 
                 "A1: Probability from z-table = {:.4f}"]
            ]
        }
        
        # Ensure we have the target topic or pick a random one
        if topic not in math_topics:
            topic = random.choice(list(math_topics.keys()))
        
        # Use question_number to seed the randomness for consistency with the question
        random.seed(question_number * 31 + hash(output_path) % 997)
        
        # Select a mark scheme template based on question number
        template_sets = math_topics[topic]
        template_index = (question_number + hash(topic)) % len(template_sets)
        mark_scheme_templates = template_sets[template_index]
        
        # Generate random values for the template
        x1 = random.uniform(-5, 5)
        x2 = random.uniform(-5, 5)
        x3 = random.uniform(0, 5) 
        x4 = random.uniform(-3, 3)
        x5 = random.uniform(1, 10)
        
        # Marks based on transform level
        marks = transform_level + 1
        
        # Draw the mark scheme content with a random slight color variation
        topic_color = (0, 0, random.randint(130, 170))
        draw.text((x_pos, y_pos + 50), f"Topic: {topic}", fill=topic_color, font=regular_font)
        
        # Calculate how many marking points to show based on marks
        points_to_show = min(marks, len(mark_scheme_templates))
        
        # Draw each line of the mark scheme with slight position variations
        y_pos = 120 + random.randint(-10, 10)
        line_spacing = 30 + random.randint(-2, 2)
        
        for i in range(points_to_show):
            template = mark_scheme_templates[i]
            x_offset = random.randint(-3, 3)
            
            # Format template with random values if needed
            if "{:.2f}" in template or "{:.1f}" in template or "{:.3f}" in template or "{:.4f}" in template:
                if i == 0:
                    line = template.format(x1)
                elif i == 1:
                    line = template.format(x2)
                elif i == 2:
                    line = template.format(x3)
                else:
                    # Handle multiple format placeholders
                    try:
                        placeholder_count = template.count("{")
                        if placeholder_count == 1:
                            line = template.format(x4)
                        elif placeholder_count == 2:
                            line = template.format(x1, x2)
                        elif placeholder_count == 3:
                            line = template.format(x1, x2, x3)
                        elif placeholder_count == 6:
                            line = template.format(x1, x2, x3, x4, x5, random.uniform(-1, 1))
                        else:
                            line = template.format(x1)
                    except Exception as format_error:
                        logger.warning(f"Format error with template {template}: {format_error}")
                        line = template.replace("{:.1f}", "?").replace("{:.2f}", "?").replace("{:.3f}", "?").replace("{:.4f}", "?")
            else:
                line = template
                
            draw.text((30 + x_offset, y_pos), line, fill=(0, 0, 0), font=regular_font)
            y_pos += line_spacing
        
        # Add the total marks line
        total_text = f"Total: {marks} marks"
        draw.text((30, y_pos + 20), total_text, fill=(0, 0, 0), font=title_font)
        
        # Add a disclaimer with a random position at the bottom
        disclaimer_text = (
            "Note: This is an AI-generated mock mark scheme for educational purposes. "
            "It may contain errors and should be reviewed by a qualified teacher."
        )
        x_disclaimer = 30 + random.randint(-5, 5)
        y_disclaimer = height - 40 + random.randint(-5, 5)
        disclaimer_color = (random.randint(140, 160), random.randint(140, 160), random.randint(140, 160))
        draw.text((x_disclaimer, y_disclaimer), disclaimer_text, fill=disclaimer_color, font=regular_font)
        
        # Reset random seed after generating mark scheme
        random.seed()
        
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
        # Convert parameters to appropriate types to avoid errors
        try:
            source_paper_id = int(source_paper_id)
            num_questions = int(num_questions) if isinstance(num_questions, str) else num_questions
            transform_level = int(transform_level) if isinstance(transform_level, str) else transform_level
            
            # Validate ranges
            num_questions = max(1, min(15, num_questions))  # Between 1 and 15
            transform_level = max(1, min(5, transform_level))  # Between 1 and 5
            
            logger.info(f"Starting simple mock generation with paper_id={source_paper_id}, questions={num_questions}, transform_level={transform_level}")
        except ValueError as e:
            logger.error(f"Parameter conversion error: {str(e)}")
            return {"success": False, "error": f"Invalid parameters: {str(e)}"}
            
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
            # Get available topics from math_topics defined in the create_simple_question function
            # We'll just use the default set to distribute topic areas across questions
            available_topics = ["Algebra", "Calculus", "Trigonometry", "Vectors", "Functions", "Probability"]
            topic_index = (question_number + hash(str(mock_paper.id))) % len(available_topics)
            topic = available_topics[topic_index]
            
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