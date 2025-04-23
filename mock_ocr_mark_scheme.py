"""
Script to generate mock OCR Pure Mathematics mark schemes
"""

import os
from PIL import Image, ImageDraw, ImageFont

def get_fonts():
    """Get appropriate fonts for drawing mark scheme text"""
    try:
        # Try to load Arial or other common fonts
        title_font = ImageFont.truetype("Arial.ttf", 28)
        section_font = ImageFont.truetype("Arial.ttf", 22)
        text_font = ImageFont.truetype("Arial.ttf", 18)
        math_font = ImageFont.truetype("Arial.ttf", 18)
    except IOError:
        # Fall back to default font if needed
        title_font = ImageFont.load_default()
        section_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
        math_font = ImageFont.load_default()
    
    return title_font, section_font, text_font, math_font

def create_triangle_mark_scheme():
    """
    Create the mark scheme for the triangle properties question
    """
    width, height = 800, 900
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Get fonts
    title_font, section_font, text_font, math_font = get_fonts()
    
    # Draw the mark scheme title
    draw.text((20, 20), "Mark Scheme - Question 1", font=title_font, fill='black')
    
    # Part (a) mark scheme
    draw.text((20, 70), "Question 1(a)", font=section_font, fill='black')
    
    y = 110
    draw.text((20, y), "Using the law of cosines:", font=text_font, fill='black'); y += 30
    draw.text((20, y), "AC² = AB² + BC² - 2(AB)(BC)cos(37°)", font=math_font, fill='black'); y += 30
    draw.text((20, y), "AC² = 8² + 12² - 2(8)(12)cos(37°)", font=math_font, fill='black'); y += 30
    draw.text((20, y), "AC² = 64 + 144 - 192cos(37°)", font=math_font, fill='black'); y += 30
    draw.text((20, y), "AC² = 208 - 192 × 0.7986", font=math_font, fill='black'); y += 30
    draw.text((20, y), "AC² = 208 - 153.33", font=math_font, fill='black'); y += 30
    draw.text((20, y), "AC² = 54.67", font=math_font, fill='black'); y += 30
    draw.text((20, y), "AC = 7.39 cm (3 s.f.)", font=math_font, fill='black'); y += 30
    
    draw.text((600, 110), "M1", font=text_font, fill='black')
    draw.text((630, 110), "Use of cosine rule", font=text_font, fill='black')
    draw.text((600, 230), "A1", font=text_font, fill='black')
    draw.text((630, 230), "Correct answer", font=text_font, fill='black')
    
    # Part (b) mark scheme
    y += 20
    draw.text((20, y), "Question 1(b)", font=section_font, fill='black'); y += 40
    
    # First approach - using law of cosines
    draw.text((20, y), "Method 1: Using the law of cosines in triangle ADC", font=text_font, fill='black'); y += 30
    draw.text((20, y), "In triangle ADC, we have:", font=text_font, fill='black'); y += 30
    draw.text((20, y), "AD = 7 cm, AC = 7.39 cm, and we need to find angle ADB", font=text_font, fill='black'); y += 30
    draw.text((20, y), "Let x = angle ADB", font=text_font, fill='black'); y += 30
    draw.text((20, y), "cos(x) = (AD² + BD² - AB²) / (2 × AD × BD)", font=math_font, fill='black'); y += 30
    
    draw.text((600, y-60), "M1", font=text_font, fill='black')
    draw.text((630, y-60), "Appropriate method to find angle", font=text_font, fill='black')
    
    # Continue with solution
    draw.text((20, y), "Using the fact that D is on BC:", font=text_font, fill='black'); y += 30
    draw.text((20, y), "BD = BC - DC = 12 - DC", font=text_font, fill='black'); y += 30
    draw.text((20, y), "Using cosine rule in triangle ADC:", font=text_font, fill='black'); y += 30
    draw.text((20, y), "DC² = AD² + AC² - 2(AD)(AC)cos(∠DAC)", font=math_font, fill='black'); y += 30
    draw.text((20, y), "This gives two possible positions for D", font=text_font, fill='black'); y += 30
    draw.text((20, y), "Therefore angle ADB = 72.4° or angle ADB = 107.6° (3 s.f.)", font=math_font, fill='black'); y += 30
    
    draw.text((600, y-90), "M1", font=text_font, fill='black')
    draw.text((630, y-90), "Recognition of two possible positions", font=text_font, fill='black')
    draw.text((600, y-30), "A1", font=text_font, fill='black')
    draw.text((630, y-30), "Both correct angles", font=text_font, fill='black')
    
    # Add AI disclaimer
    draw.text((20, 850), "Disclaimer: AI-generated mark schemes may contain errors. Verify before use.", 
              font=ImageFont.truetype("Arial.ttf", 10) if 'Arial.ttf' in ImageFont.truetype.__code__.co_names else ImageFont.load_default(), 
              fill='red')
    
    return image

