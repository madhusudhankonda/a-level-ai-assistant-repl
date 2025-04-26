"""
Simple route handlers for testing the image analysis functionality
with minimal dependencies and maximum simplicity.
"""

import os
import json
import logging
import time
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
simple_test_bp = Blueprint('simple_test', __name__)

@simple_test_bp.route('/simple-test')
@login_required
def simple_test():
    """Render the simple test page with template version to bypass cache"""
    return render_template('simple_test.html', version=int(time.time()))

@simple_test_bp.route('/api/simple-analyze', methods=['POST'])
@login_required
def simple_analyze():
    """Super simple endpoint to test image analysis without dependencies"""
    logger.info("Simple analyze endpoint called")
    
    try:
        # Basic error checking
        if not request.is_json:
            logger.error("Request is not JSON")
            return jsonify({
                "success": False,
                "error": "Request must be JSON"
            }), 400
        
        data = request.json
        if not data:
            logger.error("No data in request")
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        # Log request data for debugging
        logger.info(f"Request data keys: {list(data.keys())}")
        logger.info(f"User: {current_user.username} (ID: {current_user.id})")
        
        # Check for image data
        image_data = data.get('image')
        if not image_data:
            logger.error("No image data provided")
            return jsonify({
                "success": False,
                "error": "No image data provided"
            }), 400
            
        logger.info(f"Image data length: {len(image_data) if image_data else 0}")
        
        # Just return a success response without processing
        # This helps isolate if the issue is with OpenAI or with basic request handling
        return jsonify({
            "success": True,
            "title": "Simple Analysis Test",
            "analysis": "<p>This is a test response from the simple analyze endpoint.</p>" + 
                        "<p>Your image was received successfully.</p>" +
                        f"<p>Image data length: {len(image_data)} characters</p>"
        }), 200
        
    except Exception as e:
        logger.error(f"Error in simple analyze: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"An error occurred: {str(e)}"
        }), 500