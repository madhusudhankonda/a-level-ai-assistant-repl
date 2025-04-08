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
    
    # Simplified prompt to reduce complexity and potential issues
    system_prompt = f"""
You are an expert A-Level {subject.capitalize()} tutor. Analyze the question in the image and provide a detailed explanation.
Use proper LaTeX notation for mathematical formulas ($...$ for inline, $$...$$ for display).
Provide a step-by-step solution with clear explanations for each step.
Format your response with clear headings and numbered steps.
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
        
        # Simplified API call with fewer parameters and options
        logger.info("Calling OpenAI API")
        response = openai.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model, released May 13, 2024
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": [
                    {"type": "text", "text": f"Please explain this {subject} question:"},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]}
            ],
            max_tokens=1000
        )
        
        # Extract the explanation from the response
        explanation = response.choices[0].message.content
        
        return explanation
        
    except Exception as e:
        logger.error(f"Error generating explanation: {e}")
        raise Exception(f"OpenAI API error: {str(e)}")
