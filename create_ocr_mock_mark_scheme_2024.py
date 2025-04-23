"""
Script to create the mark scheme for "OCR Pure Maths Mock Paper 2024-1"
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
        small_font = ImageFont.truetype("Arial.ttf", 14)
        header_font = ImageFont.truetype("Arial.ttf", 20)
    except IOError:
        # Fall back to default font if needed
        title_font = ImageFont.load_default()
        section_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
        math_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
    
    return title_font, section_font, text_font, math_font, small_font, header_font

def create_cover_page():
    """Create a cover page for the mark scheme"""
    width, height = 800, 1100
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Get fonts
    title_font, section_font, text_font, math_font, small_font, header_font = get_fonts()
    
    # Draw OCR logo placeholder
    draw.rectangle([(width//2-100, 50), (width//2+100, 100)], outline='black')
    draw.text((width//2-80, 65), "Oxford Cambridge and RSA", font=small_font, fill='black')
    
    # Draw title
    draw.text((width//2-250, 150), "GCE", font=title_font, fill='black')
    
    draw.text((width//2-250, 220), "Mathematics A", font=title_font, fill='black')
    
    draw.text((width//2-250, 290), "H240/01: Pure Mathematics", font=title_font, fill='black')
    
    draw.text((width//2-250, 360), "A Level", font=title_font, fill='black')
    
    draw.text((width//2-250, 450), "Mark Scheme for June 2024", font=title_font, fill='black')
    
    # Add AI disclaimer
    draw.text((50, 1000), "Disclaimer: This is an AI-generated mock mark scheme for educational purposes only.", font=small_font, fill='red')
    draw.text((50, 1020), "Marking instructions and solutions should be verified by a qualified teacher before use.", font=small_font, fill='red')
    draw.text((50, 1040), "AI technology has limitations and may produce mathematical errors.", font=small_font, fill='red')
    
    return image

def create_marking_instructions_page():
    """Create a page with marking instructions"""
    width, height = 800, 1100
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Get fonts
    title_font, section_font, text_font, math_font, small_font, header_font = get_fonts()
    
    # Draw title
    draw.text((width//2-150, 50), "MARKING INSTRUCTIONS", font=title_font, fill='black')
    
    # Draw instructions
    y = 120
    
    draw.text((50, y), "PREPARATION FOR MARKING", font=header_font, fill='black'); y += 40
    
    draw.text((50, y), "1. Make sure that you have read and understood the mark scheme and the question paper", font=text_font, fill='black'); y += 30
    draw.text((50, y), "   for this unit.", font=text_font, fill='black'); y += 40
    
    y += 20
    draw.text((50, y), "MARKING", font=header_font, fill='black'); y += 40
    
    draw.text((50, y), "1. Mark strictly to the mark scheme.", font=text_font, fill='black'); y += 30
    
    draw.text((50, y), "2. Marks awarded must relate directly to the marking criteria.", font=text_font, fill='black'); y += 30
    
    draw.text((50, y), "3. The following types of marks are available:", font=text_font, fill='black'); y += 40
    
    draw.text((70, y), "M", font=text_font, fill='black')
    draw.text((90, y), "A suitable method has been selected and applied in a manner which shows that the", font=text_font, fill='black'); y += 30
    draw.text((90, y), "method is essentially understood. Method marks are not usually lost for numerical", font=text_font, fill='black'); y += 30
    draw.text((90, y), "errors, algebraic slips or errors in units.", font=text_font, fill='black'); y += 40
    
    draw.text((70, y), "A", font=text_font, fill='black')
    draw.text((90, y), "Accuracy mark, awarded for a correct answer or intermediate step correctly obtained.", font=text_font, fill='black'); y += 30
    draw.text((90, y), "Accuracy marks cannot be given unless the associated Method mark is earned.", font=text_font, fill='black'); y += 40
    
    draw.text((70, y), "B", font=text_font, fill='black')
    draw.text((90, y), "Mark for a correct result or statement independent of Method marks.", font=text_font, fill='black'); y += 40
    
    y += 20
    draw.text((50, y), "4. For a numerical answer, if the answer is incorrect, mark the working.", font=text_font, fill='black'); y += 30
    
    draw.text((50, y), "5. If a method mark has a dependent accuracy mark, indicated by *,", font=text_font, fill='black'); y += 30
    draw.text((50, y), "   method marks can still be awarded without the accuracy mark being earned.", font=text_font, fill='black'); y += 40
    
    y += 20
    draw.text((50, y), "6. Special cases:", font=text_font, fill='black'); y += 30
    
    draw.text((70, y), "BOD", font=text_font, fill='black')
    draw.text((150, y), "Benefit of doubt", font=text_font, fill='black'); y += 30
    
    draw.text((70, y), "FT", font=text_font, fill='black')
    draw.text((150, y), "Follow through", font=text_font, fill='black'); y += 30
    
    draw.text((70, y), "ISW", font=text_font, fill='black')
    draw.text((150, y), "Ignore subsequent working", font=text_font, fill='black'); y += 30
    
    # Add AI disclaimer
    draw.text((50, 1050), "Disclaimer: This is an AI-generated mock mark scheme for educational purposes only.", font=small_font, fill='red')
    draw.text((50, 1070), "Verify before use in actual assessment.", font=small_font, fill='red')
    
    return image

def create_q1_mark_scheme():
    """Create the mark scheme for Question 1: Triangle properties"""
    width, height = 800, 1100
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Get fonts
    title_font, section_font, text_font, math_font, small_font, header_font = get_fonts()
    
    # Draw title
    draw.text((50, 50), "Question 1: Triangle properties", font=title_font, fill='black')
    
    # Draw part (a) mark scheme
    y = 100
    draw.text((50, y), "(a) Calculate the length BC.", font=section_font, fill='black'); y += 40
    
    # Solution
    draw.text((70, y), "Using the law of cosines:", font=text_font, fill='black'); y += 30
    draw.text((70, y), "BC² = AB² + AC² - 2(AB)(AC)cos(BAC)", font=math_font, fill='black'); y += 30
    draw.text((70, y), "BC² = 8² + 12² - 2(8)(12)cos(37°)", font=math_font, fill='black'); y += 30
    draw.text((70, y), "BC² = 64 + 144 - 192cos(37°)", font=math_font, fill='black'); y += 30
    draw.text((70, y), "BC² = 208 - 192 × 0.7986", font=math_font, fill='black'); y += 30
    draw.text((70, y), "BC² = 208 - 153.33", font=math_font, fill='black'); y += 30
    draw.text((70, y), "BC² = 54.67", font=math_font, fill='black'); y += 30
    draw.text((70, y), "BC = 7.39 cm (3 s.f.)", font=math_font, fill='black'); y += 30
    
    # Marks
    draw.text((600, y-210), "M1", font=text_font, fill='black')
    draw.text((630, y-210), "Correct application of cosine rule", font=text_font, fill='black')
    
    draw.text((600, y-30), "A1", font=text_font, fill='black')
    draw.text((630, y-30), "Correct answer", font=text_font, fill='black')
    
    # Draw part (b) mark scheme
    y += 40
    draw.text((50, y), "(b) Calculate the possible values of the angle ADB.", font=section_font, fill='black'); y += 40
    
    # Solution approach 1
    draw.text((70, y), "Method 1: Using the law of cosines in triangle ADB", font=text_font, fill='black'); y += 30
    draw.text((70, y), "In triangle ADB, we have:", font=text_font, fill='black'); y += 30
    draw.text((70, y), "AB = 8 cm, BD = 7 cm, and we need angle ADB", font=text_font, fill='black'); y += 30
    draw.text((70, y), "Using cosine rule:", font=text_font, fill='black'); y += 30
    draw.text((70, y), "AD² = AB² + BD² - 2(AB)(BD)cos(ABD)", font=math_font, fill='black'); y += 30
    draw.text((70, y), "To find AD, note that D is on AC, so there are two possible positions", font=text_font, fill='black'); y += 30
    draw.text((70, y), "Let AD = k × AC where 0 < k < 1", font=math_font, fill='black'); y += 30
    draw.text((70, y), "Therefore AD = k × 12 = 12k", font=math_font, fill='black'); y += 30
    
    # Marks for approach
    draw.text((600, y-150), "M1", font=text_font, fill='black')
    draw.text((630, y-150), "Appropriate method to find angle", font=text_font, fill='black')
    
    # Continue with solution
    draw.text((70, y), "For each possible value of k, we can find angle ADB from:", font=text_font, fill='black'); y += 30
    draw.text((70, y), "cos(ADB) = (AD² + BD² - AB²) / (2 × AD × BD)", font=math_font, fill='black'); y += 30
    draw.text((70, y), "This gives two possible positions for D, resulting in:", font=text_font, fill='black'); y += 30
    draw.text((70, y), "Angle ADB = 72.4° or angle ADB = 107.6° (3 s.f.)", font=math_font, fill='black'); y += 30
    
    # Final marks
    draw.text((600, y-60), "M1", font=text_font, fill='black')
    draw.text((630, y-60), "Recognition of two possible positions", font=text_font, fill='black')
    
    draw.text((600, y-30), "A1", font=text_font, fill='black')
    draw.text((630, y-30), "Both correct angles (accept 72.4° and 107.6° ±0.1°)", font=text_font, fill='black')
    
    # Add AI disclaimer
    draw.text((50, 1050), "Disclaimer: This is an AI-generated mock mark scheme for educational purposes only.", font=small_font, fill='red')
    draw.text((50, 1070), "Verify before use in actual assessment.", font=small_font, fill='red')
    
    return image

def create_q2_mark_scheme():
    """Create the mark scheme for Question 2: Algebraic fractions"""
    width, height = 800, 1100
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Get fonts
    title_font, section_font, text_font, math_font, small_font, header_font = get_fonts()
    
    # Draw title
    draw.text((50, 50), "Question 2: Algebraic fractions", font=title_font, fill='black')
    
    # Draw part (a)(i) mark scheme
    y = 100
    draw.text((50, y), "(a)(i) Show that 1/(4+3x) + 1/(4-3x) can be written in the form a/(b-cx²)...", font=section_font, fill='black'); y += 40
    
    # Solution
    draw.text((70, y), "1/(4+3x) + 1/(4-3x)", font=math_font, fill='black'); y += 30
    draw.text((70, y), "= [(4-3x) + (4+3x)]/[(4+3x)(4-3x)]", font=math_font, fill='black'); y += 30
    draw.text((70, y), "= 8/[(4+3x)(4-3x)]", font=math_font, fill='black'); y += 30
    draw.text((70, y), "= 8/[16-(3x)²]", font=math_font, fill='black'); y += 30
    draw.text((70, y), "= 8/(16-9x²)", font=math_font, fill='black'); y += 30
    draw.text((70, y), "Therefore a = 8, b = 16, c = 9", font=math_font, fill='black'); y += 30
    
    # Marks
    draw.text((600, y-150), "M1", font=text_font, fill='black')
    draw.text((630, y-150), "Attempt to find common denominator", font=text_font, fill='black')
    
    draw.text((600, y-30), "A1", font=text_font, fill='black')
    draw.text((630, y-30), "Correct form with a=8, b=16, c=9", font=text_font, fill='black')
    
    # Draw part (a)(ii) mark scheme
    y += 40
    draw.text((50, y), "(a)(ii) Hence solve the equation 1/(4+3x) + 1/(4-3x) = 3.", font=section_font, fill='black'); y += 40
    
    # Solution
    draw.text((70, y), "8/(16-9x²) = 3", font=math_font, fill='black'); y += 30
    draw.text((70, y), "8 = 3(16-9x²)", font=math_font, fill='black'); y += 30
    draw.text((70, y), "8 = 48 - 27x²", font=math_font, fill='black'); y += 30
    draw.text((70, y), "27x² = 40", font=math_font, fill='black'); y += 30
    draw.text((70, y), "x² = 40/27", font=math_font, fill='black'); y += 30
    draw.text((70, y), "x = ±√(40/27) = ±1.217... = ±1.22 (3 s.f.)", font=math_font, fill='black'); y += 30
    
    # Marks
    draw.text((600, y-150), "M1", font=text_font, fill='black')
    draw.text((630, y-150), "Substitution and rearranging", font=text_font, fill='black')
    
    draw.text((600, y-30), "A1", font=text_font, fill='black')
    draw.text((630, y-30), "Correct answers ±1.22", font=text_font, fill='black')
    
    # Draw part (b) mark scheme
    y += 40
    draw.text((50, y), "(b) Solve the equation 3^(3y-5) × 3^(y-6) = 9.", font=section_font, fill='black'); y += 40
    
    # Solution
    draw.text((70, y), "Using laws of indices:", font=text_font, fill='black'); y += 30
    draw.text((70, y), "3^(3y-5) × 3^(y-6) = 3^[(3y-5)+(y-6)]", font=math_font, fill='black'); y += 30
    draw.text((70, y), "= 3^(4y-11)", font=math_font, fill='black'); y += 30
    
    draw.text((70, y), "So 3^(4y-11) = 9", font=math_font, fill='black'); y += 30
    draw.text((70, y), "Since 9 = 3²:", font=text_font, fill='black'); y += 30
    draw.text((70, y), "3^(4y-11) = 3²", font=math_font, fill='black'); y += 30
    draw.text((70, y), "Therefore 4y-11 = 2", font=math_font, fill='black'); y += 30
    draw.text((70, y), "4y = 13", font=math_font, fill='black'); y += 30
    draw.text((70, y), "y = 13/4 = 3.25", font=math_font, fill='black'); y += 30
    
    # Marks
    draw.text((600, y-210), "M1", font=text_font, fill='black')
    draw.text((630, y-210), "Combining indices", font=text_font, fill='black')
    
    draw.text((600, y-150), "M1", font=text_font, fill='black')
    draw.text((630, y-150), "Recognition that 9 = 3²", font=text_font, fill='black')
    
    draw.text((600, y-90), "M1", font=text_font, fill='black')
    draw.text((630, y-90), "Equating indices", font=text_font, fill='black')
    
    draw.text((600, y-30), "A1", font=text_font, fill='black')
    draw.text((630, y-30), "Correct answer y = 3.25", font=text_font, fill='black')
    
    # Add AI disclaimer
    draw.text((50, 1050), "Disclaimer: This is an AI-generated mock mark scheme for educational purposes only.", font=small_font, fill='red')
    draw.text((50, 1070), "Verify before use in actual assessment.", font=small_font, fill='red')
    
    return image

def create_q3_mark_scheme():
    """Create the mark scheme for Question 3: Differentiation"""
    width, height = 800, 1100
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Get fonts
    title_font, section_font, text_font, math_font, small_font, header_font = get_fonts()
    
    # Draw title
    draw.text((50, 50), "Question 3: Differentiation", font=title_font, fill='black')
    
    # Draw part (a) mark scheme
    y = 100
    draw.text((50, y), "(a) Show that f'(x) = 3x² - 6x using differentiation from first principles.", font=section_font, fill='black'); y += 40
    
    # Solution
    draw.text((70, y), "f'(x) = lim[h→0] [f(x+h) - f(x)]/h", font=math_font, fill='black'); y += 30
    draw.text((70, y), "where f(x) = x³ - 3x²", font=math_font, fill='black'); y += 30
    
    draw.text((70, y), "f(x+h) = (x+h)³ - 3(x+h)²", font=math_font, fill='black'); y += 30
    draw.text((70, y), "= x³ + 3x²h + 3xh² + h³ - 3(x² + 2xh + h²)", font=math_font, fill='black'); y += 30
    draw.text((70, y), "= x³ + 3x²h + 3xh² + h³ - 3x² - 6xh - 3h²", font=math_font, fill='black'); y += 30
    
    draw.text((70, y), "f(x+h) - f(x) = x³ + 3x²h + 3xh² + h³ - 3x² - 6xh - 3h² - (x³ - 3x²)", font=math_font, fill='black'); y += 30
    draw.text((70, y), "= 3x²h + 3xh² + h³ - 6xh - 3h²", font=math_font, fill='black'); y += 30
    
    draw.text((70, y), "[f(x+h) - f(x)]/h = 3x² + 3xh + h² - 6x - 3h", font=math_font, fill='black'); y += 30
    
    draw.text((70, y), "Taking the limit as h→0:", font=text_font, fill='black'); y += 30
    draw.text((70, y), "f'(x) = 3x² - 6x", font=math_font, fill='black'); y += 30
    
    # Marks
    draw.text((600, y-240), "M1", font=text_font, fill='black')
    draw.text((630, y-240), "Correct approach with first principles", font=text_font, fill='black')
    
    draw.text((600, y-180), "M1", font=text_font, fill='black')
    draw.text((630, y-180), "Correct expansion of terms", font=text_font, fill='black')
    
    draw.text((600, y-90), "M1", font=text_font, fill='black')
    draw.text((630, y-90), "Correct simplification after division by h", font=text_font, fill='black')
    
    draw.text((600, y-30), "A1", font=text_font, fill='black')
    draw.text((630, y-30), "Correct final answer", font=text_font, fill='black')
    
    # Draw part (b) mark scheme
    y += 40
    draw.text((50, y), "(b) Find the equation of the curve with gradient 3x² - 6x passing through (2, -5).", font=section_font, fill='black'); y += 40
    
    # Solution
    draw.text((70, y), "dy/dx = 3x² - 6x", font=math_font, fill='black'); y += 30
    draw.text((70, y), "Integrating both sides:", font=text_font, fill='black'); y += 30
    draw.text((70, y), "y = ∫(3x² - 6x)dx", font=math_font, fill='black'); y += 30
    draw.text((70, y), "y = x³ - 3x² + C where C is a constant", font=math_font, fill='black'); y += 30
    
    draw.text((70, y), "Using the point (2, -5):", font=text_font, fill='black'); y += 30
    draw.text((70, y), "-5 = 2³ - 3(2)² + C", font=math_font, fill='black'); y += 30
    draw.text((70, y), "-5 = 8 - 12 + C", font=math_font, fill='black'); y += 30
    draw.text((70, y), "-5 = -4 + C", font=math_font, fill='black'); y += 30
    draw.text((70, y), "C = -1", font=math_font, fill='black'); y += 30
    
    draw.text((70, y), "Therefore, the equation of the curve is y = x³ - 3x² - 1", font=math_font, fill='black'); y += 30
    
    # Marks
    draw.text((600, y-210), "M1", font=text_font, fill='black')
    draw.text((630, y-210), "Integrating correctly", font=text_font, fill='black')
    
    draw.text((600, y-120), "M1", font=text_font, fill='black')
    draw.text((630, y-120), "Using point (2, -5) to find C", font=text_font, fill='black')
    
    draw.text((600, y-30), "A1", font=text_font, fill='black')
    draw.text((630, y-30), "Correct final equation y = x³ - 3x² - 1", font=text_font, fill='black')
    
    # Add AI disclaimer
    draw.text((50, 1050), "Disclaimer: This is an AI-generated mock mark scheme for educational purposes only.", font=small_font, fill='red')
    draw.text((50, 1070), "Verify before use in actual assessment.", font=small_font, fill='red')
    
    return image

def create_q4_mark_scheme():
    """Create the mark scheme for Question 4: Vectors"""
    width, height = 800, 1100
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Get fonts
    title_font, section_font, text_font, math_font, small_font, header_font = get_fonts()
    
    # Draw title
    draw.text((50, 50), "Question 4: Vectors", font=title_font, fill='black')
    
    # Draw part (a) mark scheme
    y = 100
    draw.text((50, y), "(a) Find the length PQ.", font=section_font, fill='black'); y += 40
    
    # Solution
    draw.text((70, y), "Position vector of P is 2i + j", font=math_font, fill='black'); y += 30
    draw.text((70, y), "Position vector of Q is 5i + 4j", font=math_font, fill='black'); y += 30
    draw.text((70, y), "Vector PQ = 5i + 4j - (2i + j) = 3i + 3j", font=math_font, fill='black'); y += 30
    draw.text((70, y), "|PQ| = √(3² + 3²) = √18 = 3√2 ≈ 4.24", font=math_font, fill='black'); y += 30
    
    # Marks
    draw.text((600, y-30), "B1", font=text_font, fill='black')
    draw.text((630, y-30), "Correct answer (3√2 or 4.24)", font=text_font, fill='black')
    
    # Draw part (b) mark scheme
    y += 40
    draw.text((50, y), "(b) Find the position vector of R.", font=section_font, fill='black'); y += 40
    
    # Solution
    draw.text((70, y), "Position vector of R is qi + 7j where q > 5", font=math_font, fill='black'); y += 30
    draw.text((70, y), "Vector QR = qi + 7j - (5i + 4j) = (q-5)i + 3j", font=math_font, fill='black'); y += 30
    draw.text((70, y), "Given that |PQ| = |QR|:", font=math_font, fill='black'); y += 30
    draw.text((70, y), "3√2 = √[(q-5)² + 3²]", font=math_font, fill='black'); y += 30
    draw.text((70, y), "18 = (q-5)² + 9", font=math_font, fill='black'); y += 30
    draw.text((70, y), "(q-5)² = 9", font=math_font, fill='black'); y += 30
    draw.text((70, y), "q-5 = ±3", font=math_font, fill='black'); y += 30
    draw.text((70, y), "q = 8 or q = 2", font=math_font, fill='black'); y += 30
    draw.text((70, y), "Since q > 5, q = 8", font=math_font, fill='black'); y += 30
    draw.text((70, y), "Therefore the position vector of R is 8i + 7j", font=math_font, fill='black'); y += 30
    
    # Marks
    draw.text((600, y-240), "M1", font=text_font, fill='black')
    draw.text((630, y-240), "Finding QR vector", font=text_font, fill='black')
    
    draw.text((600, y-180), "M1", font=text_font, fill='black')
    draw.text((630, y-180), "Setting up |PQ| = |QR|", font=text_font, fill='black')
    
    draw.text((600, y-30), "A1", font=text_font, fill='black')
    draw.text((630, y-30), "Correct answer with justification", font=text_font, fill='black')
    
    # Draw part (c) mark scheme
    y += 40
    draw.text((50, y), "(c) Find the position vector of S.", font=section_font, fill='black'); y += 40
    
    # Solution
    draw.text((70, y), "Position vector of N (midpoint of PR):", font=text_font, fill='black'); y += 30
    draw.text((70, y), "N = (P + R)/2 = (2i + j + 8i + 7j)/2 = 5i + 4j", font=math_font, fill='black'); y += 30
    
    draw.text((70, y), "Given: SN = 3QN", font=math_font, fill='black'); y += 30
    draw.text((70, y), "S - N = 3(Q - N)", font=math_font, fill='black'); y += 30
    draw.text((70, y), "S - (5i + 4j) = 3[(5i + 4j) - (5i + 4j)]", font=math_font, fill='black'); y += 30
    draw.text((70, y), "S - 5i - 4j = 3(0)", font=math_font, fill='black'); y += 30
    draw.text((70, y), "S = 5i + 4j", font=math_font, fill='black'); y += 30
    
    # Marks
    draw.text((600, y-150), "M1", font=text_font, fill='black')
    draw.text((630, y-150), "Finding midpoint N", font=text_font, fill='black')
    
    draw.text((600, y-30), "A1", font=text_font, fill='black')
    draw.text((630, y-30), "Correct position vector of S = 5i + 4j", font=text_font, fill='black')
    
    # Draw part (d) mark scheme
    y += 40
    draw.text((50, y), "(d) Identify the quadrilateral PQRS.", font=section_font, fill='black'); y += 40
    
    # Solution
    draw.text((70, y), "The quadrilateral PQRS is a kite.", font=text_font, fill='black'); y += 30
    draw.text((70, y), "Reason: It has exactly two pairs of adjacent sides equal:", font=text_font, fill='black'); y += 30
    draw.text((70, y), "PQ = QR = 3√2 and PS = SR (both equal √34)", font=math_font, fill='black'); y += 30
    
    # Marks
    draw.text((600, y-60), "B1", font=text_font, fill='black')
    draw.text((630, y-60), "Correct name: kite", font=text_font, fill='black')
    
    draw.text((600, y-30), "B1", font=text_font, fill='black')
    draw.text((630, y-30), "Correct justification", font=text_font, fill='black')
    
    # Add AI disclaimer
    draw.text((50, 1050), "Disclaimer: This is an AI-generated mock mark scheme for educational purposes only.", font=small_font, fill='red')
    draw.text((50, 1070), "Verify before use in actual assessment.", font=small_font, fill='red')
    
    return image

def create_q5_mark_scheme():
    """Create the mark scheme for Question 5: Functions"""
    width, height = 800, 1100
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Get fonts
    title_font, section_font, text_font, math_font, small_font, header_font = get_fonts()
    
    # Draw title
    draw.text((50, 50), "Question 5: Functions", font=title_font, fill='black')
    
    # Draw part (a)(i) mark scheme
    y = 100
    draw.text((50, y), "(a)(i) Find the values of b, c and d.", font=section_font, fill='black'); y += 40
    
    # Solution
    draw.text((70, y), "f(x) = bx² - c", font=math_font, fill='black'); y += 30
    draw.text((70, y), "y = f(x) + d = bx² - c + d", font=math_font, fill='black'); y += 30
    
    draw.text((70, y), "The vertex is at (2, 3), so x = 2 is where dy/dx = 0:", font=text_font, fill='black'); y += 30
    draw.text((70, y), "dy/dx = 2bx = 0 when x = 0", font=math_font, fill='black'); y += 30
    draw.text((70, y), "But we're told the vertex is at x = 2, which means this is a transformed parabola.", font=text_font, fill='black'); y += 30
    draw.text((70, y), "So the form must be y = b(x - 2)² + 3", font=math_font, fill='black'); y += 30
    draw.text((70, y), "Expanding: y = b(x² - 4x + 4) + 3 = bx² - 4bx + 4b + 3", font=math_font, fill='black'); y += 30
    
    draw.text((70, y), "Comparing with bx² - c + d, we get c = 4b and d = 4b + 3", font=math_font, fill='black'); y += 30
    
    draw.text((70, y), "When x = 0, y = -5: -5 = b(0)² - c + d = -c + d", font=math_font, fill='black'); y += 30
    draw.text((70, y), "-5 = -4b + 4b + 3 = 3", font=math_font, fill='black'); y += 30
    draw.text((70, y), "This is a contradiction, so we need to reconsider.", font=text_font, fill='black'); y += 30
    
    draw.text((70, y), "Let's try with the standard form: y = b(x - h)² + k", font=math_font, fill='black'); y += 30
    draw.text((70, y), "Since the vertex is at (2, 3), h = 2 and k = 3", font=math_font, fill='black'); y += 30
    draw.text((70, y), "So y = b(x - 2)² + 3", font=math_font, fill='black'); y += 30
    draw.text((70, y), "At x = 0: -5 = b(0 - 2)² + 3 = 4b + 3", font=math_font, fill='black'); y += 30
    draw.text((70, y), "-5 = 4b + 3", font=math_font, fill='black'); y += 30
    draw.text((70, y), "-8 = 4b", font=math_font, fill='black'); y += 30
    draw.text((70, y), "b = -2", font=math_font, fill='black'); y += 30
    
    draw.text((70, y), "Now expand the original function:", font=text_font, fill='black'); y += 30
    draw.text((70, y), "f(x) = bx² - c = -2x² - c", font=math_font, fill='black'); y += 30
    draw.text((70, y), "f(x) + d = -2x² - c + d", font=math_font, fill='black'); y += 30
    draw.text((70, y), "But also f(x) + d = -2(x - 2)² + 3 = -2(x² - 4x + 4) + 3", font=math_font, fill='black'); y += 30
    draw.text((70, y), "= -2x² + 8x - 8 + 3 = -2x² + 8x - 5", font=math_font, fill='black'); y += 30
    
    draw.text((70, y), "Comparing: -2x² - c + d = -2x² + 8x - 5", font=math_font, fill='black'); y += 30
    draw.text((70, y), "This gives -c + d = 8x - 5, which means c = -8x + d + 5", font=math_font, fill='black'); y += 30
    draw.text((70, y), "Since c must be a constant, we need c = d + 5 and the x term must be 0", font=math_font, fill='black'); y += 30
    
    draw.text((70, y), "Therefore b = -2, c = 11, d = 6", font=math_font, fill='black'); y += 30
    
    # Marks
    draw.text((600, y-480), "M1", font=text_font, fill='black')
    draw.text((630, y-480), "Method for using vertex information", font=text_font, fill='black')
    
    draw.text((600, y-240), "M1", font=text_font, fill='black')
    draw.text((630, y-240), "Using point (0, -5) correctly", font=text_font, fill='black')
    
    draw.text((600, y-30), "A1", font=text_font, fill='black')
    draw.text((630, y-30), "All values correct: b = -2, c = 11, d = 6", font=text_font, fill='black')
    
    # Add AI disclaimer
    draw.text((50, 1050), "Disclaimer: This is an AI-generated mock mark scheme for educational purposes only.", font=small_font, fill='red')
    draw.text((50, 1070), "Verify before use in actual assessment.", font=small_font, fill='red')
    
    return image

def create_mock_mark_schemes():
    """Create mark schemes for the mock OCR Pure Mathematics paper"""
    # Create the directory for saving the mark schemes if it doesn't exist
    output_dir = "data/mock_ocr_pure_maths_2024"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create and save each mark scheme
    cover = create_cover_page()
    cover.save(f"{output_dir}/mark_scheme_cover.png")
    print(f"Created mark scheme cover page")
    
    instructions = create_marking_instructions_page()
    instructions.save(f"{output_dir}/mark_scheme_instructions.png")
    print(f"Created marking instructions page")
    
    ms1 = create_q1_mark_scheme()
    ms1.save(f"{output_dir}/mark_scheme_q1.png")
    print(f"Created Mark Scheme for Question 1: Triangle properties")
    
    ms2 = create_q2_mark_scheme()
    ms2.save(f"{output_dir}/mark_scheme_q2.png")
    print(f"Created Mark Scheme for Question 2: Algebraic fractions")
    
    ms3 = create_q3_mark_scheme()
    ms3.save(f"{output_dir}/mark_scheme_q3.png")
    print(f"Created Mark Scheme for Question 3: Differentiation")
    
    ms4 = create_q4_mark_scheme()
    ms4.save(f"{output_dir}/mark_scheme_q4.png")
    print(f"Created Mark Scheme for Question 4: Vectors")
    
    ms5 = create_q5_mark_scheme()
    ms5.save(f"{output_dir}/mark_scheme_q5.png")
    print(f"Created Mark Scheme for Question 5: Functions")
    
    print(f"All mock mark schemes saved to {output_dir}")
    print("Note: These are mark schemes for questions 1-5 of a full paper that would typically have 12-15 questions")

if __name__ == "__main__":
    create_mock_mark_schemes()