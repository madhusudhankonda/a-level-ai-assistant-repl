import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2

def create_sample_question_paper():
    """Create a sample question paper with mathematical equations for testing"""
    # Create a folder for sample data
    os.makedirs('data/papers', exist_ok=True)
    
    # Create a white image
    width, height = 800, 1200
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Try to load a font
    try:
        font = ImageFont.truetype("Arial", 24)
    except IOError:
        # Use default font if Arial is not available
        font = ImageFont.load_default()
    
    # Add title
    draw.text((50, 30), "Sample A-Level Mathematics Paper", fill='black', font=font)
    draw.text((50, 70), "Pure Mathematics", fill='black', font=font)
    
    # Add horizontal line
    draw.line((50, 100, 750, 100), fill='black', width=2)
    
    # Question 1
    draw.text((50, 120), "Question 1", fill='black', font=font)
    draw.text((50, 160), "Solve the quadratic equation: x² - 5x + 6 = 0", fill='black', font=font)
    
    # Horizontal line separator
    draw.line((50, 220, 750, 220), fill='black', width=2)
    
    # Question 2
    draw.text((50, 240), "Question 2", fill='black', font=font)
    draw.text((50, 280), "Differentiate f(x) = 3x² + 2x - 5 with respect to x.", fill='black', font=font)
    
    # Horizontal line separator
    draw.line((50, 340, 750, 340), fill='black', width=2)
    
    # Question 3
    draw.text((50, 360), "Question 3", fill='black', font=font)
    draw.text((50, 400), "Find the integral of g(x) = 2x + cos(x) with respect to x.", fill='black', font=font)
    
    # Horizontal line separator
    draw.line((50, 460, 750, 460), fill='black', width=2)
    
    # Question 4
    draw.text((50, 480), "Question 4", fill='black', font=font)
    draw.text((50, 520), "Solve the simultaneous equations:", fill='black', font=font)
    draw.text((50, 560), "2x + y = 7", fill='black', font=font)
    draw.text((50, 600), "x - y = 1", fill='black', font=font)
    
    # Horizontal line separator
    draw.line((50, 660, 750, 660), fill='black', width=2)
    
    # Question 5
    draw.text((50, 680), "Question 5", fill='black', font=font)
    draw.text((50, 720), "Find the derivative of h(x) = e^x * ln(x)", fill='black', font=font)
    
    # Save the image
    image_path = os.path.join('data/papers', 'sample_math_paper.png')
    image.save(image_path)
    
    return image_path

if __name__ == "__main__":
    paper_path = create_sample_question_paper()
    print(f"Sample question paper created at: {paper_path}")