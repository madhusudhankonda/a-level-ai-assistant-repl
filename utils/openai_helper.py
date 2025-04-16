import os
import json
import time
import logging
import requests  # For HTTP operations
from openai import OpenAI
import base64

# Get your API key from the environment variable
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Configure OpenAI client with additional timeout parameters
openai = OpenAI(
    api_key=OPENAI_API_KEY,
    timeout=60.0,  # Longer timeout
    max_retries=3  # More retries
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_openai_connection():
    """
    Test the OpenAI connection with a simple text prompt
    
    Returns:
        tuple: (success boolean, message string)
    """
    try:
        logger.info("Testing OpenAI connection with simple text prompt")
        
        # Simple text completion to test the connection
        response = openai.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello world!"}
            ],
            max_tokens=10
        )
        
        # Extract the response
        message = response.choices[0].message.content
        logger.info(f"OpenAI test successful. Response: {message}")
        
        return True, "OpenAI connection successful"
        
    except Exception as e:
        error_message = str(e)
        logger.error(f"OpenAI test failed: {error_message}")
        return False, f"OpenAI connection failed: {error_message}"

def generate_answer_feedback(question_image, answer_image, subject):
    """
    Generate feedback for a student's answer to a question using OpenAI's GPT-4o
    
    Args:
        question_image: Data URI of the question image
        answer_image: Data URI of the student's answer image
        subject: Subject of the question (e.g., "Mathematics", "Physics")
    
    Returns:
        Dictionary containing feedback, explanation, tips, and score
    """
    subject = subject.lower().strip()
    
    # Create a system prompt for analyzing student answers
    system_prompt = f"""
You are an expert A-Level {subject.capitalize()} tutor who evaluates student answers.
Analyze both the question image and the student's handwritten answer image provided.

Your task is to:
1. Understand the question and what it's asking for
2. Evaluate the student's answer for correctness, completeness, and approach
3. Provide constructive feedback
4. Score the answer on a scale of 1-5 stars based on:
   - Correctness (understanding and applying the right concepts)
   - Completeness (answering all parts of the question)
   - Method (showing appropriate working and steps)
   - Clarity (clear presentation and explanation)

Return your response in this JSON format:
{{
    "feedback": "Your detailed feedback on the student's answer with specific points on what was done well and what needs improvement. Be encouraging but honest.",
    "explanation": "A complete, correct solution to the question with all steps clearly shown. Use proper LaTeX notation for mathematical expressions ($...$ for inline, $$....$$ for display).",
    "tips": "2-3 specific tips for how the student can improve their answer or approach to similar problems in the future.",
    "score": "X/5" // Rating from 1-5 stars
}}

Always use proper LaTeX notation for mathematical expressions, formulas and equations.
Be encouraging and constructive in your feedback.
"""

    try:
        logger.info(f"Processing student answer for {subject} feedback")
        
        # Validate the images
        if not question_image or not answer_image:
            raise ValueError("Both question and answer images are required")
        
        # Create the content array with both images
        content = [
            {"type": "text", "text": f"Please analyze this {subject} question and the student's handwritten answer:"},
            {"type": "text", "text": "QUESTION IMAGE:"},
            {"type": "image_url", "image_url": {"url": question_image}},
            {"type": "text", "text": "STUDENT'S ANSWER:"},
            {"type": "image_url", "image_url": {"url": answer_image}}
        ]
        
        logger.info("Calling OpenAI API with both images")
        
        # Make the API call to OpenAI with JSON response format
        response = openai.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model, released May 13, 2024
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content}
            ],
            max_tokens=1500,
            response_format={"type": "json_object"}
        )
        
        # Parse the JSON response
        feedback_data = json.loads(response.choices[0].message.content)
        
        # Add the score in a standardized format
        score = feedback_data.get('score', '0/5')
        if isinstance(score, str) and '/' in score:
            score_parts = score.split('/')
            if len(score_parts) == 2 and score_parts[0].isdigit():
                # Format as "X/5 Stars"
                feedback_data['score'] = f"{score_parts[0]}/5 Stars"
        
        return feedback_data
        
    except Exception as e:
        logger.error(f"Error generating answer feedback: {e}")
        raise Exception(f"OpenAI API error: {str(e)}")

def generate_explanation(base64_image, subject):
    """
    Generate an explanation for a question using OpenAI's GPT-4o
    
    Args:
        base64_image: Base64-encoded image of the question
        subject: Subject of the question (e.g., "Mathematics", "Physics")
    
    Returns:
        Generated explanation text
    """
    subject = subject.lower().strip()
    
    # Enhanced prompt with structured JSON response format
    system_prompt = f"""
You are an expert A-Level {subject.capitalize()} tutor. Analyze the question in the image and provide a detailed explanation.
Use proper LaTeX notation for mathematical formulas ($...$ for inline, $$...$$ for display).
Provide a step-by-step solution with clear explanations for each step.

Return your response in this JSON format:
{{
    "title": "Brief description of the question",
    "explanation": "Your detailed step-by-step explanation with clear reasoning",
    "key_points": ["3-5 key concepts or formulas used in the solution"]
}}

Format the explanation with clear headings and numbered steps where appropriate.
"""

    try:
        logger.info(f"Processing image for {subject} explanation")
        
        # Clean the base64 string if it has a data URI prefix
        if isinstance(base64_image, str) and 'base64' in base64_image and ',' in base64_image:
            logger.info("Removing data URI prefix from image")
            base64_image = base64_image.split(',')[1]
        
        # Validate the base64 string
        if not base64_image or not isinstance(base64_image, str):
            raise ValueError("Invalid base64 image data")
            
        # Prepare the image URL
        image_url = f"data:image/jpeg;base64,{base64_image}"
        logger.info(f"Image prepared, length: {len(base64_image)}")
        
        # API call with JSON response format
        logger.info("Calling OpenAI API with JSON response format")
        response = openai.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model, released May 13, 2024
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": [
                    {"type": "text", "text": f"Please explain this {subject} question:"},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]}
            ],
            max_tokens=1500,
            response_format={"type": "json_object"}
        )
        
        # Parse the JSON response
        response_content = response.choices[0].message.content
        logger.info(f"Received JSON response: {response_content[:100]}...")
        
        try:
            explanation_data = json.loads(response_content)
            # For backward compatibility with existing UI, convert the JSON structure to formatted text
            explanation = f"# {explanation_data.get('title', 'Explanation')}\n\n{explanation_data.get('explanation', '')}"
            
            # Add key points if available
            key_points = explanation_data.get('key_points', [])
            if key_points:
                explanation += "\n\n## Key Points:\n"
                for i, point in enumerate(key_points):
                    explanation += f"\n{i+1}. {point}"
        except json.JSONDecodeError as e:
            # Fall back to raw text if JSON parsing fails
            logger.error(f"Failed to parse JSON response: {e}")
            explanation = response_content
        
        return explanation
        
    except Exception as e:
        logger.error(f"Error generating explanation: {e}")
        raise Exception(f"OpenAI API error: {str(e)}")
