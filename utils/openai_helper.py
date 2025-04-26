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

def check_openai_key():
    """
    Check if OpenAI API key is configured
    
    Returns:
        str: The API key if configured, otherwise None
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logger.error("OpenAI API key is not configured")
        return None
    return api_key

def call_openai_with_retry(model="gpt-4o", messages=None, max_tokens=1000, temperature=0.7, detailed_error=False):
    """
    Call OpenAI API with retry logic for handling rate limits and timeouts
    
    Args:
        model (str): The model to use for the completion
        messages (list): The messages to send to the API
        max_tokens (int): Maximum number of tokens to generate
        temperature (float): Temperature for the completion
        detailed_error (bool): Whether to return detailed error messages
    
    Returns:
        dict: The API response or error details
    """
    if not messages:
        return {"error": "No messages provided"}
    
    # Check API key
    api_key = check_openai_key()
    if not api_key:
        return {"error": "OpenAI API key is not configured"}
    
    # Retry parameters
    max_retries = 3
    retry_count = 0
    backoff_time = 2.0  # Initial backoff time in seconds
    
    while retry_count < max_retries:
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = openai.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            # Convert to dict for consistency
            return response.model_dump()
            
        except Exception as e:
            retry_count += 1
            error_message = str(e).lower()
            error_type = type(e).__name__
            
            # Log the error
            logger.error(f"OpenAI API error ({error_type}): {error_message}")
            
            # Check for retryable errors
            retryable = (
                "rate limit" in error_message or 
                "ratelimit" in error_message or
                "timeout" in error_message or
                "capacity" in error_message or
                "overloaded" in error_message or
                "internal server error" in error_message or
                "503" in error_message or
                "502" in error_message
            )
            
            if retry_count < max_retries and retryable:
                logger.warning(f"Retryable error, attempt {retry_count}/{max_retries}. Retrying in {backoff_time}s...")
                time.sleep(backoff_time)
                backoff_time *= 2  # Exponential backoff
            else:
                # Either non-retryable or max retries exceeded
                if retry_count >= max_retries:
                    logger.error(f"Maximum retries ({max_retries}) exceeded")
                else:
                    logger.error(f"Non-retryable error")
                
                if detailed_error:
                    return {
                        "error": f"OpenAI API error: {error_message}",
                        "error_type": error_type,
                        "retryable": retryable,
                        "attempts": retry_count
                    }
                else:
                    return {"error": "Failed to generate response from OpenAI API"}
    
    # Should not reach here, but just in case
    return {"error": "Unknown error in OpenAI API call"}

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

def generate_answer_feedback(question_image, answer_image, subject, combined_image=False):
    """
    Generate feedback for a student's answer to a question using OpenAI's GPT-4o model
    
    Args:
        question_image: Data URI of the question image (or combined image with both question and answer)
        answer_image: Data URI of the student's answer image (None if combined_image=True)
        subject: Subject of the question (e.g., "Mathematics", "Physics")
        combined_image: Boolean indicating if question_image contains both question and answer
    
    Returns:
        Dictionary containing feedback, explanation, tips, and score
    """
    subject = subject.lower().strip()
    logger.info(f"Generating answer feedback for {subject} {'from combined image' if combined_image else 'from separate images'}")
    
    # Create a system prompt for analyzing student answers
    base_prompt = f"""
You are an expert A-Level {subject.capitalize()} tutor who evaluates student answers.
"""

    # Add specific instructions based on whether we're using a combined image or separate images
    if combined_image:
        system_prompt = base_prompt + f"""
The uploaded image contains BOTH the question and the student's handwritten answer.
Carefully analyze the image - typically the question will be at the top and the student's answer below it.

Your task is to:
1. First identify and understand the question portion of the image
2. Then identify and evaluate the student's handwritten answer portion
3. Provide constructive feedback on the student's work
4. Score the answer on a scale of 1-5 stars

Be very careful to distinguish between the printed question and the student's handwritten answer.
"""
    else:
        system_prompt = base_prompt + f"""
Analyze both the question image and the student's handwritten answer image provided.

