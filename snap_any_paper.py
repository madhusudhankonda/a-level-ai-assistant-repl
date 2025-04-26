"""
Module for handling "Snap Any Paper" functionality, which allows users to
upload or capture photos of any A-Level question for AI analysis.
"""
import os
import base64
import json
import logging
import re
from datetime import datetime
from io import BytesIO
from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from PIL import Image
from models import db, UserQuery, User
from utils.openai_helper import check_openai_key, call_openai_with_retry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Blueprint
snap_paper_bp = Blueprint('snap_paper', __name__)

# Constants
REQUIRED_CREDITS = 10
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_IMAGE_SIZE = 4 * 1024 * 1024  # 4MB
TEMP_FOLDER = 'temp_uploads'

# Ensure temp folder exists
if not os.path.exists(TEMP_FOLDER):
    os.makedirs(TEMP_FOLDER)

def allowed_file(filename):
    """Check if uploaded file has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_temp_image(image_data):
    """Save image data to temporary file and return the path"""
    try:
        logger.info("="*50)
        logger.info("SAVE TEMP IMAGE FUNCTION DEBUGGING")
        logger.info("="*50)
        logger.info(f"Image data type: {type(image_data)}")
        logger.info(f"Image data length: {len(image_data) if image_data else 0}")
        
        if not image_data:
            logger.error("Image data is empty or None")
            return None
            
        # Log the first 100 chars to see what we're dealing with
        sample = image_data[:100] if isinstance(image_data, str) else "Non-string data"
        logger.info(f"First 100 chars of image_data: {sample}")
        
        # Check if it's a data URL
        if isinstance(image_data, str) and image_data.startswith('data:image'):
            logger.info("Detected data URL format, processing as base64")
            # Extract the base64 part
            image_data = re.sub('^data:image/.+;base64,', '', image_data)
            try:
                image_data = base64.b64decode(image_data)
                logger.info(f"Successfully decoded base64 data, length: {len(image_data)}")
            except Exception as b64_error:
                logger.error(f"Base64 decoding error: {str(b64_error)}")
                return None
                
            try:
                img = Image.open(BytesIO(image_data))
                logger.info(f"Successfully opened image from bytes, format: {img.format}, size: {img.size}")
            except Exception as img_error:
                logger.error(f"Error opening image from bytes: {str(img_error)}")
                return None
        else:
            # Handle direct binary data
            logger.info("Not a data URL, treating as direct binary image data")
            try:
                if isinstance(image_data, str):
                    logger.warning("Data is string but not a data URL, attempting to convert to bytes")
                    try:
                        # Last resort - try to decode as base64 anyway
                        image_data = base64.b64decode(image_data)
                    except:
                        logger.error("Failed to treat string as base64")
                        return None
                        
                img = Image.open(BytesIO(image_data))
                logger.info(f"Successfully opened image from bytes, format: {img.format}, size: {img.size}")
            except Exception as img_error:
                logger.error(f"Error opening image from binary: {str(img_error)}")
                return None
        
        # Create a unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"snap_any_paper_{timestamp}.jpg"
        file_path = os.path.join(TEMP_FOLDER, filename)
        logger.info(f"Created temp file path: {file_path}")
        
        # Save the image
        try:
            img.save(file_path, "JPEG")
            logger.info(f"Successfully saved image to {file_path}")
            return file_path
        except Exception as save_error:
            logger.error(f"Error saving image to file: {str(save_error)}")
            return None
    except Exception as e:
        logger.error(f"Error in save_temp_image: {str(e)}")
        logger.exception("Detailed traceback:")
        return None

def process_image_with_openai(image_path, analysis_type, subject):
    """Process image with OpenAI's vision model"""
    try:
        # Check if OpenAI key is configured
        api_key = check_openai_key()
        if not api_key:
            return {
                "success": False,
                "error": "OpenAI API key is not configured. Please contact support."
            }
        
        # Prepare the image for API request
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Set system prompt based on subject and analysis type
        if analysis_type == "question_only":
            system_prompt = f"""You are an expert A-Level {subject} tutor.
            Analyze the uploaded image which contains an A-Level {subject} question.
            Clearly identify what the question is asking, explain key concepts involved,
            and provide a detailed step-by-step solution.
            
            If the image contains handwritten work alongside the question,
            focus on explaining the question itself rather than evaluating the work.
            
            Format your response with clear section headings and use mathematical notation
            where appropriate, using LaTeX format with $ delimiters for inline math 
            and $$ delimiters for display math.
            """
        else:  # answer_feedback
            system_prompt = f"""You are an expert A-Level {subject} tutor.
            Analyze the uploaded image which contains both an A-Level {subject} question 
            and a student's handwritten solution attempt.
            
            1. Identify the question being asked
            2. Evaluate the student's work, noting what they did correctly and where they made mistakes
            3. Provide the correct solution with clear explanations
            4. Offer specific advice to help the student improve
            
            Format your response with clear section headings and use mathematical notation
            where appropriate, using LaTeX format with $ delimiters for inline math 
            and $$ delimiters for display math.
            """
        
        # Build the API request
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": [
                {"type": "text", "text": f"Please analyze this A-Level {subject} question and provide detailed help."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]}
        ]
        
        # Make the API call with retry logic
        response = call_openai_with_retry(
            model="gpt-4o",  # Use GPT-4o for vision capabilities
            messages=messages,
            max_tokens=1500,  # Adjust token limit as needed
            temperature=0.0,  # Lower temperature for more factual responses
            detailed_error=True
        )
        
        if not response or "error" in response:
            return {
                "success": False,
                "error": response.get("error", "Failed to analyze image with AI service.")
            }
        
        # Extract and format content from response
        if response is None:
            content = "No response received from AI service."
        elif isinstance(response, dict):
            # Handle dictionary response
            choices = response.get("choices", [])
            if choices and len(choices) > 0:
                if isinstance(choices[0], dict):
                    message = choices[0].get("message", {})
                    if isinstance(message, dict):
                        content = message.get("content", "")
                    else:
                        content = str(message)
                else:
                    content = str(choices[0])
            else:
                content = "No content in AI response."
        else:
            # Handle if response is not a dictionary (OpenAI response object)
            try:
                content = response.choices[0].message.content
            except (AttributeError, IndexError) as e:
                logger.error(f"Error extracting content: {str(e)}")
                content = "Unable to extract content from response"
        
        # Parse content to identify sections
        # This is a simple implementation; enhance as needed
        title = "Analysis Results"
        analysis = content
        steps = []
        
        # Look for section headings and split content
        section_pattern = r'#{1,3}\s+([^\n]+)'
        sections = re.findall(section_pattern, content)
        if sections:
            title = sections[0]
        
        # Format result
        return {
            "success": True,
            "title": title,
            "analysis": analysis,
            "steps": steps
        }
        
    except Exception as e:
        logger.error(f"Error processing image with OpenAI: {str(e)}")
        return {
            "success": False,
            "error": "Failed to process image. Please try again."
        }