def create_algebraic_fractions_mark_scheme():
    """
    Create the mark scheme for the algebraic fractions question
    """
    width, height = 800, 900
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Get fonts
    title_font, section_font, text_font, math_font = get_fonts()
    
    # Draw the mark scheme title
    draw.text((20, 20), "Mark Scheme - Question 2", font=title_font, fill='black')
    
    # Part (a)(i) mark scheme
    draw.text((20, 70), "Question 2(a)(i)", font=section_font, fill='black')
    
    y = 110
    draw.text((20, y), "1/(4+3x) + 1/(4-3x)", font=math_font, fill='black'); y += 30
    draw.text((20, y), "= (4-3x + 4+3x)/[(4+3x)(4-3x)]", font=math_font, fill='black'); y += 30
    draw.text((20, y), "= 8/[(4+3x)(4-3x)]", font=math_font, fill='black'); y += 30
    draw.text((20, y), "= 8/[16-(3x)²]", font=math_font, fill='black'); y += 30
    draw.text((20, y), "= 8/(16-9x²)", font=math_font, fill='black'); y += 30
    
    draw.text((600, 110), "M1", font=text_font, fill='black')
    draw.text((630, 110), "Attempt to find common denominator", font=text_font, fill='black')
    draw.text((600, 200), "A1", font=text_font, fill='black')
    draw.text((630, 200), "Correct form with a=8, b=16, c=9", font=text_font, fill='black')
    
    # Part (a)(ii) mark scheme
    y += 20
    draw.text((20, y), "Question 2(a)(ii)", font=section_font, fill='black'); y += 40
    
    draw.text((20, y), "1/(4+3x) + 1/(4-3x) = 3", font=math_font, fill='black'); y += 30
    draw.text((20, y), "8/(16-9x²) = 3", font=math_font, fill='black'); y += 30
    draw.text((20, y), "8 = 3(16-9x²)", font=math_font, fill='black'); y += 30
    draw.text((20, y), "8 = 48 - 27x²", font=math_font, fill='black'); y += 30
    draw.text((20, y), "27x² = 40", font=math_font, fill='black'); y += 30
    draw.text((20, y), "x² = 40/27", font=math_font, fill='black'); y += 30
    draw.text((20, y), "x = ±√(40/27) = ±1.217... = ±1.22 (3 s.f.)", font=math_font, fill='black'); y += 30
    
    draw.text((600, y-120), "M1", font=text_font, fill='black')
    draw.text((630, y-120), "Substitution and rearranging", font=text_font, fill='black')
    draw.text((600, y-30), "A1", font=text_font, fill='black')
    draw.text((630, y-30), "Correct answers", font=text_font, fill='black')
    
    # Part (b) mark scheme
    y += 20
    draw.text((20, y), "Question 2(b)", font=section_font, fill='black'); y += 40
    
    draw.text((20, y), "Solve the equation 3^(3y-5) × 3^(y-6) = 9", font=math_font, fill='black'); y += 30
    draw.text((20, y), "Using laws of indices:", font=text_font, fill='black'); y += 30
    draw.text((20, y), "3^(3y-5) × 3^(y-6) = 3^[(3y-5)+(y-6)] = 3^(4y-11)", font=math_font, fill='black'); y += 30
    draw.text((20, y), "So 3^(4y-11) = 9", font=math_font, fill='black'); y += 30
    draw.text((20, y), "Since 9 = 3²:", font=text_font, fill='black'); y += 30
    draw.text((20, y), "3^(4y-11) = 3²", font=math_font, fill='black'); y += 30
    draw.text((20, y), "Therefore 4y-11 = 2", font=math_font, fill='black'); y += 30
    draw.text((20, y), "4y = 13", font=math_font, fill='black'); y += 30
    draw.text((20, y), "y = 13/4 = 3.25", font=math_font, fill='black'); y += 30
    
    draw.text((600, y-210), "M1", font=text_font, fill='black')
    draw.text((630, y-210), "Combining indices", font=text_font, fill='black')
    draw.text((600, y-150), "M1", font=text_font, fill='black')
    draw.text((630, y-150), "Recognition that 9 = 3²", font=text_font, fill='black')
    draw.text((600, y-90), "M1", font=text_font, fill='black')
    draw.text((630, y-90), "Equating indices", font=text_font, fill='black')
    draw.text((600, y-30), "A1", font=text_font, fill='black')
    draw.text((630, y-30), "Correct answer", font=text_font, fill='black')
    
    # Add AI disclaimer
    draw.text((20, 850), "Disclaimer: AI-generated mark schemes may contain errors. Verify before use.", 
              font=ImageFont.truetype("Arial.ttf", 10) if 'Arial.ttf' in ImageFont.truetype.__code__.co_names else ImageFont.load_default(), 
              fill='red')
    
    return image