Your task is to:
1. Understand the question from the first image
2. Evaluate the student's answer (from the second image) for correctness, completeness, and approach
3. Provide constructive feedback
4. Score the answer on a scale of 1-5 stars
"""

    # The rest of the prompt is the same for both cases
    system_prompt += f"""
Format your response with these clearly labeled sections:

## Feedback
Act as a real A-Level mathematics teacher marking the paper. Evaluate how the student performed, focusing on their working rather than just the final answer.

Your feedback must include:
- Clear mark allocation: "You received X/Y marks" with specific breakdown
- Direct references to the student's work: "In your solution to part (b), you correctly..."
- Specific explanations of lost marks: "You lost a mark in part (c) because..."
- Explicit identification of what was needed for full marks: "To achieve full marks, you needed to..."
- Identification of method marks vs. accuracy marks following A-Level marking schemes

Remember that students need to know exactly where they lost marks and what they should have done differently.

## Explanation
Provide a complete, correct solution to the question with all steps clearly shown. Use proper LaTeX notation for mathematical expressions ($...$ for inline, $$....$$ for display).

## Tips
Give 2-3 specific tips for how the student can improve their answer or approach to similar problems in the future. Each tip should directly address a weakness in their answer.

## Score
Rate the answer as X/Y marks where Y is the maximum available marks (typically 5-10 for this system). Include a specific breakdown of:
- Method marks earned vs. available
- Accuracy marks earned vs. available
- Communication marks if applicable

