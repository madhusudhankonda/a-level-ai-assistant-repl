"""
Script to create "OCR Pure Maths Mock Paper 2024-1" with original mock questions
based on the OCR Pure Mathematics paper style.
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
    """Try to load appropriate fonts, or use default if not available"""
    try:
        # Try to load Arial or similar font
        title_font = ImageFont.truetype("Arial.ttf", 32)
        header_font = ImageFont.truetype("Arial.ttf", 24)
        question_font = ImageFont.truetype("Arial.ttf", 22)
        math_font = ImageFont.truetype("Arial.ttf", 20)
        small_font = ImageFont.truetype("Arial.ttf", 16)
        formula_font = ImageFont.truetype("Arial.ttf", 18)
    except IOError:
        # Fall back to default font
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        question_font = ImageFont.load_default()
        math_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
        formula_font = ImageFont.load_default()
    
    return title_font, header_font, question_font, math_font, small_font, formula_font

def create_cover_page():
    """Create a cover page for the mock paper"""
    width, height = 800, 1100
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Get fonts
    title_font, header_font, question_font, math_font, small_font, formula_font = get_fonts()
    
    # Draw OCR logo placeholder
    draw.rectangle([(width//2-100, 50), (width//2+100, 100)], outline='black')
    draw.text((width//2-80, 65), "Oxford Cambridge and RSA", font=small_font, fill='black')
    
    # Draw title
    draw.text((width//2-180, 150), "Tuesday 4 June 2024 – Afternoon", font=header_font, fill='black')
    draw.text((width//2-220, 200), "A Level Mathematics A", font=title_font, fill='black')
    draw.text((width//2-220, 250), "H240/01 Pure Mathematics", font=title_font, fill='black')
    draw.text((width//2-150, 300), "Time allowed: 2 hours", font=header_font, fill='black')
    
    # Draw instructions box
    box_top = 400
    box_height = 350
    draw.rectangle([(50, box_top), (width-50, box_top+box_height)], outline='black')
    
    # Draw instructions
    y = box_top + 20
    draw.text((100, y), "INSTRUCTIONS", font=header_font, fill='black'); y += 40
    draw.text((100, y), "• Use black ink. You can use an HB pencil, but only for graphs and diagrams.", font=question_font, fill='black'); y += 30
    draw.text((100, y), "• Answer all the questions.", font=question_font, fill='black'); y += 30
    draw.text((100, y), "• Where appropriate, your answer should be supported with working. Marks might be", font=question_font, fill='black'); y += 30
    draw.text((100, y), "  given for using a correct method, even if your answer is wrong.", font=question_font, fill='black'); y += 30
    draw.text((100, y), "• Give non-exact numerical answers correct to 3 significant figures unless a different", font=question_font, fill='black'); y += 30
    draw.text((100, y), "  degree of accuracy is specified in the question.", font=question_font, fill='black'); y += 30
    draw.text((100, y), "• The acceleration due to gravity is denoted by g m s⁻². When a numerical value is", font=question_font, fill='black'); y += 30
    draw.text((100, y), "  needed use g = 9.8 unless a different value is specified in the question.", font=question_font, fill='black'); y += 30
    
    # Draw information box
    box_top = 780
    box_height = 150
    draw.rectangle([(50, box_top), (width-50, box_top+box_height)], outline='black')
    
    # Draw information
    y = box_top + 20
    draw.text((100, y), "INFORMATION", font=header_font, fill='black'); y += 40
    draw.text((100, y), "• The total mark for this paper is 100.", font=question_font, fill='black'); y += 30
    draw.text((100, y), "• The marks for each question are shown in brackets [ ].", font=question_font, fill='black'); y += 30
    
    # Draw disclaimer
    draw.text((50, 1050), "Disclaimer: This is an AI-generated mock exam paper for educational purposes only.", font=small_font, fill='red')
    draw.text((50, 1070), "Questions and answers should be verified before use.", font=small_font, fill='red')
    
    return image

def create_formulae_page():
    """Create a page with the formulae for the mock paper"""
    width, height = 800, 1100
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Get fonts
    title_font, header_font, question_font, math_font, small_font, formula_font = get_fonts()
    
    # Draw title
    draw.text((width//2-80, 50), "Formulae", font=title_font, fill='black')
    draw.text((width//2-200, 90), "A Level Mathematics A (H240)", font=header_font, fill='black')
    
    # Draw formulae sections
    y = 150
    
    # Arithmetic series
    draw.text((50, y), "Arithmetic series", font=header_font, fill='black'); y += 40
    draw.text((50, y), "Sn = ½n(a + l) = ½n[2a + (n - 1)d]", font=formula_font, fill='black'); y += 60
    
    # Geometric series
    draw.text((50, y), "Geometric series", font=header_font, fill='black'); y += 40
    draw.text((50, y), "Sn = a(1 - rⁿ)/(1 - r)", font=formula_font, fill='black'); y += 30
    draw.text((50, y), "S∞ = a/(1 - r) for |r| < 1", font=formula_font, fill='black'); y += 60
    
    # Binomial series
    draw.text((50, y), "Binomial series", font=header_font, fill='black'); y += 40
    draw.text((50, y), "(a + b)ⁿ = aⁿ + nC₁aⁿ⁻¹b + nC₂aⁿ⁻²b² + ... + nCᵣaⁿ⁻ʳbʳ + ... + bⁿ", font=formula_font, fill='black'); y += 30
    draw.text((50, y), "where nCᵣ = (n!)/[r!(n-r)!]", font=formula_font, fill='black'); y += 50
    
    # Differentiation
    draw.text((50, y), "Differentiation", font=header_font, fill='black'); y += 40
    draw.text((50, y), "f(x)                    f'(x)", font=formula_font, fill='black'); y += 30
    draw.text((50, y), "tan kx                  k sec² kx", font=formula_font, fill='black'); y += 30
    draw.text((50, y), "sec x                   sec x tan x", font=formula_font, fill='black'); y += 30
    draw.text((50, y), "cosec x                 -cosec x cot x", font=formula_font, fill='black'); y += 40
    
    # Quotient rule
    draw.text((50, y), "Quotient rule: If y = u/v, then dy/dx = (v·du/dx - u·dv/dx)/v²", font=formula_font, fill='black'); y += 60
    
    # Integration
    draw.text((50, y), "Integration", font=header_font, fill='black'); y += 40
    draw.text((50, y), "∫(1/x)dx = ln|x| + c", font=formula_font, fill='black'); y += 30
    draw.text((50, y), "∫eᵏˣdx = (1/k)eᵏˣ + c", font=formula_font, fill='black'); y += 30
    draw.text((50, y), "∫[f'(x)/f(x)]dx = ln|f(x)| + c", font=formula_font, fill='black'); y += 60
    
    # Small angle approximations
    draw.text((50, y), "Small angle approximations", font=header_font, fill='black'); y += 40
    draw.text((50, y), "sin θ ≈ θ, cos θ ≈ 1 - θ²/2, tan θ ≈ θ where θ is in radians", font=formula_font, fill='black'); y += 60
    
    # Draw disclaimer
    draw.text((50, 1050), "Disclaimer: This is an AI-generated mock exam paper for educational purposes only.", font=small_font, fill='red')
    draw.text((50, 1070), "Questions and answers should be verified before use.", font=small_font, fill='red')
    
    return image

def create_q1_triangle_problem():
    """Create a question on triangle properties"""
    width, height = 800, 1100
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Get fonts
    title_font, header_font, question_font, math_font, small_font, formula_font = get_fonts()
    
    # Draw question number
    draw.text((50, 50), "1", font=title_font, fill='black')
    
    # Draw triangle diagram (basic representation)
    center_x, center_y = width//2, 250
    triangle_size = 150
    
    # Triangle vertices
    x_A, y_A = center_x, center_y - triangle_size
    x_B, y_B = center_x + triangle_size, center_y + triangle_size
    x_C, y_C = center_x - triangle_size, center_y + triangle_size
    
    # Draw the triangle
    draw.line([(x_A, y_A), (x_B, y_B), (x_C, y_C), (x_A, y_A)], fill='black', width=2)
    
    # Label the vertices
    draw.text((x_A-10, y_A-30), "A", font=question_font, fill='black')
    draw.text((x_B+10, y_B+10), "B", font=question_font, fill='black')
    draw.text((x_C-30, y_C+10), "C", font=question_font, fill='black')
    
    # Label the sides
    draw.text((x_A+triangle_size//2-20, y_A+triangle_size//2-20), "8 cm", font=math_font, fill='black')
    draw.text((x_A-triangle_size//2, y_A+triangle_size//2-20), "12 cm", font=math_font, fill='black')
    draw.text((center_x-20, center_y+triangle_size+10), "10 cm", font=math_font, fill='black')
    
    # Draw the angle
    angle_radius = 40
    draw.arc([(x_A-angle_radius, y_A-angle_radius), 
              (x_A+angle_radius, y_A+angle_radius)], 
             250, 290, fill='black', width=2)
    
    # Label the angle
    draw.text((x_A-20, y_A+20), "37°", font=math_font, fill='black')
    
    # Question text
    y = 400
    draw.text((100, y), "In the triangle ABC, the length AB = 8 cm, the length AC = 12 cm and the angle", font=question_font, fill='black'); y += 30
    draw.text((100, y), "BAC = 37°.", font=question_font, fill='black'); y += 50
    
    # Part (a)
    draw.text((100, y), "(a) Calculate the length BC.", font=question_font, fill='black'); y += 30
    draw.text((700, y-30), "[2]", font=question_font, fill='black'); y += 50
    
    # Part (b)
    draw.text((100, y), "D is the point on AC such that the length BD = 7 cm.", font=question_font, fill='black'); y += 50
    draw.text((100, y), "(b) Calculate the possible values of the angle ADB.", font=question_font, fill='black'); y += 30
    draw.text((700, y-30), "[3]", font=question_font, fill='black'); y += 50
    
    # Add AI disclaimer
    draw.text((50, 1050), "Disclaimer: This is an AI-generated mock exam question for educational purposes only.", font=small_font, fill='red')
    draw.text((50, 1070), "Verify mathematical accuracy before using for actual assessment.", font=small_font, fill='red')
    
    return image

def create_q2_algebraic_fractions():
    """Create a question on algebraic fractions and logarithmic equations"""
    width, height = 800, 1100
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Get fonts
    title_font, header_font, question_font, math_font, small_font, formula_font = get_fonts()
    
    # Draw question number
    draw.text((50, 50), "2", font=title_font, fill='black')
    
    # Question text
    y = 120
    
    # Part (a)
    draw.text((100, y), "(a) (i) Show that", font=question_font, fill='black'); y += 40
    draw.text((150, y), "1/(4+3x) + 1/(4-3x)", font=math_font, fill='black'); y += 40
    draw.text((150, y), "can be written in the form a/(b-cx²), where a, b and c are", font=question_font, fill='black'); y += 30
    draw.text((150, y), "constants to be determined.", font=question_font, fill='black'); y += 30
    draw.text((700, y-30), "[2]", font=question_font, fill='black'); y += 50
    
    # Part (a)(ii)
    draw.text((120, y), "(ii) Hence solve the equation", font=question_font, fill='black'); y += 40
    draw.text((150, y), "1/(4+3x) + 1/(4-3x) = 3", font=math_font, fill='black'); y += 30
    draw.text((700, y-30), "[2]", font=question_font, fill='black'); y += 50
    
    # Part (b)
    draw.text((100, y), "(b) In this question you must show detailed reasoning.", font=question_font, fill='black'); y += 50
    draw.text((150, y), "Solve the equation 3^(3y-5) × 3^(y-6) = 9", font=math_font, fill='black'); y += 30
    draw.text((700, y-30), "[4]", font=question_font, fill='black'); y += 70
    
    # Additional space for working
    y += 100
    
    # Add AI disclaimer
    draw.text((50, 1050), "Disclaimer: This is an AI-generated mock exam question for educational purposes only.", font=small_font, fill='red')
    draw.text((50, 1070), "Verify mathematical accuracy before using for actual assessment.", font=small_font, fill='red')
    
    return image

def create_q3_differentiation():
    """Create a question on differentiation from first principles"""
    width, height = 800, 1100
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Get fonts
    title_font, header_font, question_font, math_font, small_font, formula_font = get_fonts()
    
    # Draw question number
    draw.text((50, 50), "3", font=title_font, fill='black')
    
    # Question text
    y = 120
    
    # Part (a)
    draw.text((100, y), "(a) Given that f(x) = x³ - 3x², use differentiation from first principles to show", font=question_font, fill='black'); y += 30
    draw.text((100, y), "    that f'(x) = 3x² - 6x.", font=question_font, fill='black'); y += 30
    draw.text((700, y-30), "[4]", font=question_font, fill='black'); y += 70
    
    # Part (b)
    draw.text((100, y), "(b) The gradient of a curve is given by dy/dx = 3x² - 6x and the curve passes", font=question_font, fill='black'); y += 30
    draw.text((100, y), "    through the point (2, -5).", font=question_font, fill='black'); y += 50
    draw.text((100, y), "    Find the equation of the curve.", font=question_font, fill='black'); y += 30
    draw.text((700, y-30), "[3]", font=question_font, fill='black'); y += 70
    
    # Additional space for working
    y += 100
    
    # Add AI disclaimer
    draw.text((50, 1050), "Disclaimer: This is an AI-generated mock exam question for educational purposes only.", font=small_font, fill='red')
    draw.text((50, 1070), "Verify mathematical accuracy before using for actual assessment.", font=small_font, fill='red')
    
    return image

def create_q4_vectors():
    """Create a question on vectors in 2D"""
    width, height = 800, 1100
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Get fonts
    title_font, header_font, question_font, math_font, small_font, formula_font = get_fonts()
    
    # Draw question number
    draw.text((50, 50), "4", font=title_font, fill='black')
    
    # Question text
    y = 120
    
    # Main question statement
    draw.text((100, y), "It is given that PQRS is a quadrilateral. The position vector of P is 2i + j, and the", font=question_font, fill='black'); y += 30
    draw.text((100, y), "position vector of Q is 5i + 4j.", font=question_font, fill='black'); y += 50
    
    # Draw simple vector diagram
    center_x, center_y = width//2, 300
    scale = 30  # pixels per unit
    
    # Points P and Q
    px, py = center_x + 2*scale, center_y - 1*scale
    qx, qy = center_x + 5*scale, center_y - 4*scale
    
    # Draw axes
    draw.line([(center_x, center_y), (center_x + 8*scale, center_y)], fill='black', width=1)  # x-axis
    draw.line([(center_x, center_y), (center_x, center_y - 8*scale)], fill='black', width=1)  # y-axis
    
    # Label axes
    draw.text((center_x + 8*scale + 5, center_y), "i", font=math_font, fill='black')
    draw.text((center_x - 5, center_y - 8*scale - 10), "j", font=math_font, fill='black')
    draw.text((center_x - 5, center_y + 5), "O", font=math_font, fill='black')
    
    # Draw vectors
    draw.line([(center_x, center_y), (px, py)], fill='blue', width=2)  # Vector OP
    draw.line([(center_x, center_y), (qx, qy)], fill='red', width=2)   # Vector OQ
    
    # Label points
    draw.text((px + 5, py - 5), "P", font=math_font, fill='blue')
    draw.text((qx + 5, qy - 5), "Q", font=math_font, fill='red')
    
    y = 400
    
    # Part (a)
    draw.text((100, y), "(a) Find the length PQ.", font=question_font, fill='black'); y += 30
    draw.text((700, y-30), "[1]", font=question_font, fill='black'); y += 50
    
    # Part (b)
    draw.text((100, y), "(b) The position vector of R is qi + 7j where q is a constant greater than 5.", font=question_font, fill='black'); y += 30
    draw.text((100, y), "    Given that the length PQ is equal to the length QR, determine the position", font=question_font, fill='black'); y += 30
    draw.text((100, y), "    vector of R.", font=question_font, fill='black'); y += 30
    draw.text((700, y-30), "[3]", font=question_font, fill='black'); y += 50
    
    # Part (c)
    draw.text((100, y), "(c) The point N is the midpoint of PR.", font=question_font, fill='black'); y += 30
    draw.text((100, y), "    Given that SN = 3QN, determine the position vector of S.", font=question_font, fill='black'); y += 30
    draw.text((700, y-30), "[2]", font=question_font, fill='black'); y += 50
    
    # Part (d)
    draw.text((100, y), "(d) State the name of the quadrilateral PQRS, giving a reason for your answer.", font=question_font, fill='black'); y += 30
    draw.text((700, y-30), "[2]", font=question_font, fill='black'); y += 50
    
    # Add AI disclaimer
    draw.text((50, 1050), "Disclaimer: This is an AI-generated mock exam question for educational purposes only.", font=small_font, fill='red')
    draw.text((50, 1070), "Verify mathematical accuracy before using for actual assessment.", font=small_font, fill='red')
    
    return image

def create_q5_functions():
    """Create a question on functions and transformations"""
    width, height = 800, 1100
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Get fonts
    title_font, header_font, question_font, math_font, small_font, formula_font = get_fonts()
    
    # Draw question number
    draw.text((50, 50), "5", font=title_font, fill='black')
    
    # Question text
    y = 120
    
    # Part (a)
    draw.text((100, y), "(a) The function f(x) is defined for all values of x as f(x) = bx² - c, where b and c", font=question_font, fill='black'); y += 30
    draw.text((100, y), "    are positive constants.", font=question_font, fill='black'); y += 50
    
    # Part (a)(i)
    draw.text((120, y), "(i) The graph of y = f(x) + d, where d is a constant, has a vertex at (2, 3)", font=question_font, fill='black'); y += 30
    draw.text((120, y), "    and crosses the y-axis at (0, -5).", font=question_font, fill='black'); y += 30
    draw.text((120, y), "    Find the values of b, c and d.", font=question_font, fill='black'); y += 30
    draw.text((700, y-30), "[3]", font=question_font, fill='black'); y += 50
    
    # Part (a)(ii)
    draw.text((120, y), "(ii) Find the range of the function f(x).", font=question_font, fill='black'); y += 30
    draw.text((700, y-30), "[1]", font=question_font, fill='black'); y += 50
    
    # Part (b)
    draw.text((100, y), "(b) The function g(x) is defined for x > p as g(x) = q/(x-p), where p and q are", font=question_font, fill='black'); y += 30
    draw.text((100, y), "    positive constants.", font=question_font, fill='black'); y += 50
    
    # Part (b)(i)
    draw.text((120, y), "(i) Find, in terms of p and q, an expression for g⁻¹(x), stating the domain", font=question_font, fill='black'); y += 30
    draw.text((120, y), "    of g⁻¹(x).", font=question_font, fill='black'); y += 30
    draw.text((700, y-30), "[3]", font=question_font, fill='black'); y += 50
    
    # Part (b)(ii)
    draw.text((120, y), "(ii) State the set of values of q for which the equation g(x) = g⁻¹(x) has", font=question_font, fill='black'); y += 30
    draw.text((120, y), "     exactly one solution.", font=question_font, fill='black'); y += 30
    draw.text((700, y-30), "[1]", font=question_font, fill='black'); y += 50
    
    # Add AI disclaimer
    draw.text((50, 1050), "Disclaimer: This is an AI-generated mock exam question for educational purposes only.", font=small_font, fill='red')
    draw.text((50, 1070), "Verify mathematical accuracy before using for actual assessment.", font=small_font, fill='red')
    
    return image

def create_ocr_mock_paper():
    """Create a complete mock OCR Pure Mathematics paper"""
    # Create the directory for saving the paper if it doesn't exist
    output_dir = "data/mock_ocr_pure_maths_2024"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create and save each page of the paper
    cover = create_cover_page()
    cover.save(f"{output_dir}/cover.png")
    print(f"Created cover page")
    
    formulae = create_formulae_page()
    formulae.save(f"{output_dir}/formulae.png")
    print(f"Created formulae page")
    
    q1 = create_q1_triangle_problem()
    q1.save(f"{output_dir}/q1_triangle.png")
    print(f"Created Question 1: Triangle properties")
    
    q2 = create_q2_algebraic_fractions()
    q2.save(f"{output_dir}/q2_algebraic_fractions.png")
    print(f"Created Question 2: Algebraic fractions")
    
    q3 = create_q3_differentiation()
    q3.save(f"{output_dir}/q3_differentiation.png")
    print(f"Created Question 3: Differentiation from first principles")
    
    q4 = create_q4_vectors()
    q4.save(f"{output_dir}/q4_vectors.png")
    print(f"Created Question 4: Vectors in a quadrilateral")
    
    q5 = create_q5_functions()
    q5.save(f"{output_dir}/q5_functions.png")
    print(f"Created Question 5: Functions and transformations")
    
    print(f"Complete mock paper saved to {output_dir}")
    print("Note: This is question set 1-5 of a full paper that would typically have 12-15 questions")

if __name__ == "__main__":
    create_ocr_mock_paper()