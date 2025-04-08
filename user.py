from flask import Blueprint, render_template, request, jsonify, redirect, url_for, current_app, send_file
import os
import base64
import re
import uuid
from datetime import datetime
from models import db, QuestionPaper, Question, Explanation
from utils.openai_helper import generate_explanation

# Create user blueprint
user_bp = Blueprint('user', __name__, template_folder='templates/user')

@user_bp.route('/')
def index():
    """User dashboard showing available papers"""
    # Get all papers with at least one question
    papers = QuestionPaper.query.join(QuestionPaper.questions).group_by(QuestionPaper.id).order_by(QuestionPaper.created_at.desc()).all()
    return render_template('user/index.html', papers=papers)

@user_bp.route('/camera-capture')
def camera_capture():
    """Page for capturing questions with camera"""
    # Get list of subjects for the dropdown
    subjects = db.session.query(QuestionPaper.subject).distinct().all()
    subjects = [s[0] for s in subjects]
    
    return render_template('user/camera_capture.html', subjects=subjects)

@user_bp.route('/paper/<int:paper_id>')
def view_paper(paper_id):
    """View a specific paper and its questions"""
    paper = QuestionPaper.query.get_or_404(paper_id)
    
    # Get all questions for this paper
    questions = Question.query.filter_by(paper_id=paper_id).order_by(Question.question_number).all()
    
    return render_template(
        'user/question_viewer.html', 
        paper=paper, 
        questions=questions
    )

@user_bp.route('/question-image/<int:question_id>')
def get_question_image(question_id):
    """Endpoint to serve question images"""
    question = Question.query.get_or_404(question_id)
    
    # Return the image file
    try:
        return send_file(question.image_path, mimetype='image/png')
    except Exception as e:
        current_app.logger.error(f"Error serving question image: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error retrieving image'
        }), 404

def process_math_notation(text):
    """Process mathematical notation in explanation text to ensure proper rendering"""
    
    # Replace markdown headers with HTML headers to avoid conflicts with LaTeX
    text = re.sub(r'### (.*?)(\n|$)', r'<h3>\1</h3>\n', text)
    text = re.sub(r'#### (.*?)(\n|$)', r'<h4>\1</h4>\n', text)
    
    # Replace bold markdown with HTML bold
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    
    # Replace italic markdown with HTML italic
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    
    # Wrap display math ($$..$$) in special containers for better styling
    text = re.sub(r'\$\$(.*?)\$\$', r'<div class="math-container display-math">\n$$\1$$\n</div>', text, flags=re.DOTALL)
    
    # Ensure inline math ($...$) is properly spaced
    text = re.sub(r'([^\$])\$([^\$])', r'\1 $\2', text)
    text = re.sub(r'([^\$])\$([^\$])', r'\1$ \2', text)
    
    # Format numbered lists
    text = re.sub(r'(\n|\A)(\d+)\.\s+(.*?)(\n|\Z)', r'\1<ol start="\2"><li>\3</li></ol>\4', text)
    
    # Format bullet lists
    text = re.sub(r'(\n|\A)- (.*?)(\n|\Z)', r'\1<ul><li>\2</li></ul>\3', text)
    
    # Wrap code blocks
    text = re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', text, flags=re.DOTALL)
    
    # Add class to the content for styling
    text = f'<div class="markdown-content">{text}</div>'
    
    return text

