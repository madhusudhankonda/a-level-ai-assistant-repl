"""
A simple test module to debug API functionality.
"""
import logging
from flask import Blueprint, jsonify, request

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
test_bp = Blueprint('test', __name__)

@test_bp.route('/test-button')
def test_button():
    """Render the test button page"""
    from flask import render_template
    return render_template('test_button.html')

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