Always use proper LaTeX notation for mathematical expressions, formulas and equations.
Be encouraging but realistic in your feedback, just like a real teacher would mark an A-Level paper.
"""

    try:
        logger.info(f"Processing student answer for {subject} feedback")
        
        # Prepare content array based on whether we have a combined image or separate images
        if combined_image:
            # For combined image mode, we only need to validate question_image
            if not question_image:
                raise ValueError("Question image (combined with answer) is required")
                
            # Create content array with just the combined image
            content = [
                {"type": "text", "text": f"Please analyze this {subject} question and the student's handwritten answer in this single image:"},
                {"type": "image_url", "image_url": {"url": question_image}}
            ]
            
            logger.info("Calling OpenAI API with combined question and answer image")
        else:
            # For separate images mode, validate both images
            if not question_image or not answer_image:
                raise ValueError("Both question and answer images are required for separate image mode")
            
            # Create content array with both images
            content = [
                {"type": "text", "text": f"Please analyze this {subject} question and the student's handwritten answer:"},
                {"type": "text", "text": "QUESTION IMAGE:"},
                {"type": "image_url", "image_url": {"url": question_image}},
                {"type": "text", "text": "STUDENT'S ANSWER:"},
                {"type": "image_url", "image_url": {"url": answer_image}}
            ]
            
            logger.info("Calling OpenAI API with separate question and answer images")
        
        # Make the API call to OpenAI with retry logic for rate limiting and timeouts
        max_retries = 3
        retry_count = 0
        backoff_time = 2.0  # Initial backoff time in seconds
        response = None
        
        while retry_count < max_retries:
            try:
                # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
                # do not change this unless explicitly requested by the user
                response = openai.chat.completions.create(
                    model="gpt-4o",  # Using the latest GPT-4o model which supports vision
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": content}
                    ],
                    max_tokens=1500,
                    temperature=0.3  # Lower temperature for more consistent responses
                )
                # If we reach here, the request was successful
                break
                
            except Exception as retry_error:
                retry_count += 1
                error_message = str(retry_error).lower()
                
                # Only retry on certain error types
                if (retry_count < max_retries and 
                    ("rate limit" in error_message or 
                     "ratelimit" in error_message or
                     "timeout" in error_message or
                     "capacity" in error_message or
                     "overloaded" in error_message)):
                    
                    logger.warning(f"OpenAI API request failed (attempt {retry_count}/{max_retries}): {error_message}")
                    logger.info(f"Retrying in {backoff_time} seconds...")
                    time.sleep(backoff_time)
                    backoff_time *= 2  # Exponential backoff
                    continue
                else:
                    # Either we've reached max retries or this is not a retryable error
                    if retry_count >= max_retries:
                        logger.error(f"Maximum retries ({max_retries}) exceeded: {error_message}")
                    else:
                        logger.error(f"Non-retryable error: {error_message}")
                    raise  # Re-raise the last exception
        
        # Check if we got a response
        if not response:
            raise Exception("Failed to get a response from OpenAI after multiple attempts")
        
        # Get the text response without JSON parsing
        response_text = response.choices[0].message.content
        logger.info(f"Received feedback response: {response_text[:100]}...")
        
        # Extract the different sections from the markdown-formatted text
        sections = {
            'feedback': '',
            'explanation': '',
            'tips': '',
            'score': '3/5 Marks'  # Default score using mark-based grading
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
                if current_section == 'score' and ('/' in line or 'mark' in line.lower() or 'marks' in line.lower()):
                    # Try to extract X/Y pattern
                    score_match = re.search(r'(\d+)/(\d+)', line)
                    if score_match:
                        # Display as marks rather than stars to be more like a teacher's marking
                        sections['score'] = f"{score_match.group(1)}/{score_match.group(2)} Marks"
        
        # Add the last section
        if current_section:
            sections[current_section] = '\n'.join(section_content).strip()
            
        return sections
        
    except Exception as e:
        logger.error(f"Error generating answer feedback: {e}")
        raise Exception(f"OpenAI API error: {str(e)}")

def generate_explanation(base64_image, subject):
    """
    Generate an explanation for a question using OpenAI's GPT-4o model
    
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
        
        # Simplified handling of different input formats with better logging
        if not isinstance(base64_image, str):
            logger.error(f"Invalid image data type: {type(base64_image)}")
            raise ValueError(f"Invalid image data type: {type(base64_image)}")
            
        logger.info(f"Image data length: {len(base64_image)} characters")
        
        # Extract the base64 part from data URI if needed
        if base64_image.startswith('data:image/'):
            logger.info("Input has data URI format, extracting base64 portion")
            try:
                # Extract base64 part after the "base64," marker
                image_parts = base64_image.split('base64,')
                if len(image_parts) < 2:
                    raise ValueError("Invalid data URI format: missing base64 data")
                
                # The second part is the actual base64 data
                clean_base64 = image_parts[1]
                logger.info(f"Successfully extracted base64 data: {len(clean_base64)} characters")
                
                # Reconstruct the data URI with the extracted part (in case there were format issues)
                image_url = f"data:image/jpeg;base64,{clean_base64}"
            except Exception as extract_error:
                logger.error(f"Failed to extract base64 from data URI: {extract_error}")
                raise ValueError(f"Invalid data URI format: {extract_error}")
        else:
            # Check if it's already a clean base64 string (no data URI prefix)
            logger.info("Checking if input is a clean base64 string")
            try:
                # Validate it's decodable as base64 (just a sample)
                test_decode = base64.b64decode(base64_image[:100] + "=" * ((4 - len(base64_image[:100]) % 4) % 4))
                logger.info("Input appears to be clean base64 data")
                image_url = f"data:image/jpeg;base64,{base64_image}"
            except Exception as decode_error:
                logger.error(f"Input is not valid base64 data: {decode_error}")
                # Last attempt - maybe it has base64, but not at the beginning
                if 'base64,' in base64_image:
                    try:
                        image_parts = base64_image.split('base64,')
                        clean_base64 = image_parts[1]
                        image_url = f"data:image/jpeg;base64,{clean_base64}"
                        logger.info(f"Recovered base64 data from non-standard format: {len(clean_base64)} characters")
                    except Exception as recovery_error:
                        logger.error(f"Failed to recover base64 data: {recovery_error}")
                        raise ValueError("Unable to process the provided image data")
                else:
                    raise ValueError("Image data is not in a recognizable format")
        
        # Final validation check on the prepared URL
        if not image_url or len(image_url) < 100:
            logger.error(f"Final image URL is too short: {len(image_url) if image_url else 0} characters")
            raise ValueError("Processed image data is too short or empty")
            
        logger.info(f"Final image URL prepared, total length: {len(image_url)} characters")
        
        # API call with explicit error handling and logging
        logger.info(f"Calling OpenAI API (GPT-4o) for explanation")
        try:
            # Implement an exponential backoff retry mechanism for rate limits and timeouts
            max_retries = 3
            retry_count = 0
            backoff_time = 2.0  # Initial backoff time in seconds
            
            while retry_count < max_retries:
                try:
                    # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
                    # do not change this unless explicitly requested by the user
                    response = openai.chat.completions.create(
                        model="gpt-4o",  # Using the latest GPT-4o model which supports vision
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": [
                                {"type": "text", "text": f"Please explain this {subject} question in detail:"},
                                {"type": "image_url", "image_url": {"url": image_url}}
                            ]}
                        ],
                        max_tokens=1500,
                        temperature=0.3,  # Lower temperature for more focused responses
                        timeout=90.0  # Increase timeout for longer processing
                    )
                    # If we get here, the request was successful
                    break
                    
                except Exception as retry_error:
                    retry_count += 1
                    error_message = str(retry_error).lower()
                    
                    # Only retry on rate limit or timeout errors
                    if (retry_count < max_retries and 
                        ("rate limit" in error_message or 
                         "ratelimit" in error_message or
                         "timeout" in error_message or
                         "capacity" in error_message or
                         "overloaded" in error_message)):
                        
                        logger.warning(f"OpenAI API request failed (attempt {retry_count}/{max_retries}): {error_message}")
                        logger.info(f"Retrying in {backoff_time} seconds...")
                        time.sleep(backoff_time)
                        backoff_time *= 2  # Exponential backoff
                        continue
                    else:
                        # Either we've reached max retries or this is not a retryable error
                        if retry_count >= max_retries:
                            logger.error(f"Maximum retries ({max_retries}) exceeded: {error_message}")
                        else:
                            logger.error(f"Non-retryable error: {error_message}")
                        raise  # Re-raise the last exception
            
            # Process the response
            explanation = response.choices[0].message.content
            if not explanation or len(explanation) < 10:
                logger.error(f"Received empty or very short explanation from OpenAI: '{explanation}'")
                raise Exception("The AI returned an empty or insufficient response. Please try again.")
                
            logger.info(f"Received explanation of length {len(explanation)} characters")
            logger.info(f"Explanation preview: {explanation[:100]}...")
            
            return explanation
            
        except Exception as api_error:
            logger.error(f"OpenAI API call failed: {api_error}")
            error_str = str(api_error).lower()
            
            # Provide specific error messages based on different error patterns
            if "api key" in error_str:
                logger.error("API key authentication issue detected")
                raise Exception("OpenAI API key issue. Please check your API key configuration.")
            elif "timeout" in error_str:
                logger.error("Request timeout detected")
                raise Exception("The request timed out. The question might be too complex or the server is busy. Please try again.")
            elif "rate limit" in error_str or "ratelimit" in error_str:
                logger.error("Rate limit error detected")
                raise Exception("OpenAI rate limit reached. Please try again in a few moments.")
            elif any(term in error_str for term in ["quota", "exceeded", "insufficient_quota", "429"]):
                logger.error("Quota exceeded error detected")
                raise Exception("The AI service is temporarily unavailable due to exceeding usage limits. The administrator has been notified. Please try again later.")
            elif "invalid" in error_str and ("format" in error_str or "image" in error_str):
                logger.error("Invalid image format error detected")
                raise Exception("The image format is invalid or corrupted. Please try with a different image.")
            else:
                logger.error(f"Unspecified OpenAI API error: {api_error}")
                raise Exception(f"OpenAI API error: {str(api_error)}")
        
    except Exception as e:
        logger.error(f"Error generating explanation: {e}")
        if "OpenAI API error" in str(e) or "API key" in str(e) or "timed out" in str(e):
            # Pass through already formatted OpenAI errors
            raise e
        else:
            # Format other errors
            raise Exception(f"Error processing request: {str(e)}")