def cleanup_temp_file(file_path):
    """Clean up temporary file"""
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        logger.error(f"Error cleaning up temp file {file_path}: {str(e)}")

def deduct_credits(user_id, credits=REQUIRED_CREDITS):
    """Deduct credits from user's account"""
    try:
        user = User.query.get(user_id)
        if not user:
            return False
        
        if user.credits < credits:
            return False
        
        user.credits -= credits
        db.session.commit()
        return True
    except Exception as e:
        logger.error(f"Error deducting credits: {str(e)}")
        db.session.rollback()
        return False

def log_user_query(user_id, query_type, subject, image_path=None):
    """Log the user query to database"""
    try:
        # Create a new record
        new_query = UserQuery(
            user_id=user_id,
            query_type=query_type,
            subject=subject,
            created_at=datetime.now(),
            credits_used=REQUIRED_CREDITS,
            response_text="Processed with Snap Any Paper feature"
        )
        
        # Add reference to the image if provided
        if image_path:
            new_query.image_path = image_path
        
        db.session.add(new_query)
        db.session.commit()
        return new_query.id
    except Exception as e:
        logger.error(f"Error logging user query: {str(e)}")
        db.session.rollback()
        return None

@snap_paper_bp.route('/snap-any-paper')
@login_required
def snap_any_paper():
    """Render the Snap Any Paper page with template version to bypass cache"""
    import time
    # Add current timestamp to ensure the template is not cached
    return render_template('snap_any_paper_minimal.html', version=int(time.time()))

