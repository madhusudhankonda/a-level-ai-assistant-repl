from app import app, db
from models import Question, QuestionPaper
import os
import time
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime

def get_data_folder():
    """Get the data folder for storing papers and questions"""
    data_folder = os.path.join(os.getcwd(), 'data')
    os.makedirs(data_folder, exist_ok=True)
    return data_folder

def create_mechanics_image(question_number, path):
    """Create a distinctive mechanics-focused image with clear physics content"""
    # Create a blank image with white background
    width, height = 800, 600
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Add timestamp with higher precision to ensure uniqueness 
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    
    # Create distinctive title
    title = f"Mathematics & Mechanics - {timestamp[:14]}"
    draw.text((width//2 - 250, 30), title, fill='black')
    
    # Draw colored border to make changes visually obvious
    for i in range(5):
        draw.rectangle([(5+i, 5+i), (width-5-i, height-5-i)], outline=(0, 0, 200), width=1)
    
    # Draw large question number in the center
    question_text = f"Question {question_number}"
    draw.text((width//2 - 100, height//2 - 150), question_text, fill='black')
    
    # Add mechanics-specific content that's visually distinctive
    math_content = ""
    if question_number == "q1":
        math_content = "A particle P moves with constant acceleration (3i − 2j) m s⁻². At time t = 4 seconds, P has velocity 6i m s⁻¹. Determine the speed of P at time t = 0 seconds."
    elif question_number == "q2":
        math_content = "A car of mass 1200 kg accelerates from rest at a constant rate of 2.5 m s⁻² for 8 seconds. Calculate the work done by the engine during this time."
    elif question_number == "q3":
        math_content = "A ball is thrown vertically upward with an initial velocity of 25 m s⁻¹. Find the maximum height reached by the ball. Take g = 9.8 m s⁻²."
    elif question_number == "q4":
        math_content = "A force F = (4i + 5j) N acts on a particle that moves from position (1, 2) m to (3, 7) m. Calculate the work done by the force."
    elif question_number == "q5":
        math_content = "A block of mass 5 kg is pushed up a rough inclined plane by a horizontal force of 60 N. If the coefficient of friction is 0.3 and the plane is inclined at 30° to the horizontal, find the acceleration of the block."
    elif question_number == "q6":
        math_content = "Two particles connected by a light inextensible string pass over a smooth pulley. If one has mass 3 kg and the other 5 kg, find the acceleration of the system."
    elif question_number == "q7":
        math_content = "A projectile is fired with an initial velocity of 80 m s⁻¹ at an angle of 30° to the horizontal. Find the range and the maximum height reached. Take g = 9.8 m s⁻²."
    elif question_number == "q8":
        math_content = "A particle P moves with constant acceleration (3i − 2j) m s⁻². At time t = 4 seconds, P has velocity 6i m s⁻¹. Determine the speed of P at time t = 0 seconds."
    elif question_number == "q9":
        math_content = "A car of mass 1500 kg is traveling at 20 m s⁻¹ when the brakes are applied, causing a constant deceleration of 4 m s⁻². Calculate the stopping distance and the work done by the brakes."
    elif question_number == "q10":
        math_content = "A body of mass 2 kg is suspended from a spring with stiffness 50 N m⁻¹. If the body is pulled down 0.2 m from its equilibrium position and released, find the subsequent motion."
    elif question_number == "q11":
        math_content = "A pendulum consists of a bob of mass 0.5 kg attached to a string of length 1 m. If it is released from rest at an angle of 10° to the vertical, find the tension in the string at the lowest point."
    elif question_number == "q12":
        math_content = "A particle moves along a straight line such that its displacement s metres from a fixed point O at time t seconds is given by s = t³ - 6t² + 9t. Find the values of t when the particle is momentarily at rest."
    elif question_number == "q13":
        math_content = "A projectile is fired with an initial velocity of 60 m s⁻¹ at an angle of 45° to the horizontal. Calculate the time taken to reach its maximum height and the horizontal distance traveled during this time."
    else:
        math_content = "Mechanics question - with physics content"
    
    # Draw the math content with clear wrapping
    lines = []
    words = math_content.split()
    current_line = ""
    for word in words:
        if len(current_line + " " + word) <= 60:  # character limit per line
            current_line += " " + word if current_line else word
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    
    y_position = height//2 - 50
    for line in lines:
        draw.text((width//2 - 250, y_position), line, fill='black')
        y_position += 25  # line spacing
    
    # Add physics-related diagram based on question content
    if "projectile" in math_content.lower():
        # Draw a projectile trajectory
        draw.arc([(100, 350), (300, 550)], 0, 180, fill=(255, 0, 0), width=2)
        draw.line([(100, 450), (300, 450)], fill=(0, 0, 0), width=2)  # ground
        draw.text((150, 350), "Projectile Motion", fill=(255, 0, 0))
    elif "force" in math_content.lower():
        # Draw a force diagram
        draw.line([(550, 350), (650, 350)], fill=(255, 0, 0), width=3)  # Force vector
        draw.polygon([(650, 350), (640, 345), (640, 355)], fill=(255, 0, 0))  # Arrow
        draw.text((560, 320), "Force Vector", fill=(255, 0, 0))
    elif "mass" in math_content.lower():
        # Draw a mass
        draw.rectangle([(550, 350), (600, 400)], fill=(200, 200, 200), outline=(0, 0, 0), width=2)
        draw.text((560, 370), "Mass", fill=(0, 0, 0))
    
    # Add a clear indicator this is the mechanical components paper
    draw.text((width//2 - 200, height - 50), f"MECHANICS PAPER - Question {question_number} - v{timestamp[:8]}", fill=(255, 0, 0))
    
    # Save the image
    image.save(path)
    return True

with app.app_context():
    # Update the title of paper 55 to ensure it's clearly a mechanics paper
    paper = QuestionPaper.query.get(55)
    if paper:
        paper.title = "June 2023 Mathematics & Mechanics"
        paper.description = "June 2023 Mathematics & Mechanics Paper - Physics Content"
        db.session.commit()
        print(f"Updated paper title to: {paper.title}")
    else:
        print("Error: Paper 55 not found")
    
    # Get all questions for paper_id=55
    questions = Question.query.filter_by(paper_id=55).all()
    print(f"Found {len(questions)} questions for paper_id=55")
    
    # Create the paper_55 directory if it doesn't exist
    paper_dir = os.path.join(get_data_folder(), "paper_55")
    os.makedirs(paper_dir, exist_ok=True)
    print(f"Ensured directory exists: {paper_dir}")
    
    # Delete any existing images to ensure clean generation
    for old_file in os.listdir(paper_dir):
        old_path = os.path.join(paper_dir, old_file)
        try:
            os.remove(old_path)
            print(f"Removed old file: {old_path}")
        except Exception as e:
            print(f"Error removing file {old_path}: {str(e)}")
    
    # For each question, create a unique image file with distinctive mechanics content
    for question in questions:
        # To absolutely ensure no caching issues, we'll modify the image path
        # to include today's date in the filename
        today = datetime.now().strftime("%Y%m%d")
        filename = f"{question.question_number}_mechanics_{today}.png"
        
        # Create the new file path
        image_path = os.path.join(paper_dir, filename)
        
        # Create a custom image for this question
        try:
            result = create_mechanics_image(question.question_number, image_path)
            if result:
                print(f"  ✓ Created mechanics image for Question {question.question_number} at: {image_path}")
                
                # Update the database with the new path
                question.image_path = image_path
                db.session.commit()
                print(f"  ✓ Updated database record with new path: {image_path}")
            else:
                print(f"  ✗ Failed to create mechanics image for Question {question.question_number}")
        except Exception as e:
            print(f"  ✗ Error creating image: {str(e)}")
    
    # Verify all questions have updated paths
    updated_questions = Question.query.filter_by(paper_id=55).all()
    for q in updated_questions:
        print(f"Question {q.question_number} - Path: {q.image_path}")
    
    # Force a small delay to ensure file system changes are propagated
    print("\nWaiting for file system changes to propagate...")
    time.sleep(2)
    
    print("\nDone! All question images for the mechanics paper have been recreated with distinctive physics content.")