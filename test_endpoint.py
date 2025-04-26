"""
A simple test module to debug API functionality.
"""
import os
import logging
import json
from flask import Blueprint, jsonify, request, render_template, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
test_bp = Blueprint('test', __name__)

@test_bp.route('/test-button')
def test_button():
    """Render the test button page"""
    return render_template('test_button.html')

@test_bp.route('/direct-upload')
@login_required
def direct_upload():
    """Render the direct upload form"""
    return render_template('direct_upload.html')

@test_bp.route('/api/direct-upload', methods=['POST'])
@login_required
def handle_direct_upload():
    """Handle direct file upload with form submission"""
    logger.info("Direct upload endpoint called")
    
    try:
        # Check if a file was uploaded
        if 'file' not in request.files:
            return render_template('direct_upload.html', error="No file selected")
            
        file = request.files['file']
        if file.filename == '':
            return render_template('direct_upload.html', error="No file selected")
            
        # Get form data
        analysis_type = request.form.get('analysis_type', 'question_only')
        subject = request.form.get('subject', 'mathematics')
        
        logger.info(f"Analysis type: {analysis_type}, Subject: {subject}")
        logger.info(f"File: {file.filename}, {file.content_type}")
        
        # Save the file temporarily
        temp_dir = os.path.join(os.getcwd(), 'temp_uploads')
        os.makedirs(temp_dir, exist_ok=True)
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(temp_dir, filename)
        file.save(filepath)
        
        # Simple response for now
        result_html = f"""
        <h4>File Upload Successful</h4>
        <p><strong>Filename:</strong> {filename}</p>
        <p><strong>Analysis Type:</strong> {analysis_type}</p>
        <p><strong>Subject:</strong> {subject}</p>
        <p><strong>File Size:</strong> {os.path.getsize(filepath)} bytes</p>
        """
        
        # Clean up the file
        os.remove(filepath)
        
        return render_template('direct_upload.html', result=result_html)
        
    except Exception as e:
        logger.error(f"Error in direct upload: {str(e)}")
        return render_template('direct_upload.html', error=f"Error: {str(e)}")

@test_bp.route('/api/test-endpoint', methods=['POST'])
def test_endpoint():
    """Simple test API endpoint"""
    logger.info("Test endpoint called")
    
    try:
        # Get request data
        data = request.json
        logger.info(f"Request data: {data}")
        
        if not data:
            logger.warning("No JSON data provided")
            return jsonify({
                "success": False,
                "error": "No data provided."
            }), 400
        
        # Return success response
        return jsonify({
            "success": True,
            "message": "Test endpoint successful!",
            "received_data": data
        }), 200
        
    except Exception as e:
        logger.error(f"Error in test endpoint: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"An error occurred: {str(e)}"
        }), 500