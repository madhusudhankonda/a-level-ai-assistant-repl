from app import app, db
from models import Question
import os
import uuid
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime

def get_data_folder():
    """Get the data folder for storing papers and questions"""
    data_folder = os.path.join(os.getcwd(), 'data')
    os.makedirs(data_folder, exist_ok=True)
    return data_folder

def create_question_image(question_number, path, force_mechanics=False):
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
        
    # Add a timestamp to make each image unique
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # Check if this paper is for Mechanics content (paper_id 55)
    paper_id = os.path.basename(os.path.dirname(path)).replace("paper_", "")
    is_mechanics_paper = (paper_id == "55" or force_mechanics)
    
    # Draw title at the top with timestamp to make each image uniquely identifiable
    if is_mechanics_paper:
        title = f"A-Level Mathematics & Mechanics ({timestamp})"
    else:
        title = f"A-Level Pure Mathematics ({timestamp})"
    draw.text((width//2 - 250, 50), title, fill='black', font=None)
    
    # Draw a line under the title
    draw.line([(50, 100), (width-50, 100)], fill='black', width=2)
    
    # Draw large question number in the center
    question_text = f"Question {question_number}"
    
    # Calculate text size and position (approximate)
    text_x = width // 2 - len(question_text) * 15
    text_y = height // 2 - 50
    
    # Draw with large size
    draw.text((text_x, text_y), question_text, fill='black', font=None)
    
    # Add some mathematical content appropriate for question number and paper type
    math_content = ""
    
    if is_mechanics_paper:
        # Mechanics questions
        if question_number == "1":
            math_content = "A particle P moves with constant acceleration (3i − 2j) m s⁻². At time t = 4 seconds, P has velocity 6i m s⁻¹. Determine the speed of P at time t = 0 seconds."
        elif question_number == "2":
            math_content = "A car of mass 1200 kg accelerates from rest at a constant rate of 2.5 m s⁻² for 8 seconds. Calculate the work done by the engine during this time."
        elif question_number == "3":
            math_content = "A ball is thrown vertically upward with an initial velocity of 25 m s⁻¹. Find the maximum height reached by the ball. Take g = 9.8 m s⁻²."
        elif question_number == "4":
            math_content = "A force F = (4i + 5j) N acts on a particle that moves from position (1, 2) m to (3, 7) m. Calculate the work done by the force."
        elif question_number == "5":
            math_content = "A block of mass 5 kg is pushed up a rough inclined plane by a horizontal force of 60 N. If the coefficient of friction is 0.3 and the plane is inclined at 30° to the horizontal, find the acceleration of the block."
        elif question_number == "6":
            math_content = "Two particles connected by a light inextensible string pass over a smooth pulley. If one has mass 3 kg and the other 5 kg, find the acceleration of the system."
        elif question_number == "7":
            math_content = "A projectile is fired with an initial velocity of 80 m s⁻¹ at an angle of 30° to the horizontal. Find the range and the maximum height reached. Take g = 9.8 m s⁻²."
        elif question_number == "8":
            math_content = "A particle P moves with constant acceleration (3i − 2j) m s⁻². At time t = 4 seconds, P has velocity 6i m s⁻¹. Determine the speed of P at time t = 0 seconds."
        elif question_number == "9":
            math_content = "A car of mass 1500 kg is traveling at 20 m s⁻¹ when the brakes are applied, causing a constant deceleration of 4 m s⁻². Calculate the stopping distance and the work done by the brakes."
        elif question_number == "10":
            math_content = "A body of mass 2 kg is suspended from a spring with stiffness 50 N m⁻¹. If the body is pulled down 0.2 m from its equilibrium position and released, find the subsequent motion."
        elif question_number == "11":
            math_content = "A pendulum consists of a bob of mass 0.5 kg attached to a string of length 1 m. If it is released from rest at an angle of 10° to the vertical, find the tension in the string at the lowest point."
        else:
            math_content = "A particle moves along a straight line such that its displacement s metres from a fixed point O at time t seconds is given by s = t³ - 6t² + 9t. Find the values of t when the particle is momentarily at rest."
    else:
        # Pure Mathematics questions (original content)
        if question_number == "1":
            math_content = "Solve for x in the given equation: x² + 5x + 6 = 0"
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
    
    # Add a note at the bottom with correct paper type
    if is_mechanics_paper:
        draw.text((width//2 - 150, height-80), f"Mathematics and Mechanics (Question {question_number})", fill='black', font=None)
    else:
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
        
        # Create a custom image for this question - force mechanics content for paper 55
        try:
            result = create_question_image(question.question_number, image_path, force_mechanics=True)
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
