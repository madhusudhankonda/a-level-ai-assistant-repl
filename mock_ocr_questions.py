"""
Script to generate mock OCR Pure Mathematics questions
"""

import os
import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from io import BytesIO

def get_fonts():
    """Get appropriate fonts for drawing mathematical text"""
    try:
        # Try to load Arial or other common fonts
        title_font = ImageFont.truetype("Arial.ttf", 32)
        question_font = ImageFont.truetype("Arial.ttf", 24)
        math_font = ImageFont.truetype("Arial.ttf", 22)
    except IOError:
        # Fall back to default font if needed
        title_font = ImageFont.load_default()
        question_font = ImageFont.load_default()
        math_font = ImageFont.load_default()
    
    return title_font, question_font, math_font

def create_triangle_question():
    """
    Create a question about triangle properties similar to question 1 in the OCR paper 
    but with different values and approach
    """
    # Create a blank white image
    width, height = 800, 600
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Get fonts
    title_font, question_font, math_font = get_fonts()
    
    # Draw the question title
    draw.text((20, 20), "Question 1", font=title_font, fill='black')
    
    # Define triangle vertices for visualization
    a, b, c = 8, 12, 10  # Side lengths
    angle_A = math.acos((b**2 + c**2 - a**2) / (2 * b * c))
    
    # Define triangle coordinates
    x_C, y_C = 400, 500
    x_A, y_A = x_C, y_C - c
    x_B, y_B = x_C + b * math.sin(angle_A), y_C - b * math.cos(angle_A)
    
    # Draw the triangle
    draw.line([(x_A, y_A), (x_B, y_B), (x_C, y_C), (x_A, y_A)], fill='black', width=2)
    
    # Label the vertices
    draw.text((x_A-15, y_A-20), "A", font=question_font, fill='black')
    draw.text((x_B+10, y_B-10), "B", font=question_font, fill='black')
    draw.text((x_C-15, y_C+10), "C", font=question_font, fill='black')
    
    # Label the sides
    draw.text((x_A+b/2-20, y_A+20), f"{a} cm", font=math_font, fill='black')
    draw.text((x_B-40, y_B+c/2), f"{b} cm", font=math_font, fill='black')
    draw.text((x_C-40, y_C-c/2), f"{c} cm", font=math_font, fill='black')
    
    # Draw the angle
    angle_radius = 40
    draw.arc([(x_A-angle_radius, y_A-angle_radius), 
              (x_A+angle_radius, y_A+angle_radius)], 
             180-math.degrees(angle_A), 180, fill='black', width=2)
    
    draw.text((x_A-60, y_A), f"37°", font=math_font, fill='black')
    
    # Add point D description
    draw.text((20, 100), "In the triangle ABC, the length AB = 8 cm, the length BC = 12 cm and the angle BAC = 37°.", 
              font=question_font, fill='black')
    
    # Part (a)
    draw.text((20, 150), "(a) Calculate the length AC.", font=question_font, fill='black')
    draw.text((40, 180), "[2]", font=question_font, fill='black')
    
    # Part (b)
    draw.text((20, 220), "D is the point on BC such that the length AD = 7 cm.", font=question_font, fill='black')
    draw.text((20, 250), "(b) Calculate the possible values of the angle ADB.", font=question_font, fill='black')
    draw.text((40, 280), "[3]", font=question_font, fill='black')
    
    # Add AI disclaimer
    draw.text((20, 550), "Disclaimer: AI-generated questions may contain errors. Verify before use.", 
              font=ImageFont.truetype("Arial.ttf", 10) if 'Arial.ttf' in ImageFont.truetype.__code__.co_names else ImageFont.load_default(), 
              fill='red')
    
    return image

def create_algebraic_fractions_question():
    """
    Create a question about algebraic fractions similar to question 2 in the OCR paper
    but with different algebraic expressions
    """
    width, height = 800, 450
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Get fonts
    title_font, question_font, math_font = get_fonts()
    
    # Draw the question title
    draw.text((20, 20), "Question 2", font=title_font, fill='black')
    
    # Part (a)
    draw.text((20, 80), "(a) (i) Show that", font=question_font, fill='black')
    draw.text((150, 80), "1/(4+3x) + 1/(4-3x)", font=math_font, fill='black')
    draw.text((150, 120), "can be written in the form a/(b-cx²), where a, b and c are", font=question_font, fill='black')
    draw.text((150, 150), "constants to be determined.", font=question_font, fill='black')
    draw.text((700, 150), "[2]", font=question_font, fill='black')
    
    # Part (a)(ii)
    draw.text((120, 190), "(ii) Hence solve the equation", font=question_font, fill='black')
    draw.text((350, 190), "1/(4+3x) + 1/(4-3x) = 3", font=math_font, fill='black')
    draw.text((700, 190), "[2]", font=question_font, fill='black')
    
    # Part (b)
    draw.text((20, 240), "(b) In this question you must show detailed reasoning.", font=question_font, fill='black')
    draw.text((40, 280), "Solve the equation 3^(3y-5) × 3^(y-6) = 9", font=math_font, fill='black')
    draw.text((700, 280), "[4]", font=question_font, fill='black')
    
    # Add AI disclaimer
    draw.text((20, 400), "Disclaimer: AI-generated questions may contain errors. Verify before use.", 
              font=ImageFont.truetype("Arial.ttf", 10) if 'Arial.ttf' in ImageFont.truetype.__code__.co_names else ImageFont.load_default(), 
              fill='red')
    
    return image

