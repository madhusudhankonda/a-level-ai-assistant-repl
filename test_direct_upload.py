import os
import base64
import re
import logging
from io import BytesIO
from datetime import datetime
from PIL import Image
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user

from models import User, db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
direct_test_bp = Blueprint('direct_test', __name__)

# Constants
TEMP_FOLDER = 'temp_uploads'

# Ensure temp folder exists
if not os.path.exists(TEMP_FOLDER):
    os.makedirs(TEMP_FOLDER)

def save_image_data(image_data):
    """Save image data to temporary file and return the path"""
    try:
        logger.info("="*50)
        logger.info("DIRECT TEST - SAVE IMAGE FUNCTION")
        logger.info("="*50)
        logger.info(f"Image data type: {type(image_data)}")
        logger.info(f"Image data length: {len(image_data) if image_data else 0}")
        
        if not image_data:
            logger.error("Image data is empty or None")
            return None
            
        # Log the first 100 chars to see what we're dealing with
        sample = image_data[:100] if isinstance(image_data, str) else "Non-string data"
        logger.info(f"First 100 chars of image_data: {sample}")
        
        # Extract the base64 part if it's a data URL
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
                
        # Create a unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"direct_test_{timestamp}.jpg"
        file_path = os.path.join(TEMP_FOLDER, filename)
        logger.info(f"Created temp file path: {file_path}")
        
        # Open and save the image
        try:
            img = Image.open(BytesIO(image_data))
            logger.info(f"Successfully opened image, format: {img.format}, size: {img.size}")
            img.save(file_path, "JPEG")
            logger.info(f"Successfully saved image to {file_path}")
            return file_path
        except Exception as img_error:
            logger.error(f"Error processing image: {str(img_error)}")
            return None
            
    except Exception as e:
        logger.error(f"Error in save_image_data: {str(e)}")
        logger.exception("Detailed traceback:")
        return None

@direct_test_bp.route('/direct-test')
@login_required
def direct_test():
    """Render a super simple direct test page"""
    return render_template('direct_test.html')

@direct_test_bp.route('/api/direct-test', methods=['POST'])
@login_required
def handle_direct_test():
    """API endpoint for the direct test"""
    logger.info("="*50)
    logger.info("DIRECT TEST API ENDPOINT")
    logger.info("="*50)
    logger.info(f"Request method: {request.method}")
    logger.info(f"Content-Type: {request.headers.get('Content-Type')}")
    logger.info(f"User ID: {current_user.id}, Username: {current_user.username}")
    
    try:
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
        
        # More detailed logging
        logger.info(f"Image data present: {bool(image_data)}")
        logger.info(f"Image data length: {len(image_data) if image_data else 0}")
        
        if not image_data:
            logger.error("No image data provided in request")
            return jsonify({
                "success": False,
                "error": "No image provided."
            }), 400
        
        # Save temporary image - just to test if it works
        temp_file_path = save_image_data(image_data)
        if not temp_file_path:
            return jsonify({
                "success": False,
                "error": "Failed to process the image. Please try again."
            }), 400
        
        # If we got here, the image was saved successfully
        return jsonify({
            "success": True,
            "message": f"Image processed successfully. Path: {temp_file_path}",
            "file_path": temp_file_path
        }), 200
        
    except Exception as e:
        logger.error(f"Error in direct_test endpoint: {str(e)}")
        logger.exception("Detailed traceback:")
        return jsonify({
            "success": False,
            "error": "An unexpected error occurred. Please try again."
        }), 500