@snap_paper_bp.route('/basic-test')
@login_required
def basic_test():
    """A super basic test page with minimal JavaScript for debugging"""
    from flask import render_template_string
    
    # Inline HTML template with very basic JavaScript
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Basic Test</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            button { 
                padding: 10px; 
                margin: 5px; 
                background: #4CAF50; 
                color: white; 
                border: none; 
                cursor: pointer; 
            }
            #result { 
                margin-top: 20px; 
                padding: 10px; 
                border: 1px solid #ddd; 
                background: #f9f9f9; 
            }
        </style>
    </head>
    <body>
        <h1>Basic JavaScript Test</h1>
        <p>This is a minimal test page to check if JavaScript is working properly.</p>
        
        <button id="test1">Simple Button Test</button>
        <button id="test2">Alert Test</button>
        <button id="test3">Show Current Time</button>
        
        <div id="result">Results will appear here.</div>
        
        <script>
            // Check if JavaScript is running at all
            document.getElementById('result').textContent = 'JavaScript is running. Page loaded at: ' + new Date().toString();
            
            // Super simple button test
            document.getElementById('test1').onclick = function() {
                document.getElementById('result').textContent = 'Button 1 clicked at: ' + new Date().toString();
            };
            
            // Alert test
            document.getElementById('test2').onclick = function() {
                alert('This is a test alert');
                document.getElementById('result').textContent = 'Alert button clicked at: ' + new Date().toString();
            };
            
            // Show time test
            document.getElementById('test3').onclick = function() {
                document.getElementById('result').textContent = 'Current time: ' + new Date().toString();
            };
        </script>
    </body>
    </html>
    """
    
    return render_template_string(html)

@snap_paper_bp.route('/api/analyze-any-paper', methods=['POST'])
@login_required
def analyze_any_paper():
    """API endpoint to analyze an uploaded paper image"""
    logger.info("="*50)
    logger.info("API ENDPOINT DETAILED DEBUGGING")
    logger.info("="*50)
    logger.info("API endpoint /api/analyze-any-paper called")
    logger.info(f"Request method: {request.method}")
    logger.info(f"Content-Type: {request.headers.get('Content-Type')}")
    logger.info(f"User ID: {current_user.id}, Username: {current_user.username}")
    logger.info(f"All request headers: {dict(request.headers)}")
    logger.info(f"Request args: {request.args}")
    logger.info(f"Request form: {request.form}")
    logger.info(f"Request is JSON: {request.is_json}")
    logger.info(f"Request content length: {request.content_length}")
    
    try:
        # Check if user has enough credits
        logger.info(f"User credits: {current_user.credits}, Required: {REQUIRED_CREDITS}")
        if current_user.credits < REQUIRED_CREDITS:
            logger.warning(f"User {current_user.id} does not have enough credits")
            return jsonify({
                "success": False,
                "error": f"You don't have enough credits. {REQUIRED_CREDITS} credits required."
            }), 400
        
        # Get request data
        data = request.json
        logger.info(f"Request data received: {bool(data)}")
        if not data:
            logger.error("No JSON data provided in request")
            return jsonify({
                "success": False,
                "error": "No data provided."
            }), 400
        
        # Log the keys in the request data for debugging
        logger.info(f"Request data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dictionary'}")
        
        image_data = data.get('image')
        analysis_type = data.get('analysis_type', 'question_only')
        subject = data.get('subject', 'mathematics')
        
        # More detailed logging
        logger.info(f"Analysis type: {analysis_type}, Subject: {subject}")
        logger.info(f"Image data present: {bool(image_data)}")
        logger.info(f"Image data length: {len(image_data) if image_data else 0}")
        logger.info(f"Image data type: {type(image_data).__name__}")
        
        if not image_data:
            logger.error("No image data provided in request")
            return jsonify({
                "success": False,
                "error": "No image provided."
            }), 400
        
        # Save temporary image
        temp_file_path = save_temp_image(image_data)
        if not temp_file_path:
            return jsonify({
                "success": False,
                "error": "Failed to process the image. Please try again."
            }), 400
        
        # Process image with OpenAI
        result = process_image_with_openai(temp_file_path, analysis_type, subject)
        
        # Cleanup temp file
        cleanup_temp_file(temp_file_path)
        
        if not result["success"]:
            return jsonify(result), 400
        
        # Deduct credits and log query
        if not deduct_credits(current_user.id, REQUIRED_CREDITS):
            return jsonify({
                "success": False,
                "error": "Failed to deduct credits. Please try again."
            }), 400
        
        # Log the query
        log_user_query(current_user.id, analysis_type, subject)
        
        # Add credits to response
        result["credits"] = current_user.credits
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error in analyze_any_paper: {str(e)}")
        return jsonify({
            "success": False,
            "error": "An unexpected error occurred. Please try again."
        }), 500