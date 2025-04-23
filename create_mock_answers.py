#!/usr/bin/env python3
"""
Script to create mock student answers for selected questions
"""
import os
import sys
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io

# Add the current directory to sys.path to ensure imports work
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import app, db
from models import Question, MockStudentAnswer

def create_mock_answer_image(question_path, level="good"):
    """
    Create a mock student answer image based on the original question
    and a specified quality level
    
    Args:
        question_path: Path to the question image
        level: Quality level of the answer ("excellent", "good", "average", "needs_improvement")
        
    Returns:
        Path to the generated mock answer image
    """
    # Load the question image
    try:
        question_img = Image.open(question_path).convert("RGB")
    except Exception as e:
        print(f"Error opening question image: {e}")
        return None
        
    # Calculate dimensions for the answer space
    width, height = question_img.size
    answer_height = height + 400  # Add 400px at the bottom for the student answer
    
    # Create a new image with the question on top and space for the answer below
    answer_img = Image.new("RGB", (width, answer_height), color=(255, 255, 255))
    answer_img.paste(question_img, (0, 0))
    
    # Get a drawing context
    draw = ImageDraw.Draw(answer_img)
    
    # Add a dividing line
    draw.line([(0, height), (width, height)], fill=(0, 0, 0), width=2)
    
    # Add "Student Answer" label
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        # Use default font if Arial is not available
        font = ImageFont.load_default()
        
    draw.text((20, height + 10), "Student Answer:", fill=(0, 0, 0), font=font)
    
    # Draw the mock answer content based on level
    if question_path.endswith("q1_c9a127e4794c482f9309368b4b41c518.png"):
        # This is Question 1 from Pure Maths June 2023
        if level == "excellent":
            # Draw an excellent answer for part (a)
            draw.text((30, height + 50), "(a) Using the cosine rule in triangle ABC:", fill=(0, 0, 0), font=font)
            draw.text((30, height + 90), "BC² = AB² + AC² - 2(AB)(AC)cos(BAC)", fill=(0, 0, 0), font=font)
            draw.text((30, height + 130), "BC² = 6² + 15² - 2(6)(15)cos(30°)", fill=(0, 0, 0), font=font)
            draw.text((30, height + 170), "BC² = 36 + 225 - 2(6)(15)(0.866)", fill=(0, 0, 0), font=font)
            draw.text((30, height + 210), "BC² = 36 + 225 - 155.88", fill=(0, 0, 0), font=font)
            draw.text((30, height + 250), "BC² = 105.12", fill=(0, 0, 0), font=font)
            draw.text((30, height + 290), "BC = √105.12 = 10.25 cm (3 s.f.)", fill=(0, 0, 0), font=font)
            
            # Draw an excellent answer for part (b)
            draw.text((30, height + 340), "(b) Point D divides AC with BD = 4 cm", fill=(0, 0, 0), font=font)
            draw.text((30, height + 380), "Let's use the sine rule with triangle ABD:", fill=(0, 0, 0), font=font)
            draw.text((30, height + 420), "sin(ADB)/AB = sin(BAD)/BD", fill=(0, 0, 0), font=font)
            draw.text((30, height + 460), "sin(ADB)/6 = sin(30°)/4", fill=(0, 0, 0), font=font)
            draw.text((30, height + 500), "sin(ADB) = 6 × sin(30°)/4 = 6 × 0.5/4 = 0.75", fill=(0, 0, 0), font=font)
            draw.text((30, height + 540), "ADB = arcsin(0.75)", fill=(0, 0, 0), font=font)
            draw.text((30, height + 580), "ADB = 48.6° or ADB = 180° - 48.6° = 131.4°", fill=(0, 0, 0), font=font)
            draw.text((30, height + 620), "Therefore, angle ADB = 48.6° or 131.4° (3 s.f.)", fill=(0, 0, 0), font=font)
            
        elif level == "good":
            # Draw a good answer with minor issues
            draw.text((30, height + 50), "(a) Using cosine rule:", fill=(0, 0, 0), font=font)
            draw.text((30, height + 90), "BC² = AB² + AC² - 2(AB)(AC)cos(BAC)", fill=(0, 0, 0), font=font)
            draw.text((30, height + 130), "BC² = 6² + 15² - 2(6)(15)cos(30°)", fill=(0, 0, 0), font=font)
            draw.text((30, height + 170), "BC² = 36 + 225 - 2(6)(15)(0.866)", fill=(0, 0, 0), font=font)
            draw.text((30, height + 210), "BC² = 36 + 225 - 155.88", fill=(0, 0, 0), font=font)
            draw.text((30, height + 250), "BC² = 105.12", fill=(0, 0, 0), font=font)
            draw.text((30, height + 290), "BC = 10.25 cm", fill=(0, 0, 0), font=font)
            
            # Part (b) with a calculation error
            draw.text((30, height + 340), "(b) For angle ADB:", fill=(0, 0, 0), font=font)
            draw.text((30, height + 380), "Using the sine rule:", fill=(0, 0, 0), font=font)
            draw.text((30, height + 420), "sin(ADB)/AB = sin(BAD)/BD", fill=(0, 0, 0), font=font)
            draw.text((30, height + 460), "sin(ADB)/6 = sin(30°)/4", fill=(0, 0, 0), font=font)
            draw.text((30, height + 500), "sin(ADB) = 6 × sin(30°)/4 = 6 × 0.5/4 = 0.75", fill=(0, 0, 0), font=font)
            draw.text((30, height + 540), "ADB = arcsin(0.75) = 48.6°", fill=(0, 0, 0), font=font)
            # Forgot to mention the second solution
            
        elif level == "average":
            # Draw an average answer with more serious issues
            draw.text((30, height + 50), "(a) Using cosine rule:", fill=(0, 0, 0), font=font)
            draw.text((30, height + 90), "BC² = AB² + AC² - 2(AB)(AC)cos(BAC)", fill=(0, 0, 0), font=font)
            draw.text((30, height + 130), "BC² = 6² + 15² - 2(6)(15)cos(30°)", fill=(0, 0, 0), font=font)
            draw.text((30, height + 170), "BC² = 36 + 225 - 180cos(30°)", fill=(0, 0, 0), font=font)
            draw.text((30, height + 210), "BC² = 261 - 180 × 0.866", fill=(0, 0, 0), font=font)
            draw.text((30, height + 250), "BC² = 261 - 155.9 = 105.1", fill=(0, 0, 0), font=font)
            draw.text((30, height + 290), "BC = √105.1 = 10.3 cm", fill=(0, 0, 0), font=font)
            
            # Part (b) with conceptual error
            draw.text((30, height + 340), "(b) For the angle ADB:", fill=(0, 0, 0), font=font)
            draw.text((30, height + 380), "Let's calculate using the sine rule in triangle ABD:", fill=(0, 0, 0), font=font)
            draw.text((30, height + 420), "sin(ADB)/sin(30°) = AB/BD", fill=(0, 0, 0), font=font)
            draw.text((30, height + 460), "sin(ADB)/0.5 = 6/4", fill=(0, 0, 0), font=font)
            draw.text((30, height + 500), "sin(ADB) = 0.5 × 6/4 = 0.75", fill=(0, 0, 0), font=font)
            draw.text((30, height + 540), "ADB = arcsin(0.75) = 48.6°", fill=(0, 0, 0), font=font)
            
        elif level == "needs_improvement":
            # Draw a poor answer with significant issues
            draw.text((30, height + 50), "(a) To find BC:", fill=(0, 0, 0), font=font)
            draw.text((30, height + 90), "I think I need to use the cosine rule", fill=(0, 0, 0), font=font)
            draw.text((30, height + 130), "BC² = AB² + AC² - 2(AB)(AC)cos(C)", fill=(0, 0, 0), font=font)
            draw.text((30, height + 170), "BC² = 6² + 15² - 2(6)(15)cos(30°)", fill=(0, 0, 0), font=font)
            draw.text((30, height + 210), "BC² = 36 + 225 - 180 × 0.5", fill=(0, 0, 0), font=font)
            draw.text((30, height + 250), "BC² = 261 - 90 = 171", fill=(0, 0, 0), font=font)
            draw.text((30, height + 290), "BC = 13.1 cm", fill=(0, 0, 0), font=font)
            
            # Part (b) with serious errors
            draw.text((30, height + 340), "(b) For angle ADB:", fill=(0, 0, 0), font=font)
            draw.text((30, height + 380), "Not sure how to approach this problem.", fill=(0, 0, 0), font=font)
            draw.text((30, height + 420), "The angle might be 30° again because of the original triangle.", fill=(0, 0, 0), font=font)
            draw.text((30, height + 460), "So ADB = 30°", fill=(0, 0, 0), font=font)
    
    # Save the mock answer image to a file
    # Create directory structure if it doesn't exist
    base_dir = os.path.dirname(question_path)
    answer_dir = os.path.join(base_dir, "mock_answers")
    os.makedirs(answer_dir, exist_ok=True)
    
    # Generate filename based on question and level
    q_filename = os.path.basename(question_path)
    answer_filename = f"mock_{level}_{q_filename}"
    answer_path = os.path.join(answer_dir, answer_filename)
    
    # Save the image
    answer_img.save(answer_path)
    print(f"Created mock answer image: {answer_path}")
    
    return answer_path

