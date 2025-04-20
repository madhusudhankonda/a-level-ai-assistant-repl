import os
import json
import time
import logging
import requests  # For HTTP operations
import re  # For regex pattern matching
from openai import OpenAI
import base64

# Get your API key from the environment variable
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Check and log API key status
if OPENAI_API_KEY:
    logger = logging.getLogger(__name__)
    logger.info(f"OpenAI API key is configured (length: {len(OPENAI_API_KEY)})")
else:
    logger = logging.getLogger(__name__)
    logger.error("OpenAI API key is missing or empty!")

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
    Test the OpenAI connection with a simple API check
    
    Returns:
        tuple: (success boolean, message string)
    """
    try:
        logger.info("Testing OpenAI connection")
        
        # First try with models endpoint which is much lighter than a full completion
        if not OPENAI_API_KEY:
            logger.error("Missing OpenAI API key")
            return False, "OpenAI API key is missing. Please configure the API key."
            
        # Simply verify API key is valid by checking the models endpoint
        try:
            # List models to verify API key is valid
            openai.models.list()
            logger.info("OpenAI test successful using models list endpoint")
            return True, "OpenAI connection successful"
        except Exception as models_error:
            # Fall back to a simple completion with gpt-3.5-turbo if models list fails
            error_message = str(models_error)
            logger.warning(f"Models list check failed: {error_message}, trying simpler model")
            
            try:
                # Simple text completion with a smaller model for basic testing
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",  # Use a simpler model for testing
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": "Say hello world!"}
                    ],
                    max_tokens=5
                )
                
                # Extract the response
                message = response.choices[0].message.content
                logger.info(f"OpenAI test successful with fallback model. Response: {message}")
                
                return True, "OpenAI connection successful"
            except Exception as completion_error:
                # Both methods failed
                logger.error(f"OpenAI completion test also failed: {completion_error}")
                return False, f"OpenAI connection failed: {str(completion_error)}"
        
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
4. Score the answer on a scale of 1-5 stars

Format your response with these clearly labeled sections:

## Feedback
Provide detailed feedback on the student's answer with specific points on what was done well and what needs improvement. Be encouraging but honest.

## Explanation
Provide a complete, correct solution to the question with all steps clearly shown. Use proper LaTeX notation for mathematical expressions ($...$ for inline, $$....$$ for display).

## Tips
Give 2-3 specific tips for how the student can improve their answer or approach to similar problems in the future.

## Score
Rate the answer from 1-5 stars based on:
- Correctness (understanding and applying the right concepts)
- Completeness (answering all parts of the question)
- Method (showing appropriate working and steps)
- Clarity (clear presentation and explanation)

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
        
        # Make the API call to OpenAI without requiring JSON format
        response = openai.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model, released May 13, 2024
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content}
            ],
            max_tokens=1500
        )
        
        # Get the text response without JSON parsing
        response_text = response.choices[0].message.content
        logger.info(f"Received feedback response: {response_text[:100]}...")
        
        # Extract the different sections from the markdown-formatted text
        sections = {
            'feedback': '',
            'explanation': '',
            'tips': '',
            'score': '3/5 Stars'  # Default score
        }
        
        # Simple text parsing by section headers
        current_section = None
        section_content = []
        
        for line in response_text.split('\n'):
            if line.startswith('## Feedback'):
                current_section = 'feedback'
                section_content = []
            elif line.startswith('## Explanation'):
                if current_section:
                    sections[current_section] = '\n'.join(section_content).strip()
                current_section = 'explanation'
                section_content = []
            elif line.startswith('## Tips'):
                if current_section:
                    sections[current_section] = '\n'.join(section_content).strip()
                current_section = 'tips'
                section_content = []
            elif line.startswith('## Score'):
                if current_section:
                    sections[current_section] = '\n'.join(section_content).strip()
                current_section = 'score'
                section_content = []
            elif current_section:
                section_content.append(line)
                
                # Look for a score pattern in the score section
                if current_section == 'score' and ('/' in line or 'stars' in line.lower() or 'star' in line.lower()):
                    # Try to extract X/5 pattern
                    score_match = re.search(r'(\d+)/(\d+)', line)
                    if score_match:
                        sections['score'] = f"{score_match.group(1)}/5 Stars"
        
        # Add the last section
        if current_section:
            sections[current_section] = '\n'.join(section_content).strip()
            
        return sections
        
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
    
    # Simple prompt without requiring JSON to avoid parsing issues
    system_prompt = f"""
You are an expert A-Level {subject.capitalize()} tutor. Analyze the question in the image and provide a detailed explanation.
Use proper LaTeX notation for mathematical formulas ($...$ for inline, $$...$$ for display).
Provide a step-by-step solution with clear explanations for each step.

Format your response with:
1. A brief title or description of the question
2. A detailed step-by-step explanation with clear reasoning
3. A summary of 3-5 key concepts or formulas used in the solution

Use clear headings (e.g., "## Step 1:") and numbered steps where appropriate.
Your explanation should be comprehensive, explaining both the mathematical concepts and their application.
"""

    try:
        logger.info(f"Processing image for {subject} explanation")
        
        # Clean the base64 string if it has a data URI prefix
        if isinstance(base64_image, str) and 'base64' in base64_image and ',' in base64_image:
            logger.info("Removing data URI prefix from image")
            image_parts = base64_image.split(',')
            if len(image_parts) > 1:
                base64_image = image_parts[1]
            else:
                logger.warning("Data URI format detected but couldn't extract base64 part")
        
        # Validate the base64 string
        if not base64_image or not isinstance(base64_image, str):
            raise ValueError("Invalid base64 image data")
        
        # Prepare the image URL
        image_url = f"data:image/jpeg;base64,{base64_image}"
        logger.info(f"Image prepared, length: {len(base64_image)}")
        
        # API call without requiring JSON response format
        logger.info("Calling OpenAI API for explanation")
        try:
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
                timeout=90.0  # Increase timeout for longer processing
            )
            
            # Get the text response directly - no JSON parsing needed anymore
            explanation = response.choices[0].message.content
            logger.info(f"Received explanation: {explanation[:100]}...")
            
            return explanation
        except Exception as api_error:
            logger.error(f"OpenAI API call failed: {api_error}")
            # Provide a more detailed error message
            error_str = str(api_error).lower()
            if "API key" in error_str:
                raise Exception("OpenAI API key issue. Please check your API key configuration.")
            elif "timeout" in error_str:
                raise Exception("The request timed out. The question might be too complex or the server is busy. Please try again.")
            elif "rate limit" in error_str:
                raise Exception("OpenAI rate limit reached. Please try again in a few moments.")
            elif "quota" in error_str or "exceeded" in error_str or "insufficient_quota" in error_str or "429" in error_str:
                raise Exception("The AI service is temporarily unavailable due to exceeding usage limits. The administrator has been notified. Please try again later.")
            else:
                raise Exception(f"OpenAI API error: {str(api_error)}")
        
    except Exception as e:
        logger.error(f"Error generating explanation: {e}")
        if "OpenAI API error" in str(e):
            # Pass through already formatted OpenAI errors
            raise e
        else:
            # Format other errors
            raise Exception(f"Error processing request: {str(e)}")