def create_differentiation_mark_scheme():
    """
    Create the mark scheme for the differentiation question
    """
    width, height = 800, 900
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Get fonts
    title_font, section_font, text_font, math_font = get_fonts()
    
    # Draw the mark scheme title
    draw.text((20, 20), "Mark Scheme - Question 3", font=title_font, fill='black')
    
    # Part (a) mark scheme
    draw.text((20, 70), "Question 3(a)", font=section_font, fill='black')
    
    y = 110
    draw.text((20, y), "f'(x) = lim[h→0] [f(x+h) - f(x)]/h", font=math_font, fill='black'); y += 30
    draw.text((20, y), "= lim[h→0] [(x+h)³ - 3(x+h)² - (x³ - 3x²)]/h", font=math_font, fill='black'); y += 30
    draw.text((20, y), "= lim[h→0] [x³ + 3x²h + 3xh² + h³ - 3x² - 6xh - 3h² - x³ + 3x²]/h", font=math_font, fill='black'); y += 30
    draw.text((20, y), "= lim[h→0] [3x²h + 3xh² + h³ - 6xh - 3h²]/h", font=math_font, fill='black'); y += 30
    draw.text((20, y), "= lim[h→0] [3x² + 3xh + h² - 6x - 3h]", font=math_font, fill='black'); y += 30
    draw.text((20, y), "= 3x² - 6x", font=math_font, fill='black'); y += 30
    
    draw.text((600, 110), "M1", font=text_font, fill='black')
    draw.text((630, 110), "Correct approach with first principles", font=text_font, fill='black')
    draw.text((600, 170), "M1", font=text_font, fill='black')
    draw.text((630, 170), "Correct expansion of terms", font=text_font, fill='black')
    draw.text((600, 230), "M1", font=text_font, fill='black')
    draw.text((630, 230), "Correct simplification/cancellation", font=text_font, fill='black')
    draw.text((600, 290), "A1", font=text_font, fill='black')
    draw.text((630, 290), "Correct final answer", font=text_font, fill='black')
    
    # Part (b) mark scheme
    y += 20
    draw.text((20, y), "Question 3(b)", font=section_font, fill='black'); y += 40
    
    draw.text((20, y), "dy/dx = 3x² - 6x", font=math_font, fill='black'); y += 30
    draw.text((20, y), "Integrating both sides:", font=text_font, fill='black'); y += 30
    draw.text((20, y), "y = ∫(3x² - 6x)dx", font=math_font, fill='black'); y += 30
    draw.text((20, y), "y = x³ - 3x² + C where C is a constant", font=math_font, fill='black'); y += 30
    draw.text((20, y), "Using the point (2, -5):", font=text_font, fill='black'); y += 30
    draw.text((20, y), "-5 = 2³ - 3(2)² + C", font=math_font, fill='black'); y += 30
    draw.text((20, y), "-5 = 8 - 12 + C", font=math_font, fill='black'); y += 30
    draw.text((20, y), "-5 = -4 + C", font=math_font, fill='black'); y += 30
    draw.text((20, y), "C = -1", font=math_font, fill='black'); y += 30
    draw.text((20, y), "Therefore, the equation of the curve is y = x³ - 3x² - 1", font=math_font, fill='black'); y += 30
    
    draw.text((600, y-210), "M1", font=text_font, fill='black')
    draw.text((630, y-210), "Integrating correctly", font=text_font, fill='black')
    draw.text((600, y-120), "M1", font=text_font, fill='black')
    draw.text((630, y-120), "Using point (2, -5) to find C", font=text_font, fill='black')
    draw.text((600, y-30), "A1", font=text_font, fill='black')
    draw.text((630, y-30), "Correct final equation", font=text_font, fill='black')
    
    # Add AI disclaimer
    draw.text((20, 850), "Disclaimer: AI-generated mark schemes may contain errors. Verify before use.", 
              font=ImageFont.truetype("Arial.ttf", 10) if 'Arial.ttf' in ImageFont.truetype.__code__.co_names else ImageFont.load_default(), 
              fill='red')
    
    return image

