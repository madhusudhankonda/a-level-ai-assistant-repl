from app import app, db
from models import Question
import os
import uuid
from PIL import Image, ImageDraw, ImageFont
import io

def get_data_folder():
    """Get the data folder for storing papers and questions"""
    data_folder = os.path.join(os.getcwd(), 'data')
    os.makedirs(data_folder, exist_ok=True)
    return data_folder

def create_question_image(question_number, path):
    """Create a unique question image with the question number visible"""
    # Create a blank image with white background
    width, height = 800, 600
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Try to use a font, fall back to default if not available
    try:
        # Try to load a font
        font_size = 72
        font = ImageFont.truetype("Arial", font_size)
    except IOError:
        # If font not available, use default
        font = None
    
    # Draw title at the top
    title = "Sample A-Level Mathematics Paper"
    draw.text((width//2 - 200, 50), title, fill='black', font=None)
    
    # Draw a line under the title
    draw.line([(50, 100), (width-50, 100)], fill='black', width=2)
    
    # Draw large question number in the center
    question_text = f"Question {question_number}"
    
    # Calculate text size and position (approximate)
    text_x = width // 2 - len(question_text) * 15
    text_y = height // 2 - 50
    
    # Draw with large size
    draw.text((text_x, text_y), question_text, fill='black', font=None)
    
    # Add some mathematical content appropriate for question number
    math_content = ""
    if question_number == "1":
        math_content = "Solve the quadratic equation: x² + 5x + 6 = 0"
    elif question_number == "2":
        math_content = "Differentiate f(x) = 3x² + 2x - 5 with respect to x"
    elif question_number == "3":
        math_content = "Find the integral of g(x) = 2x + cos(x) with respect to x"
    elif question_number == "4":
        math_content = "Solve the system of equations: 2x + y = 7, x - y = 1"
    elif question_number == "5":
        math_content = "If f(x) = x³ - 3x + 2, find f'(2)"
    elif question_number == "6":
        math_content = "Find the equation of the tangent to y = x² at x = 3"
    elif question_number == "7":
        math_content = "Calculate the area under the curve y = x² between x = 0 and x = 4"
    elif question_number == "8":
        math_content = "Find the maximum value of f(x) = -x² + 8x - 12"
    elif question_number == "9":
        math_content = "Solve the inequality: 2x - 3 > 5x + 2"
    elif question_number == "10":
        math_content = "The gradient of a curve at point (2, 3) is 4. Find its equation."
    elif question_number == "11":
        math_content = "If f(x) = 2ˣ and g(x) = x + 3, find (f∘g)(2)"
    elif question_number == "12":
        math_content = "Simplify the expression: log₃(27) - log₃(9) + log₃(3)"
    elif question_number == "13":
        math_content = "Find all values of x such that sin(x) = 0.5, where 0 ≤ x ≤ 2π"
    else:
        math_content = "Solve for x in the given equation"
    
    # Draw the math content below the question number
    draw.text((width//2 - 250, height//2 + 50), math_content, fill='black', font=None)
    
    # Draw a line at the bottom
    draw.line([(50, height-100), (width-50, height-100)], fill='black', width=2)
    
    # Add a note at the bottom
    draw.text((width//2 - 150, height-80), f"Pure Mathematics (Question {question_number})", fill='black', font=None)
    
    # Save the image
    image.save(path)
    return True

with app.app_context():
    # Get all questions for paper_id=55
    questions = Question.query.filter_by(paper_id=55).all()
    print(f"Found {len(questions)} questions for paper_id=55")
    
    # Create the paper_55 directory if it doesn't exist
    paper_dir = os.path.join(get_data_folder(), "paper_55")
    os.makedirs(paper_dir, exist_ok=True)
    print(f"Ensured directory exists: {paper_dir}")
    
    # For each question, create a unique image file in the correct location
    for question in questions:
        print(f"Processing question {question.id}: {question.question_number}")
        
        # Get the expected filename from the path
        filename = os.path.basename(question.image_path)
        
        # Create the new file path
        image_path = os.path.join(paper_dir, filename)
        
        # Create a custom image for this question
        try:
            result = create_question_image(question.question_number, image_path)
            if result:
                print(f"  ✓ Created unique image for Question {question.question_number} at: {image_path}")
            else:
                print(f"  ✗ Failed to create unique image for Question {question.question_number}")
                
            # Verify the file exists
            if os.path.exists(image_path):
                print(f"  ✓ Verified file exists")
            else:
                print(f"  ✗ File not created successfully")
                
        except Exception as e:
            print(f"  ✗ Error creating image: {str(e)}")
    
    print("\nDone! All question images should now be unique.")