def create_mock_answer_for_q1():
    """Create a set of mock answers for Question 1 of June 2023 Pure Maths"""
    with app.app_context():
        # Find the question by ID
        question = Question.query.filter_by(id=14).first()  # Question ID from our SQL query
        
        if not question:
            print("Question not found!")
            return
            
        print(f"Creating mock answers for Question {question.question_number} of Paper ID {question.paper_id}")
        
        # Create mock answers with different quality levels
        levels = ["excellent", "good", "average", "needs_improvement"]
        
        for level in levels:
            # Create the mock answer image
            answer_image_path = create_mock_answer_image(question.image_path, level)
            
            if not answer_image_path:
                print(f"Failed to create mock answer image for level: {level}")
                continue
                
            # Create feedback text based on the level
            if level == "excellent":
                feedback = """
# Excellent Work! 

## Part (a) - Score: 2/2
Your application of the cosine rule is perfect. You've correctly set up the equation, substituted the values accurately, and calculated the final answer to an appropriate level of precision (3 significant figures). Your working is clear, systematic, and easy to follow.

## Part (b) - Score: 3/3
You've demonstrated excellent understanding by:
1. Correctly identifying that two solutions exist for this problem
2. Setting up the sine rule appropriately for triangle ABD
3. Performing accurate calculations to find both possible values (48.6° and 131.4°)
4. Presenting your final answer with the correct precision

Overall, this is a model answer that shows complete mastery of the trigonometric techniques required for solving triangles. Well done!

**Total Score: 5/5**
"""
                score = 5
                max_score = 5
                
            elif level == "good":
                feedback = """
# Good Work!

## Part (a) - Score: 2/2
Your application of the cosine rule is correct, and your calculations are accurate. Your work is well organized, showing all the steps clearly.

## Part (b) - Score: 2/3
You've correctly:
- Set up the sine rule for triangle ABD
- Calculated sin(ADB) = 0.75
- Found one possible value for angle ADB (48.6°)

However, when finding angles using the inverse sine function, you need to consider both possible solutions:
- ADB = arcsin(0.75) = 48.6°
- ADB = 180° - 48.6° = 131.4°

Remember that sin(θ) = sin(180°-θ), so we get two possible angles.

**Total Score: 4/5**
"""
                score = 4
                max_score = 5
                
            elif level == "average":
                feedback = """
# Satisfactory Work

## Part (a) - Score: 1.5/2
You've used the correct approach with the cosine rule, but there are some inconsistencies in your calculations:
- In one step you wrote BC² = 261 - 180cos(30°), which doesn't match your previous line
- Your final answer of 10.3 cm is slightly inaccurate (the correct answer is 10.3 cm to 1 decimal place, but 10.25 cm to 3 significant figures)

## Part (b) - Score: 1/3
Issues in your solution:
- The sine rule application is correct, but your formula has been written inconsistently
- You've found only one value for angle ADB (48.6°)
- You've missed the second possible solution (131.4°)

Remember when using inverse sine, there are generally two possible angles that give the same sine value.

**Total Score: 2.5/5**
"""
                score = 2
                max_score = 5
                
            else:  # needs_improvement
                feedback = """
# Areas to Improve

## Part (a) - Score: 0.5/2
You've identified that the cosine rule is needed, which is good. However, there are several issues:
- You've incorrectly written cos(C) instead of cos(BAC)
- You used cos(30°) = 0.5 which is incorrect (cos(30°) ≈ 0.866)
- This led to a significantly incorrect final answer of 13.1 cm (correct answer is approximately 10.25 cm)

## Part (b) - Score: 0/3
Your approach shows fundamental misconceptions:
- There's no attempt to use an appropriate trigonometric rule (sine rule is needed here)
- The assumption that angle ADB = 30° is incorrect and not supported by any calculations
- No working is shown to justify your answer

I recommend reviewing the sine rule for triangles and how to find angles when given side lengths.

**Total Score: 0.5/5**
"""
                score = 0
                max_score = 5
            
            # Create the mock student answer in the database
            mock_answer = MockStudentAnswer(
                question_id=question.id,
                answer_image_path=answer_image_path,
                feedback=feedback,
                score=score,
                max_score=max_score,
                level=level,
                display_order={'excellent': 1, 'good': 2, 'average': 3, 'needs_improvement': 4}[level]
            )
            
            db.session.add(mock_answer)
        
        # Commit all changes to the database
        db.session.commit()
        print("Successfully created mock answers for Question 1")

if __name__ == "__main__":
    create_mock_answer_for_q1()