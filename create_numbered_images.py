"""
Script to create uniquely identifiable sample images for each question number.
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont
import shutil

def create_numbered_image(question_number, output_path):
    """
    Create a unique image for a specific question number with the number
    clearly displayed on the image
    """
    # Create a blank image with a dark background
    width, height = 800, 600
    image = Image.new('RGB', (width, height), color=(40, 44, 52))
    draw = ImageDraw.Draw(image)
    
    try:
        # Try to load a font, or use default if not found
        try:
            font_large = ImageFont.truetype("Arial", 60)
            font_small = ImageFont.truetype("Arial", 24)
        except IOError:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Draw a border
        draw.rectangle([(20, 20), (width-20, height-20)], outline=(100, 100, 100), width=2)
        
        # Draw question number large in the center
        title = f"Question {question_number}"
        draw.text((width//2, height//3), title, fill=(255, 255, 255), font=font_large, anchor="mm")
        
        # Draw A-Level Math text at top
        draw.text((width//2, 50), "A-Level Mathematics", fill=(200, 200, 200), font=font_small, anchor="mm")
        
        # Draw different question text based on question number
        question_texts = {
            "1": "Solve the quadratic equation: x² - 5x + 6 = 0",
            "2": "Differentiate f(x) = 3x³ + 2x - 5 with respect to x.",
            "3": "Find the integral of g(x) = 2x + cos(x) with respect to x.",
            "4": "Solve the simultaneous equations: 2x + y = 7, x - y = 1",
            "5": "Find the equation of the line through points (2,3) and (4,7).",
            "6": "Calculate the area under the curve y = x² between x = 1 and x = 3.",
            "7": "Solve the inequality: 2x - 1 > 3x + 2",
            "8": "Find the value of sin²(θ) + cos²(θ) for any angle θ.",
            "9": "Calculate the derivative of h(x) = e^(2x) * ln(x).",
            "10": "Find the coordinates of the stationary points of f(x) = x³ - 6x² + 9x + 2.",
            "11": "Solve the equation: ln(x) = 2",
            "12": "Calculate the binomial expansion of (1 + x)^5 up to x³."
        }
        
        # Get the appropriate question text or use default
        question_text = question_texts.get(str(question_number), "Sample mathematical question")
        
        # Draw the question text
        draw.text((width//2, height//2 + 50), question_text, fill=(180, 180, 255), font=font_small, anchor="mm")
        
        # Add a footer
        draw.text((width//2, height - 50), "Pure Mathematics Paper", fill=(150, 150, 150), font=font_small, anchor="mm")
        
    except Exception as e:
        # If there's an error, draw error text
        print(f"Error creating image: {str(e)}", file=sys.stderr)
        draw.text((width//2, height//2), f"Question {question_number}", fill=(255, 255, 255), anchor="mm")
    
    # Save the image
    try:
        image.save(output_path)
        print(f"Created image for question {question_number} at {output_path}")
        return True
    except Exception as save_error:
        print(f"Error saving image: {str(save_error)}", file=sys.stderr)
        return False

def ensure_unique_question_images():
    """Ensure that each question has a unique and identifiable sample image"""
    questions_dir = "./data/questions/paper_1"
    
    # Make sure the directory exists
    if not os.path.exists(questions_dir):
        os.makedirs(questions_dir, exist_ok=True)
        print(f"Created directory: {questions_dir}")
    
    # Create a unique image for each question number
    success = True
    for q_num in range(1, 13):
        image_path = os.path.join(questions_dir, f"question_q{q_num}_703866-q{q_num}.png")
        if not create_numbered_image(q_num, image_path):
            success = False
    
    print("All sample question images created successfully" if success else 
          "Some images could not be created properly")
    return success

if __name__ == "__main__":
    ensure_unique_question_images()