def create_vectors_mark_scheme():
    """
    Create the mark scheme for the vectors question
    """
    width, height = 800, 900
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Get fonts
    title_font, section_font, text_font, math_font = get_fonts()
    
    # Draw the mark scheme title
    draw.text((20, 20), "Mark Scheme - Question 4", font=title_font, fill='black')
    
    # Part (a) mark scheme
    draw.text((20, 70), "Question 4(a)", font=section_font, fill='black')
    
    y = 110
    draw.text((20, y), "PQ = 5i + 4j - (2i + j) = 3i + 3j", font=math_font, fill='black'); y += 30
    draw.text((20, y), "|PQ| = √(3² + 3²) = √18 = 3√2 ≈ 4.24", font=math_font, fill='black'); y += 30
    
    draw.text((600, 120), "B1", font=text_font, fill='black')
    draw.text((630, 120), "Correct answer", font=text_font, fill='black')
    
    # Part (b) mark scheme
    y += 20
    draw.text((20, y), "Question 4(b)", font=section_font, fill='black'); y += 40
    
    draw.text((20, y), "QR = qi + 7j - (5i + 4j) = (q - 5)i + 3j", font=math_font, fill='black'); y += 30
    draw.text((20, y), "|PQ| = |QR|", font=math_font, fill='black'); y += 30
    draw.text((20, y), "3√2 = √[(q - 5)² + 3²]", font=math_font, fill='black'); y += 30
    draw.text((20, y), "18 = (q - 5)² + 9", font=math_font, fill='black'); y += 30
    draw.text((20, y), "(q - 5)² = 9", font=math_font, fill='black'); y += 30
    draw.text((20, y), "q - 5 = ±3", font=math_font, fill='black'); y += 30
    draw.text((20, y), "q = 8 or q = 2", font=math_font, fill='black'); y += 30
    draw.text((20, y), "Since q > 5, q = 8", font=math_font, fill='black'); y += 30
    draw.text((20, y), "Therefore the position vector of R is 8i + 7j", font=math_font, fill='black'); y += 30
    
    draw.text((600, y-180), "M1", font=text_font, fill='black')
    draw.text((630, y-180), "Finding QR vector", font=text_font, fill='black')
    draw.text((600, y-120), "M1", font=text_font, fill='black')
    draw.text((630, y-120), "Setting up |PQ| = |QR|", font=text_font, fill='black')
    draw.text((600, y-30), "A1", font=text_font, fill='black')
    draw.text((630, y-30), "Correct answer with justification", font=text_font, fill='black')
    
    # Part (c) mark scheme
    y += 20
    draw.text((20, y), "Question 4(c)", font=section_font, fill='black'); y += 40
    
    draw.text((20, y), "Position vector of N (midpoint of PR):", font=text_font, fill='black'); y += 30
    draw.text((20, y), "N = (P + R)/2 = (2i + j + 8i + 7j)/2 = 5i + 4j", font=math_font, fill='black'); y += 30
    draw.text((20, y), "Given: SN = 3QN", font=math_font, fill='black'); y += 30
    draw.text((20, y), "S - N = 3(Q - N)", font=math_font, fill='black'); y += 30
    draw.text((20, y), "S - (5i + 4j) = 3[(5i + 4j) - (5i + 4j)]", font=math_font, fill='black'); y += 30
    draw.text((20, y), "S - 5i - 4j = 3(0)", font=math_font, fill='black'); y += 30
    draw.text((20, y), "S = 5i + 4j", font=math_font, fill='black'); y += 30
    
    draw.text((600, y-120), "M1", font=text_font, fill='black')
    draw.text((630, y-120), "Finding midpoint N", font=text_font, fill='black')
    draw.text((600, y-30), "A1", font=text_font, fill='black')
    draw.text((630, y-30), "Correct position vector of S", font=text_font, fill='black')
    
    # Part (d) mark scheme
    y += 20
    draw.text((20, y), "Question 4(d)", font=section_font, fill='black'); y += 40
    
    draw.text((20, y), "The quadrilateral PQRS is a kite.", font=text_font, fill='black'); y += 30
    draw.text((20, y), "Reason: It has exactly two pairs of adjacent sides equal (PQ = QR and PS = SR).", font=text_font, fill='black'); y += 30
    draw.text((20, y), "This can be verified by calculating the lengths of all sides.", font=text_font, fill='black'); y += 30
    
    draw.text((600, y-60), "B1", font=text_font, fill='black')
    draw.text((630, y-60), "Correct name", font=text_font, fill='black')
    draw.text((600, y-30), "B1", font=text_font, fill='black')
    draw.text((630, y-30), "Correct justification", font=text_font, fill='black')
    
    # Add AI disclaimer
    draw.text((20, 850), "Disclaimer: AI-generated mark schemes may contain errors. Verify before use.", 
              font=ImageFont.truetype("Arial.ttf", 10) if 'Arial.ttf' in ImageFont.truetype.__code__.co_names else ImageFont.load_default(), 
              fill='red')
    
    return image

def create_mock_mark_schemes():
    """Create mark schemes for the mock OCR Pure Mathematics questions"""
    # Create the directory for saving the mark schemes if it doesn't exist
    output_dir = "data/mock_ocr_pure_maths_2024"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create and save each mark scheme
    ms1 = create_triangle_mark_scheme()
    ms1.save(f"{output_dir}/ms1_triangle.png")
    print(f"Created Mark Scheme for Question 1: Triangle properties")
    
    ms2 = create_algebraic_fractions_mark_scheme()
    ms2.save(f"{output_dir}/ms2_algebraic_fractions.png")
    print(f"Created Mark Scheme for Question 2: Algebraic fractions")
    
    ms3 = create_differentiation_mark_scheme()
    ms3.save(f"{output_dir}/ms3_differentiation.png")
    print(f"Created Mark Scheme for Question 3: Differentiation")
    
    ms4 = create_vectors_mark_scheme()
    ms4.save(f"{output_dir}/ms4_vectors.png")
    print(f"Created Mark Scheme for Question 4: Vectors")
    
    print(f"All mock mark schemes saved to {output_dir}")

if __name__ == "__main__":
    create_mock_mark_schemes()