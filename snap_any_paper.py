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
        # Check if it's a data URL
        if image_data.startswith('data:image'):
            # Extract the base64 part
            image_data = re.sub('^data:image/.+;base64,', '', image_data)
            image_data = base64.b64decode(image_data)
            img = Image.open(BytesIO(image_data))
        else:
            # Handle file upload
            img = Image.open(BytesIO(image_data))
        
        # Create a unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"snap_any_paper_{timestamp}.jpg"
        file_path = os.path.join(TEMP_FOLDER, filename)
        
        # Save the image
        img.save(file_path, "JPEG")
        return file_path
    except Exception as e:
        logger.error(f"Error saving image: {str(e)}")
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
        content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
        
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
            query_date=datetime.now(),
            credits_used=REQUIRED_CREDITS
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
    """Render the Snap Any Paper page"""
    return render_template('snap_any_paper.html')

@snap_paper_bp.route('/api/analyze-any-paper', methods=['POST'])
@login_required
def analyze_any_paper():
    """API endpoint to analyze an uploaded paper image"""
    try:
        # Check if user has enough credits
        if current_user.credits < REQUIRED_CREDITS:
            return jsonify({
                "success": False,
                "error": f"You don't have enough credits. {REQUIRED_CREDITS} credits required."
            }), 400
        
        # Get request data
        data = request.json
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided."
            }), 400
        
        image_data = data.get('image')
        analysis_type = data.get('analysis_type', 'question_only')
        subject = data.get('subject', 'mathematics')
        
        if not image_data:
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