@user_bp.route('/api/analyze-captured-image', methods=['POST'])
def analyze_captured_image():
    """API endpoint to analyze a question image captured with the camera"""
    try:
        current_app.logger.info("Received image analysis request")
        
        # Validate request format
        if not request.json:
            current_app.logger.error("Invalid request format: No JSON data")
            return jsonify({
                'success': False,
                'message': 'Invalid request format: No JSON data'
            }), 400
            
        # Get the image data and subject from the request
        image_data = request.json.get('image_data', '')
        subject = request.json.get('subject', 'Mathematics')
        
        current_app.logger.info(f"Processing image for subject: {subject}")
        
        if not image_data:
            current_app.logger.error("No image data provided")
            return jsonify({
                'success': False,
                'message': 'No image data provided'
            }), 400
        
        # We should now have clean base64 data from the client
        # Let's log some basic info about it for debugging
        if isinstance(image_data, str):
            current_app.logger.info(f"Received base64 image data of length: {len(image_data)}")
            # Just a simple check to make sure it's valid base64
            try:
                if not image_data.strip():
                    raise ValueError("Empty base64 string")
                # Try decoding a small sample to check validity
                base64.b64decode(image_data[:20] + "=" * ((4 - len(image_data[:20]) % 4) % 4))
                current_app.logger.info("Base64 data appears to be valid")
            except Exception as e:
                current_app.logger.error(f"Invalid base64 data: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': f'Invalid image data format: {str(e)}'
                }), 400
        else:
            current_app.logger.error(f"Received non-string image data: {type(image_data)}")
            return jsonify({
                'success': False,
                'message': 'Image data must be a base64 string'
            }), 400
        
        # Create data directory if it doesn't exist
        data_dir = os.path.join(os.getcwd(), 'data', 'captured_images')
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            current_app.logger.info(f"Created directory: {data_dir}")
        
        # Generate a unique filename and save the image
        filename = f"captured_{uuid.uuid4().hex}.png"
        image_path = os.path.join(data_dir, filename)
        
        try:
            # Decode and save the base64 image
            image_bytes = base64.b64decode(image_data)
            with open(image_path, 'wb') as f:
                f.write(image_bytes)
            current_app.logger.info(f"Image saved to {image_path}")
        except Exception as image_error:
            current_app.logger.error(f"Error saving image: {str(image_error)}")
            return jsonify({
                'success': False,
                'message': f'Error processing image data: {str(image_error)}'
            }), 400
        
        try:
            # Generate explanation using OpenAI
            current_app.logger.info("Calling OpenAI for explanation")
            explanation_text = generate_explanation(
                image_data,
                subject
            )
            current_app.logger.info("Received explanation from OpenAI")
        except Exception as ai_error:
            current_app.logger.error(f"OpenAI API error: {str(ai_error)}")
            return jsonify({
                'success': False,
                'message': f'Error generating explanation: {str(ai_error)}'
            }), 500
        
        # Process the mathematical notation for display
        processed_text = process_math_notation(explanation_text)
        current_app.logger.info("Math notation processed")
        
        return jsonify({
            'success': True,
            'explanation': processed_text,
            'subject': subject,
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        current_app.logger.error(f"Error analyzing captured image: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error analyzing image: {str(e)}'
        }), 500

@user_bp.route('/api/explain/<int:question_id>', methods=['GET', 'POST'])
def explain_question(question_id):
    """API endpoint to get an explanation for a question"""
    question = Question.query.get_or_404(question_id)
    paper = QuestionPaper.query.get(question.paper_id)
    
    # Check if we already have a saved explanation
    existing_explanation = Explanation.query.filter_by(question_id=question_id).order_by(Explanation.generated_at.desc()).first()
    
    # If requesting a new explanation via POST or no saved explanation exists
    if request.method == 'POST' or not existing_explanation:
        try:
            # Read the image and encode it to base64
            with open(question.image_path, "rb") as image_file:
                image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Generate explanation using OpenAI
            explanation_text = generate_explanation(
                image_base64,
                paper.subject
            )
            
            # Process the mathematical notation
            processed_text = process_math_notation(explanation_text)
            
            # Save the original explanation
            explanation = Explanation(
                question_id=question_id,
                explanation_text=explanation_text
            )
            
            db.session.add(explanation)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'question_id': question_id,
                'explanation': processed_text,
                'is_new': True
            })
            
        except Exception as e:
            current_app.logger.error(f"Error generating explanation: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Error generating explanation: {str(e)}'
            }), 500
    
    # Return existing explanation for GET requests when one exists
    processed_text = process_math_notation(existing_explanation.explanation_text)
    
    return jsonify({
        'success': True,
        'question_id': question_id,
        'explanation': processed_text,
        'is_new': False,
        'generated_at': existing_explanation.generated_at.strftime('%Y-%m-%d %H:%M:%S')
    })