def create_differentiation_question():
    """
    Create a question about differentiation similar to question 3 in the OCR paper
    but with a different function
    """
    width, height = 800, 450
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Get fonts
    title_font, question_font, math_font = get_fonts()
    
    # Draw the question title
    draw.text((20, 20), "Question 3", font=title_font, fill='black')
    
    # Part (a)
    draw.text((20, 80), "(a) Given that f(x) = x³ - 3x², use differentiation from first principles to show", font=question_font, fill='black')
    draw.text((20, 110), "     that f'(x) = 3x² - 6x.", font=question_font, fill='black')
    draw.text((700, 110), "[4]", font=question_font, fill='black')
    
    # Part (b)
    draw.text((20, 170), "(b) The gradient of a curve is given by dy/dx = 3x² - 6x and the curve passes", font=question_font, fill='black')
    draw.text((20, 200), "     through the point (2, -5).", font=question_font, fill='black')
    draw.text((20, 240), "     Find the equation of the curve.", font=question_font, fill='black')
    draw.text((700, 240), "[3]", font=question_font, fill='black')
    
    # Add AI disclaimer
    draw.text((20, 400), "Disclaimer: AI-generated questions may contain errors. Verify before use.", 
              font=ImageFont.truetype("Arial.ttf", 10) if 'Arial.ttf' in ImageFont.truetype.__code__.co_names else ImageFont.load_default(), 
              fill='red')
    
    return image

def create_vectors_question():
    """
    Create a question about vectors similar to question 4 in the OCR paper
    but with different positions and approach
    """
    width, height = 800, 550
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Get fonts
    title_font, question_font, math_font = get_fonts()
    
    # Draw the question title
    draw.text((20, 20), "Question 4", font=title_font, fill='black')
    
    # Main question text
    draw.text((20, 80), "It is given that PQRS is a quadrilateral. The position vector of P is 2i + j, and the position", font=question_font, fill='black')
    draw.text((20, 110), "vector of Q is 5i + 4j.", font=question_font, fill='black')
    
    # Part (a)
    draw.text((20, 170), "(a) Find the length PQ.", font=question_font, fill='black')
    draw.text((700, 170), "[1]", font=question_font, fill='black')
    
    # Part (b)
    draw.text((20, 220), "(b) The position vector of R is qi + 7j where q is a constant greater than 5.", font=question_font, fill='black')
    draw.text((20, 250), "     Given that the length PQ is equal to the length QR, determine the position", font=question_font, fill='black')
    draw.text((20, 280), "     vector of R.", font=question_font, fill='black')
    draw.text((700, 280), "[3]", font=question_font, fill='black')
    
    # Part (c)
    draw.text((20, 330), "(c) The point N is the midpoint of PR.", font=question_font, fill='black')
    draw.text((20, 360), "     Given that SN = 3QN, determine the position vector of S.", font=question_font, fill='black')
    draw.text((700, 360), "[2]", font=question_font, fill='black')
    
    # Part (d)
    draw.text((20, 410), "(d) State the name of the quadrilateral PQRS, giving a reason for your answer.", font=question_font, fill='black')
    draw.text((700, 410), "[2]", font=question_font, fill='black')
    
    # Add AI disclaimer
    draw.text((20, 500), "Disclaimer: AI-generated questions may contain errors. Verify before use.", 
              font=ImageFont.truetype("Arial.ttf", 10) if 'Arial.ttf' in ImageFont.truetype.__code__.co_names else ImageFont.load_default(), 
              fill='red')
    
    return image

def create_mock_questions():
    """Create a set of mock OCR Pure Mathematics questions"""
    # Create the directory for saving the questions if it doesn't exist
    output_dir = "data/mock_ocr_pure_maths_2024"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create and save each question
    q1 = create_triangle_question()
    q1.save(f"{output_dir}/q1_triangle.png")
    print(f"Created Question 1: Triangle properties")
    
    q2 = create_algebraic_fractions_question()
    q2.save(f"{output_dir}/q2_algebraic_fractions.png")
    print(f"Created Question 2: Algebraic fractions")
    
    q3 = create_differentiation_question()
    q3.save(f"{output_dir}/q3_differentiation.png")
    print(f"Created Question 3: Differentiation from first principles")
    
    q4 = create_vectors_question()
    q4.save(f"{output_dir}/q4_vectors.png")
    print(f"Created Question 4: Vectors in a quadrilateral")
    
    print(f"All mock questions saved to {output_dir}")

if __name__ == "__main__":
    create_mock_questions()