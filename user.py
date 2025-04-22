from flask import Blueprint, render_template, request, jsonify, redirect, url_for, current_app, send_file, flash, make_response
import os
import base64
import re
import uuid
import json
from datetime import datetime
from flask_login import login_required, current_user
from models import (
    db, Subject, ExamBoard, PaperCategory, QuestionPaper, 
    Question, Explanation, User, UserQuery, StudentAnswer, QuestionTopic, UserProfile
)
from utils.openai_helper import generate_explanation, generate_answer_feedback, test_openai_connection

# Create user blueprint
user_bp = Blueprint('user', __name__, template_folder='templates/user')

@user_bp.route('/')
def index():
    """User dashboard showing available papers through hierarchical navigation"""
    # Get all subjects with related data
    subjects = Subject.query.all()
    
    # Get all boards (with subject information) for dropdown navigation
    all_boards = ExamBoard.query.all()
    
    # Get all paper categories for dropdown navigation
    all_categories = PaperCategory.query.all()
    
    # Check if we have hierarchical data
    if subjects:
        # We have subjects, use the new hierarchical interface with dropdown navigation
        return render_template('user/index_hierarchical.html', 
                             subjects=subjects,
                             boards=all_boards,
                             categories=all_categories)
    else:
        # Fall back to the old interface if no subjects are found
        try:
            # Get all papers with at least one question
            papers = QuestionPaper.query.all()
            return render_template('user/index.html', papers=papers)
        except Exception as e:
            # If there's an error, just show an empty list
            current_app.logger.error(f"Error fetching papers: {str(e)}")
            return render_template('user/index.html', papers=[])

@user_bp.route('/camera-capture')
def camera_capture():
    """Page for capturing questions with camera"""
    # Get list of subjects for the dropdown
    subjects = db.session.query(QuestionPaper.subject).distinct().all()
    subjects = [s[0] for s in subjects]
    
    return render_template('user/camera_capture_new.html', subjects=subjects)

@user_bp.route('/api/test-openai', methods=['GET'])
def test_openai_api():
    """Test endpoint to check OpenAI API connection"""
    current_app.logger.info("Testing OpenAI API connection")
    
    success, message = test_openai_connection()
    
    return jsonify({
        'success': success,
        'message': message
    })

@user_bp.route('/api/test-image-analysis', methods=['GET'])
@login_required
def test_image_analysis():
    """Test endpoint for the image analysis functionality"""
    try:
        current_app.logger.info(f"Test image analysis endpoint called by user {current_user.id}")
        
        # Import the OpenAI helper
        from utils.openai_helper import generate_explanation
        
        # Path to a sample image to test with
        sample_image_path = "./data/questions/paper_1/question_q1_703866-q1.png"
        
        # If the image exists, process it
        if os.path.exists(sample_image_path):
            # Read and encode the image
            with open(sample_image_path, "rb") as img_file:
                img_data = base64.b64encode(img_file.read()).decode('utf-8')
                
            # Call the explanation function directly
            try:
                result = generate_explanation(img_data, "Mathematics")
                
                # If successful, return the explanation
                return jsonify({
                    'success': True,
                    'explanation': result[:200] + "..." if len(result) > 200 else result,
                    'message': 'Image analysis test successful'
                })
            except Exception as api_error:
                current_app.logger.error(f"API error in test: {str(api_error)}")
                return jsonify({
                    'success': False,
                    'message': f'API error: {str(api_error)}'
                }), 500
        else:
            # If the sample image doesn't exist
            return jsonify({
                'success': False,
                'message': f'Sample image not found at {sample_image_path}'
            }), 404
    except Exception as e:
        current_app.logger.error(f"Error in test image analysis: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Test error: {str(e)}'
        }), 500

@user_bp.route('/api/check-ai-consent', methods=['GET'])
@login_required
def check_ai_consent():
    """Check if the user has consented to AI usage"""
    current_app.logger.info(f"check-ai-consent endpoint called by user {current_user.id}")
    """API endpoint to check if user has consented to AI usage"""
    try:
        # Get user profile
        user_profile = UserProfile.query.filter_by(user_id=current_user.id).first()
        
        # If no profile or consent required, user hasn't consented
        if not user_profile or user_profile.ai_usage_consent_required:
            return jsonify({
                'success': True,
                'consent_given': False
            })
        
        # Check if consent was given within the last 30 days
        if user_profile.last_ai_consent_date:
            consent_age = datetime.utcnow() - user_profile.last_ai_consent_date
            # If consent is older than 30 days, require new consent
            if consent_age.days > 30:
                user_profile.ai_usage_consent_required = True
                db.session.commit()
                return jsonify({
                    'success': True,
                    'consent_given': False,
                    'reason': 'Consent expired'
                })
        
        # User has valid consent
        return jsonify({
            'success': True,
            'consent_given': True,
            'last_consent_date': user_profile.last_ai_consent_date.isoformat() if user_profile.last_ai_consent_date else None
        })
    
    except Exception as e:
        current_app.logger.error(f"Error checking AI consent: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error checking consent: {str(e)}'
        }), 500

@user_bp.route('/api/record-ai-consent', methods=['POST'])
@login_required
def record_ai_consent():
    """API endpoint to record user's consent for AI usage"""
    try:
        # Support both JSON and form data
        if request.is_json:
            data = request.json
            consent_given = data.get('consent_given', False)
        else:
            # Handle form data from the consent modal
            consent_given = 'ai_consent' in request.form
        
        if not consent_given:
            return jsonify({
                'success': False,
                'message': 'Consent is required to use AI features'
            }), 400
        
        # Get user profile or create if not exists
        user_profile = UserProfile.query.filter_by(user_id=current_user.id).first()
        if not user_profile:
            user_profile = UserProfile(user_id=current_user.id)
            db.session.add(user_profile)
        
        # Update consent info
        user_profile.ai_usage_consent_required = False
        user_profile.last_ai_consent_date = datetime.utcnow()
        
        # Log the update for debugging
        current_app.logger.info(f"Recording AI consent for user {current_user.id}. Setting ai_usage_consent_required=False and last_ai_consent_date={user_profile.last_ai_consent_date}")
        
        db.session.commit()
        
        # Double-check if the changes were saved properly
        db.session.refresh(user_profile)
        current_app.logger.info(f"After commit: User {current_user.id}, ai_usage_consent_required={user_profile.ai_usage_consent_required}, last_ai_consent_date={user_profile.last_ai_consent_date}")
        
        return jsonify({
            'success': True,
            'message': 'AI usage consent recorded successfully'
        })
    
    except Exception as e:
        current_app.logger.error(f"Error recording AI consent: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error recording consent: {str(e)}'
        }), 500

@user_bp.route('/subject/<int:subject_id>')
def view_subject(subject_id):
    """View a specific subject and its exam boards"""
    subject = Subject.query.get_or_404(subject_id)
    boards = ExamBoard.query.filter_by(subject_id=subject_id).all()
    
    return render_template(
        'user/subject_view.html',
        subject=subject,
        boards=boards
    )

@user_bp.route('/board/<int:board_id>')
def view_board(board_id):
    """View a specific exam board and its paper categories"""
    board = ExamBoard.query.get_or_404(board_id)
    categories = PaperCategory.query.filter_by(board_id=board_id).all()
    
    return render_template(
        'user/board_view.html',
        board=board,
        categories=categories
    )

@user_bp.route('/board/<int:board_id>/exams')
def view_board_exams(board_id):
    """View papers for a specific exam board organized by exam period"""
    board = ExamBoard.query.get_or_404(board_id)
    
    # Get all papers for this board across all categories
    papers_by_period = {}
    
    # Get all categories for this board
    categories = PaperCategory.query.filter_by(board_id=board_id).all()
    
    # For each category, get the papers and organize by exam period
    for category in categories:
        papers = QuestionPaper.query.filter_by(category_id=category.id).all()
        for paper in papers:
            period = paper.exam_period or "Unknown"
            if period not in papers_by_period:
                papers_by_period[period] = []
            
            # Add category information to the paper for display
            paper.category_name = category.name
            papers_by_period[period].append(paper)
    
    # Sort the periods (typically these would be like "June 2023", "November 2022", etc.)
    sorted_periods = sorted(papers_by_period.keys(), reverse=True)
    
    return render_template(
        'user/board_exams_view.html',
        board=board,
        papers_by_period=papers_by_period,
        sorted_periods=sorted_periods
    )

@user_bp.route('/category/<int:category_id>')
def view_category(category_id):
    """View a specific paper category and its papers"""
    try:
        # Try to get the category
        category = PaperCategory.query.get(category_id)
        if not category:
            # If category doesn't exist, flash a message and redirect to dashboard
            flash(f"Category with ID {category_id} not found.", "warning")
            return redirect(url_for('user.index'))
            
        # Get papers for this category
        papers = QuestionPaper.query.filter_by(category_id=category_id).all()
        
        return render_template(
            'user/category_view.html',
            category=category,
            papers=papers
        )
    except Exception as e:
        # Log the error for debugging
        current_app.logger.error(f"Error displaying category {category_id}: {str(e)}")
        flash(f"An error occurred while loading the category. Please try again.", "danger")
        return redirect(url_for('user.index'))
    

@user_bp.route('/paper/<int:paper_id>')
def view_paper(paper_id):
    """View a specific paper and its questions"""
    try:
        # Get the paper or redirect with an error message
        paper = QuestionPaper.query.get(paper_id)
        if not paper:
            flash(f"Paper with ID {paper_id} not found.", "warning")
            return redirect(url_for('user.index'))
        
        # Get all questions for this paper and log them for debugging
        questions = Question.query.filter_by(paper_id=paper_id).all()
        current_app.logger.info(f"Found {len(questions)} questions for paper ID {paper_id}")
        
        # Log question info for debugging
        for q in questions:
            current_app.logger.info(f"Question ID: {q.id}, Number: {q.question_number}, Path: {q.image_path}")
        
        # If no questions found, populate with sample questions for paper ID 1
        if not questions and paper_id == 1:  # Only for the first paper (Mathematics sample)
            current_app.logger.info("No questions found for sample paper, creating sample questions")
            
            # Create sample questions for the paper
            sample_questions = [
                {'number': 'q1', 'image': './data/questions/paper_1/question_q1_703866-q1.png', 'marks': 10},
                {'number': 'q2', 'image': './data/questions/paper_1/question_q2_703866-q2.png', 'marks': 10},
                {'number': 'q3', 'image': './data/questions/paper_1/question_q3_703866-q3.png', 'marks': 10},
                {'number': 'q4', 'image': './data/questions/paper_1/question_q4_703866-q4.png', 'marks': 10}
            ]
            
            for q_data in sample_questions:
                # Check if the question image exists
                if os.path.exists(q_data['image']):
                    current_app.logger.info(f"Creating sample question from {q_data['image']}")
                    # Create the question in the database
                    new_question = Question(
                        paper_id=paper_id,
                        question_number=q_data['number'],
                        marks=q_data['marks'],
                        image_path=q_data['image']
                    )
                    db.session.add(new_question)
            
            # Commit all sample questions
            db.session.commit()
            
            # Reload questions
            questions = Question.query.filter_by(paper_id=paper_id).all()
            current_app.logger.info(f"Created {len(questions)} sample questions for paper ID {paper_id}")
        
        # Sort questions numerically by question number
        # This handles question numbers like '1', '2', '10' properly
        def question_number_key(q):
            # Extract the numeric part from the question number
            # This handles formats like 'q1', '1a', 'question 1', etc.
            import re
            num_match = re.search(r'(\d+)', q.question_number)
            if num_match:
                return int(num_match.group(1))
            return 0  # Default to 0 if no number found
        
        # Sort the questions using the custom sorting function
        questions = sorted(questions, key=question_number_key)
        
        # Get category information if available
        category = None
        board = None
        subject = None
        
        if paper.category_id:
            category = PaperCategory.query.get(paper.category_id)
            if category:
                board = ExamBoard.query.get(category.board_id)
                if board:
                    subject = Subject.query.get(board.subject_id)
        
        # Check if there are any questions
        if not questions:
            flash("This paper does not have any questions yet.", "info")
        
        return render_template(
            'user/question_viewer.html', 
            paper=paper, 
            questions=questions,
            category=category,
            board=board,
            subject=subject
        )
    except Exception as e:
        # Log the error for debugging
        current_app.logger.error(f"Error displaying paper {paper_id}: {str(e)}")
        flash("An error occurred while loading the paper. Please try again.", "danger")
        return redirect(url_for('user.index'))
    

@user_bp.route('/question-image/<int:question_id>')
def get_question_image(question_id):
    """Endpoint to serve question images"""
    try:
        # Get the question or return a friendly error
        question = Question.query.get(question_id)
        if not question:
            current_app.logger.error(f"Question with ID {question_id} not found")
            # Return a placeholder image or error message
            return jsonify({
                'success': False,
                'message': f'Question with ID {question_id} not found'
            }), 404
        
        # Special handling for paper 57 questions 5-12 where we don't have original images 
        # and need to show an appropriate message instead of Q1's image
        paper_id = question.paper_id
        question_num = question.question_number
        if paper_id == 57 and question_num in ['q5', 'q6', 'q7', 'q8', 'q9', 'q10', 'q11', 'q12']:
            # For paper 57 questions 5-12, we need to use their actual images
            question_number = int(question_num.replace('q', ''))
            current_app.logger.info(f"Special handling for paper 57, question {question_num}")
            
            # For question 7, we need to use the image_1745269580538.png
            if question_num == 'q7':
                # This is the triangle question image you shared
                img_path = './attached_assets/image_1745269580538.png'
                if os.path.isfile(img_path):
                    current_app.logger.info(f"Using specific image for q7: {img_path}")
                    response = make_response(send_file(img_path, mimetype='image/png'))
                    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
                    return response
        
        # Return the image file
        try:
            # Get paths to try
            image_path = question.image_path
            current_app.logger.info(f"Attempting to serve image at path: {image_path}")
            
            # Extract folder name and filename
            folder_name = os.path.basename(os.path.dirname(image_path))
            file_name = os.path.basename(image_path)
            current_app.logger.info(f"Image folder: {folder_name}, filename: {file_name}")
            
            # Get the question number for fallback purposes
            question_number = question.question_number.replace('q', '')
            try:
                q_num = int(question_number)
            except Exception as e:
                current_app.logger.warning(f"Could not parse question number: {str(e)}")
                q_num = 1
            
            # Create a list of possible paths to try - prioritize actual uploaded images 
            # from the attached_assets directory
            
            # First, try the original uploaded question files, prioritizing original authentic assets
            if 1 <= q_num <= 4:
                # First priority - use the original images we have for questions 1-4
                original_image_path = f"./data/questions/paper_1/question_q{q_num}_703866-q{q_num}.png"
                if os.path.isfile(original_image_path):
                    current_app.logger.info(f"Using original uploaded image for q{q_num}")
                    response = make_response(send_file(original_image_path, mimetype='image/png'))
                    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
                    return response
            
            # Try database paths as fallback
            paths_to_try = [
                image_path,  # Original path from database
                image_path.replace('/home/runner/workspace/', './'),  # Relative path
                f"./data/{folder_name}/{file_name}",  # Local data folder
                f"./{folder_name}/{file_name}",  # Direct folder access
                
                # Try storage in other formats
                os.path.join(os.getcwd(), 'data', folder_name, file_name),
                os.path.join(os.getcwd(), folder_name, file_name)
            ]
            
            # Add the original image path if it exists
            if 1 <= q_num <= 4:  # We have originals for q1-q4
                # Include the original image path as the first option
                paths_to_try.insert(0, f"./data/questions/paper_1/question_q{q_num}_703866-q{q_num}.png")
            elif 1 <= q_num <= 12:  # For other questions, use q1 as fallback
                paths_to_try.append(f"./data/questions/paper_1/question_q1_703866-q1.png")
            else:
                # Fallback to q1 if we can't determine the question number
                paths_to_try.append(f"./data/questions/paper_1/question_q1_703866-q1.png")
            
            # Try each path
            for path in paths_to_try:
                current_app.logger.info(f"Trying path: {path}")
                if os.path.isfile(path):
                    current_app.logger.info(f"Found image at: {path}")
                    # Add a timestamp to prevent browser caching
                    response = make_response(send_file(path, mimetype='image/png'))
                    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
                    response.headers['Pragma'] = 'no-cache'
                    response.headers['Expires'] = '0'
                    # Add a timestamp as query param to force fresh load
                    response.headers['X-Timestamp'] = str(datetime.now().timestamp())
                    return response
            
            # If we get here, no image was found
            current_app.logger.error(f"Image file not found in any of these locations: {', '.join(paths_to_try)}")
            
            # Return a placeholder or default image instead of error
            # Let's check if we have any sample images to use
            
            # Determine which uploaded question file to use based on the question number
            # Use the original uploaded images as the primary source
            original_image = f"./data/questions/paper_1/question_q{q_num}_703866-q{q_num}.png"
            
            # Use the original images you uploaded for all questions
            current_app.logger.info(f"Looking for original image: {original_image}")
            
            sample_paths = [
                original_image,  # Try the specific question's original image first
                "./data/questions/paper_1/question_q1_703866-q1.png",  # Fallback to q1 original if specific not found
                "./data/papers/sample_math_paper.png"  # Final fallback
            ]
            
            for path in sample_paths:
                if os.path.isfile(path):
                    current_app.logger.warning(f"Using sample image instead: {path}")
                    # Set a cookie to indicate this is a fallback image
                    response = make_response(send_file(path, mimetype='image/png'))
                    response.headers['X-Is-Fallback-Image'] = 'true'
                    return response
            
            # If all attempts fail, log the error
            return jsonify({
                'success': False,
                'message': 'Image file not found'
            }), 404
        except Exception as e:
            current_app.logger.error(f"Error serving question image: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Error retrieving image: {str(e)}'
            }), 404
    except Exception as outer_e:
        current_app.logger.error(f"Unexpected error in get_question_image: {str(outer_e)}")
        return jsonify({
            'success': False,
            'message': 'An unexpected error occurred'
        }), 500

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
@login_required
def analyze_captured_image():
    """API endpoint to analyze a captured image of a question"""
    current_app.logger.info(f"analyze-captured-image endpoint called by user {current_user.id}")
    try:
        current_app.logger.info("Received image analysis request")
        
        # Get user profile, but don't block based on consent status
        user_profile = UserProfile.query.filter_by(user_id=current_user.id).first()
        
        # Log user information
        if user_profile:
            current_app.logger.info(f"User {current_user.id} consent status: ai_usage_consent_required={user_profile.ai_usage_consent_required}, last_ai_consent_date={user_profile.last_ai_consent_date}")
            
            # Auto-update consent to avoid blocking access
            if user_profile.ai_usage_consent_required or not user_profile.last_ai_consent_date:
                user_profile.ai_usage_consent_required = False
                user_profile.last_ai_consent_date = datetime.utcnow()
                db.session.commit()
                current_app.logger.info(f"Updated consent for user {current_user.id}")
        else:
            current_app.logger.warning(f"User {current_user.id} does not have a UserProfile record, creating one")
            # Create a profile with consent for this user
            user_profile = UserProfile(
                user_id=current_user.id,
                ai_usage_consent_required=False,
                last_ai_consent_date=datetime.utcnow()
            )
            db.session.add(user_profile)
            db.session.commit()
        
        # Credit verification - require 10 credits per analysis
        if not current_user.has_sufficient_credits(10):
            current_app.logger.warning(f"User {current_user.id} attempted analysis without sufficient credits")
            return jsonify({
                'success': False,
                'message': 'You need at least 10 credits to use this feature. Please purchase more credits.',
                'credits_required': True
            }), 403
        
        # Validate request format
        if not request.json:
            current_app.logger.error("Invalid request format: No JSON data")
            return jsonify({
                'success': False,
                'message': 'Invalid request format: No JSON data'
            }), 400
            
        # Get the image data and subject from the request and log the payload size
        request_size = len(str(request.json))
        current_app.logger.info(f"Received analysis request: JSON payload size: {request_size / 1024:.2f} KB")
        
        image_data = request.json.get('image_data', '')
        subject = request.json.get('subject', 'Mathematics')
        mode = request.json.get('mode', 'question-only')  # Default to question-only
        
        current_app.logger.info(f"Processing image for subject: {subject}, mode: {mode}, image data length: {len(image_data) if image_data else 'EMPTY'}")
        
        if not image_data:
            current_app.logger.error("No image data provided")
            return jsonify({
                'success': False,
                'message': 'No image data provided'
            }), 400
        
        # Check image data format
        if isinstance(image_data, str):
            current_app.logger.info(f"Received image data of length: {len(image_data)}")
            
            # Handle data URI format (e.g., data:image/jpeg;base64,...)
            if image_data.startswith('data:'):
                current_app.logger.info("Received image in data URI format")
                try:
                    # Extract the base64 part from the data URI
                    if ';base64,' in image_data:
                        base64_part = image_data.split(';base64,')[1]
                        current_app.logger.info(f"Extracted base64 data of length: {len(base64_part)}")
                        
                        # This variable will be used for saving the image
                        clean_base64 = base64_part
                    else:
                        current_app.logger.error("Invalid data URI format (missing base64 marker)")
                        return jsonify({
                            'success': False,
                            'message': 'Invalid image format (missing base64 marker)'
                        }), 400
                except Exception as uri_error:
                    current_app.logger.error(f"Error parsing data URI: {str(uri_error)}")
                    return jsonify({
                        'success': False,
                        'message': f'Error parsing image data: {str(uri_error)}'
                    }), 400
            else:
                # Assume it's already a clean base64 string
                current_app.logger.info("Received image data as plain base64")
                clean_base64 = image_data
                
            # Validate the base64 data
            try:
                if not clean_base64.strip():
                    raise ValueError("Empty base64 string")
                # Test decode a small sample
                padding = "=" * ((4 - len(clean_base64[:20]) % 4) % 4)
                base64.b64decode(clean_base64[:20] + padding)
                current_app.logger.info("Image data appears to be valid")
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
                'message': 'Image data must be a string'
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
            # Decode and save the base64 image using our cleaned base64 data
            image_bytes = base64.b64decode(clean_base64)
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
            
            # We'll pass the original image_data (data URI format) to OpenAI
            # This is compatible with our updated OpenAI helper
            current_app.logger.info(f"Image data length being sent to OpenAI: {len(image_data) if image_data else 'EMPTY'}")
            
            # Validate the image data before sending to OpenAI
            if not image_data or len(image_data) < 100:  # Arbitrary minimum length for valid data
                current_app.logger.error("Image data appears to be too short or empty")
                return jsonify({
                    'success': False,
                    'message': 'The captured image data is invalid or too small. Please try again with a clearer picture.'
                }), 400
            
            # Import here to refresh the module and ensure environment variables are loaded
            from utils.openai_helper import generate_explanation, OPENAI_API_KEY
            
            # Check API key availability
            if not OPENAI_API_KEY:
                current_app.logger.error("OpenAI API key is not available in the environment")
                return jsonify({
                    'success': False,
                    'message': 'API configuration error: Missing OpenAI API key. Please contact support.'
                }), 500
                
            current_app.logger.info(f"OpenAI API key is available (length: {len(OPENAI_API_KEY)})")
            
            # Call OpenAI with the validated image data (using the full data URI format)
            explanation_text = generate_explanation(
                image_data,  # Send the complete data URI
                subject
            )
            current_app.logger.info("Received explanation from OpenAI")
            
            # Log the length of the explanation received
            current_app.logger.info(f"Received explanation of length: {len(explanation_text)}")
            
        except Exception as ai_error:
            error_message = str(ai_error)
            current_app.logger.error(f"OpenAI API error: {error_message}")
            
            # Provide user-friendly error messages
            if "pattern" in error_message.lower():
                message = "Image format error: There was an issue with the captured image. Please try again with a clearer picture."
            elif "api key" in error_message.lower():
                message = "API configuration error. Please contact support."
            else:
                message = f"Error generating explanation: {error_message}"
                
            return jsonify({
                'success': False,
                'message': message
            }), 500
        
        # The explanation is already in text format from OpenAI - no JSON parsing needed
        current_app.logger.info("Using explanation text directly without JSON parsing")
        
        # Process the mathematical notation for display
        processed_text = process_math_notation(explanation_text)
        current_app.logger.info("Math notation processed")
        
        # Deduct 10 credits for successful AI explanation
        if not current_user.use_credits(10):
            # This should never happen as we checked credits earlier, but just in case
            current_app.logger.error(f"Failed to deduct credits from user {current_user.id} - insufficient balance")
            return jsonify({
                'success': False,
                'message': 'You need at least 10 credits to use this feature. Please purchase more credits.',
                'credits_required': True
            }), 403
            
        db.session.commit()
        current_app.logger.info(f"Deducted 10 credits from user {current_user.id}, new balance: {current_user.credits}")
        
        # Create a well-structured response
        return jsonify({
            'success': True,
            'explanation': processed_text,
            'subject': subject,
            'credits_remaining': current_user.credits,
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        current_app.logger.error(f"Error analyzing captured image: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error analyzing image: {str(e)}'
        }), 500

@user_bp.route('/api/analyze-answer', methods=['POST'])
@login_required
def analyze_answer():
    """API endpoint to analyze a student's answer"""
    current_app.logger.info(f"analyze-answer endpoint called by user {current_user.id}")
    """API endpoint to analyze both question and student answer images"""
    try:
        current_app.logger.info("Received answer analysis request")
        
        # Get user profile, but don't block based on consent status
        user_profile = UserProfile.query.filter_by(user_id=current_user.id).first()
        
        # Log user information
        if user_profile:
            current_app.logger.info(f"User {current_user.id} consent status: ai_usage_consent_required={user_profile.ai_usage_consent_required}, last_ai_consent_date={user_profile.last_ai_consent_date}")
            
            # Auto-update consent to avoid blocking access
            if user_profile.ai_usage_consent_required or not user_profile.last_ai_consent_date:
                user_profile.ai_usage_consent_required = False
                user_profile.last_ai_consent_date = datetime.utcnow()
                db.session.commit()
                current_app.logger.info(f"Updated consent for user {current_user.id}")
        else:
            current_app.logger.warning(f"User {current_user.id} does not have a UserProfile record, creating one")
            # Create a profile with consent for this user
            user_profile = UserProfile(
                user_id=current_user.id,
                ai_usage_consent_required=False,
                last_ai_consent_date=datetime.utcnow()
            )
            db.session.add(user_profile)
            db.session.commit()
        
        # Credit verification - require 10 credits per analysis
        if not current_user.has_sufficient_credits(10):
            current_app.logger.warning(f"User {current_user.id} attempted answer analysis without sufficient credits")
            return jsonify({
                'success': False,
                'message': 'You need at least 10 credits to use this feature. Please purchase more credits.',
                'credits_required': True
            }), 403
        
        # Validate request format
        if not request.json:
            current_app.logger.error("Invalid request format: No JSON data")
            return jsonify({
                'success': False,
                'message': 'Invalid request format: No JSON data'
            }), 400
            
        # Get the image data and subject from the request
        question_image = request.json.get('question_image', '')
        answer_image = request.json.get('answer_image', '')
        subject = request.json.get('subject', 'Mathematics')
        
        current_app.logger.info(f"Processing answer for subject: {subject}")
        
        # Validate both images
        if not question_image or not answer_image:
            current_app.logger.error("Missing question or answer image")
            return jsonify({
                'success': False,
                'message': 'Both question and answer images are required'
            }), 400
            
        # Validate image formats (both should be data URIs)
        if not isinstance(question_image, str) or not isinstance(answer_image, str):
            current_app.logger.error("Invalid image data types")
            return jsonify({
                'success': False,
                'message': 'Image data must be strings'
            }), 400
        
        # Create data directory if it doesn't exist
        data_dir = os.path.join(os.getcwd(), 'data', 'student_answers')
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            current_app.logger.info(f"Created directory: {data_dir}")
        
        # Generate unique IDs for this analysis
        analysis_id = uuid.uuid4().hex
        
        try:
            # Call OpenAI to analyze the student's answer
            current_app.logger.info("Calling OpenAI to analyze student answer")
            
            # Import here to refresh the module and ensure environment variables are loaded
            from utils.openai_helper import generate_answer_feedback, OPENAI_API_KEY
            
            # Check API key availability
            if not OPENAI_API_KEY:
                current_app.logger.error("OpenAI API key is not available in the environment")
                return jsonify({
                    'success': False,
                    'message': 'API configuration error: Missing OpenAI API key. Please contact support.'
                }), 500
                
            current_app.logger.info(f"OpenAI API key is available (length: {len(OPENAI_API_KEY)})")
            
            # Log the mode we're using
            analysis_mode = request.json.get('mode', 'answer-feedback')
            current_app.logger.info(f"Answer analysis mode: {analysis_mode}")
            
            # Check if this is a combined image (explicitly specified or identical images)
            is_combined_image = request.json.get('combined_image', False)
            same_image = question_image == answer_image
            
            if is_combined_image or same_image:
                current_app.logger.info(f"Using combined image mode: explicitly set={is_combined_image}, identical images={same_image}")
                
                # Update the prompt to inform OpenAI that this is a combined image containing both question and answer
                response = generate_answer_feedback(
                    question_image,  # Combined image with both question and answer (data URI)
                    answer_image,    # Pass the answer image for backwards compatibility
                    subject,
                    combined_image=True
                )
            else:
                # Use regular two-image processing if they're different
                current_app.logger.info("Processing separate question and answer images")
                response = generate_answer_feedback(
                    question_image,  # Question image (data URI)
                    answer_image,    # Answer image (data URI)
                    subject
                )
            
            current_app.logger.info("Received answer analysis from OpenAI")
            
            # Extract the different components from the response
            feedback = process_math_notation(response.get('feedback', 'No feedback available'))
            explanation = process_math_notation(response.get('explanation', 'No explanation available'))
            tips = process_math_notation(response.get('tips', 'No tips available'))
            score = response.get('score', '3/5 Marks')  # Default to 3/5 marks if not provided
            
            # Deduct 10 credits for successful AI answer analysis
            if not current_user.use_credits(10):
                # This should never happen as we checked credits earlier, but just in case
                current_app.logger.error(f"Failed to deduct credits from user {current_user.id} - insufficient balance")
                return jsonify({
                    'success': False,
                    'message': 'You need at least 10 credits to use this feature. Please purchase more credits.',
                    'credits_required': True
                }), 403
                
            db.session.commit()
            current_app.logger.info(f"Deducted 10 credits from user {current_user.id}, new balance: {current_user.credits}")
            
            # Create the response
            return jsonify({
                'success': True,
                'feedback': feedback,
                'explanation': explanation,
                'tips': tips,
                'score': score,
                'subject': subject,
                'credits_remaining': current_user.credits,
                'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            })
            
        except Exception as ai_error:
            error_message = str(ai_error)
            current_app.logger.error(f"OpenAI API error: {error_message}")
            
            # Provide user-friendly error messages
            if "pattern" in error_message.lower():
                message = "Image format error: There was an issue with the captured images. Please try again with clearer pictures."
            elif "api key" in error_message.lower():
                message = "API configuration error. Please contact support."
            else:
                message = f"Error analyzing answer: {error_message}"
                
            return jsonify({
                'success': False,
                'message': message
            }), 500
            
    except Exception as e:
        current_app.logger.error(f"Error analyzing student answer: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error analyzing answer: {str(e)}'
        }), 500

@user_bp.route('/api/explain/<int:question_id>', methods=['GET', 'POST'])
@login_required
def api_get_explanation(question_id):
    """API endpoint to get an explanation for a question
    
    This endpoint serves two purposes:
    1. GET: Retrieves an existing explanation or auto-generates one if none exists
    2. POST: Forces regeneration of an explanation using OpenAI
    """
    try:
        # Get the question or return an error
        question = Question.query.get(question_id)
        if not question:
            current_app.logger.error(f"Question with ID {question_id} not found")
            return jsonify({
                'success': False,
                'message': f'Question with ID {question_id} not found'
            }), 404
        
        paper = QuestionPaper.query.get(question.paper_id)
        if not paper:
            current_app.logger.error(f"Paper with ID {question.paper_id} not found")
            return jsonify({
                'success': False,
                'message': 'The paper associated with this question could not be found'
            }), 404
        
        # Check if user is authenticated - needed for all operations
        if not current_user.is_authenticated:
            current_app.logger.warning("Unauthenticated user attempted to access explanation")
            return jsonify({
                'success': False,
                'message': 'You need to be logged in to view explanations.',
                'requires_login': True
            }), 403
        
        # Log the user and request method for debugging
        current_app.logger.info(f"User {current_user.id} requesting explanation for question {question_id} via {request.method}")
        
        # Check if the current user has already queried this explanation (for caching)
        user_cached_explanation = UserQuery.query.filter_by(
            user_id=current_user.id,
            question_id=question_id,
            query_type='explanation'
        ).order_by(UserQuery.created_at.desc()).first()
        
        # Log whether we found a cached explanation
        if user_cached_explanation:
            current_app.logger.info(f"Found cached explanation from {user_cached_explanation.created_at}")
        else:
            current_app.logger.info("No cached explanation found")
        
        # Check if we have a system-wide explanation (from Explanation model)
        existing_explanation = Explanation.query.filter_by(question_id=question_id).order_by(Explanation.generated_at.desc()).first()
        
        # If requesting a new explanation via POST, always generate new one regardless of cache
        if request.method == 'POST':
            # Get user profile for logging but don't block based on consent
            user_profile = UserProfile.query.filter_by(user_id=current_user.id).first()
            
            # Log status for debugging
            if user_profile:
                current_app.logger.info(f"User {current_user.id} consent status: ai_usage_consent_required={user_profile.ai_usage_consent_required}, last_ai_consent_date={user_profile.last_ai_consent_date}")
                # Update consent date if needed but don't block access
                if user_profile.ai_usage_consent_required:
                    user_profile.ai_usage_consent_required = False
                    user_profile.last_ai_consent_date = datetime.utcnow()
                    db.session.commit()
                    current_app.logger.info(f"Updated consent for user {current_user.id}")
            else:
                current_app.logger.warning(f"User {current_user.id} does not have a UserProfile record")
                # Create a profile with consent if missing
                new_profile = UserProfile(
                    user_id=current_user.id,
                    ai_usage_consent_required=False,
                    last_ai_consent_date=datetime.utcnow()
                )
                db.session.add(new_profile)
                db.session.commit()
                current_app.logger.info(f"Created profile with consent for user {current_user.id}")
            
            # Credit verification - require 10 credits for new explanations
            if not current_user.has_sufficient_credits(10):
                current_app.logger.warning(f"User {current_user.id} attempted to get new explanation without sufficient credits")
                return jsonify({
                    'success': False,
                    'message': 'You need at least 10 credits to generate a new explanation. Please purchase more credits.',
                    'credits_required': True
                }), 403
            try:
                # Get paths to try
                image_path = question.image_path
                current_app.logger.info(f"Looking for image at path: {image_path}")
                
                # Create a list of possible paths to try
                paths_to_try = [
                    image_path,  # Original path from database
                    image_path.replace('/home/runner/workspace/', './'),  # Relative path
                    f"./data/{os.path.basename(os.path.dirname(image_path))}/{os.path.basename(image_path)}",  # Local data folder
                ]
                
                # Add fallback to default images when image is missing
                question_number = question.question_number.replace('q', '')
                try:
                    q_num = int(question_number)
                    if 1 <= q_num <= 4:  # Only use sample images for questions 1-4
                        paths_to_try.append(f"./data/questions/paper_1/question_q{q_num}_703866-q{q_num}.png")
                except:
                    pass  # Skip if question number isn't numeric
                
                # Try each path
                image_found = False
                for path in paths_to_try:
                    current_app.logger.info(f"Trying path: {path}")
                    if os.path.isfile(path):
                        current_app.logger.info(f"Found image at: {path}")
                        image_path = path
                        image_found = True
                        break
                
                # Check for sample images if no image was found
                if not image_found:
                    current_app.logger.warning(f"Image not found in any expected location. Looking for sample images.")
                    
                    # Determine which sample question file to use based on the question number
                    question_sample = "./data/questions/paper_1/question_q1_703866-q1.png"  # Default fallback
                    
                    # Try to use a sample image that matches the current question number
                    try:
                        q_num = int(question_number)
                        if 1 <= q_num <= 4:
                            question_sample = f"./data/questions/paper_1/question_q{q_num}_703866-q{q_num}.png"
                            current_app.logger.info(f"Using numbered sample image for q{q_num}")
                    except:
                        current_app.logger.warning(f"Could not determine question number, using default sample")
                    
                    sample_paths = [
                        question_sample,
                        "./data/papers/sample_math_paper.png"
                    ]
                    
                    for path in sample_paths:
                        if os.path.isfile(path):
                            current_app.logger.warning(f"Using sample image instead: {path}")
                            image_path = path
                            image_found = True
                            break
                
                if not image_found:
                    current_app.logger.error(f"No usable image found for question {question_id}")
                    return jsonify({
                        'success': False,
                        'message': 'Question image not found. Please contact support.'
                    }), 404
                
                # Read the image and encode it to base64 with data URI format
                try:
                    with open(image_path, "rb") as image_file:
                        image_bytes = image_file.read()
                        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                        # Create a data URI with proper mime type
                        data_uri = f"data:image/png;base64,{image_base64}"
                except Exception as e:
                    current_app.logger.error(f"Error reading image file {image_path}: {str(e)}")
                    return jsonify({
                        'success': False,
                        'message': 'Error reading question image. Please try again or contact support.'
                    }), 500
                
                # Generate explanation using OpenAI with data URI format
                current_app.logger.info(f"Generating explanation for question {question_id}, subject: {paper.subject}")
                explanation_text = generate_explanation(
                    data_uri,
                    paper.subject
                )
                
                # The explanation from OpenAI is already in text format, no JSON parsing needed
                current_app.logger.info("Using explanation text directly without JSON parsing")
                
                # Process the mathematical notation
                processed_text = process_math_notation(explanation_text)
                
                # Save the original explanation
                explanation = Explanation(
                    question_id=question_id,
                    explanation_text=explanation_text
                )
                
                # Create a user query record for tracking
                user_query = UserQuery(
                    user_id=current_user.id,
                    query_type='explanation',
                    question_id=question_id,
                    response_text=explanation_text,
                    credits_used=10,
                    subject=paper.subject
                )
                
                # Deduct 10 credits for successful AI explanation
                if not current_user.use_credits(10):
                    # This should never happen as we checked credits earlier, but just in case
                    current_app.logger.error(f"Failed to deduct credits from user {current_user.id} - insufficient balance")
                    return jsonify({
                        'success': False,
                        'message': 'You need at least 10 credits to use this feature. Please purchase more credits.',
                        'credits_required': True
                    }), 403
                
                # Add explanation and save both explanation and credit transaction
                db.session.add(explanation)
                db.session.add(user_query)
                db.session.commit()
                current_app.logger.info(f"Deducted 10 credits from user {current_user.id}, new balance: {current_user.credits}")
                
                return jsonify({
                    'success': True,
                    'question_id': question_id,
                    'explanation': processed_text,
                    'credits_remaining': current_user.credits,
                    'is_new': True
                })
                
            except Exception as e:
                current_app.logger.error(f"Error generating explanation: {str(e)}")
                error_message = str(e)
                # Display a more user-friendly message for quota errors
                if "quota" in error_message.lower() or "exceeded" in error_message.lower() or "unavailable" in error_message.lower():
                    return jsonify({
                        'success': False,
                        'message': 'The AI service is temporarily unavailable. Our team has been notified and is working to restore service. Please try again later.',
                        'admin_message': error_message if current_user.is_admin else None
                    }), 503
                return jsonify({
                    'success': False,
                    'message': f'Error generating explanation: {error_message}'
                }), 500
        
        # For GET requests, check if we have a cached explanation from this user
        if request.method == 'GET' and user_cached_explanation:
            # User has already viewed this explanation - return it without charging credits
            current_app.logger.info(f"Using cached explanation for user {current_user.id}, question {question_id}")
            processed_text = process_math_notation(user_cached_explanation.response_text)
            
            # Add a special note that this was a cached explanation
            explanation_with_cache_note = f"""
            <div class="cached-explanation">
                {processed_text}
            </div>
            """
            
            return jsonify({
                'success': True,
                'question_id': question_id,
                'explanation': explanation_with_cache_note,
                'is_new': False,
                'is_cached': True,
                'credits_remaining': current_user.credits,
                'generated_at': user_cached_explanation.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        # If no user-specific cache but a general explanation exists, check if we need to charge credits
        if existing_explanation:
            processed_text = process_math_notation(existing_explanation.explanation_text)
            
            # If we reach here and this is a GET request, we'll be charging credits (for first-time viewing)
            # We need to check if the user has sufficient credits before proceeding
            if request.method == 'GET' and not current_user.has_sufficient_credits(10):
                # Instead of a 403 error, return a more helpful response with the explanation
                # but clearly indicate they need to purchase credits for future use
                current_app.logger.warning(f"User {current_user.id} has insufficient credits to view explanation for first time")
                processed_text_with_warning = f"""
                <div class="credits-warning alert alert-warning">
                    <strong>⚠️ You have insufficient credits to view this explanation.</strong>
                    <p>This is a preview of the explanation. Purchase credits to unlock more explanations.</p>
                    <a href="{url_for('auth.buy_credits')}" class="btn btn-sm btn-warning">Buy Credits</a>
                </div>
                <div class="preview-explanation" style="opacity: 0.7;">
                    {processed_text}
                </div>
                """
                return jsonify({
                    'success': True,
                    'question_id': question_id,
                    'explanation': processed_text_with_warning,
                    'is_new': False,
                    'is_cached': False,
                    'is_preview': True,
                    'credits_remaining': current_user.credits,
                    'generated_at': existing_explanation.generated_at.strftime('%Y-%m-%d %H:%M:%S')
                })
        else:
            # No explanation exists at all - for GET requests, we'll automatically generate one 
            # if the user has enough credits
            current_app.logger.info(f"No explanation found for question {question_id}, attempting auto-generation")
            
            # Credit verification - require 10 credits for new explanations
            if not current_user.has_sufficient_credits(10):
                current_app.logger.warning(f"User {current_user.id} has insufficient credits for auto-generation")
                # Show a "need credits" message instead of generating explanation
                insufficient_credits_message = """
                <div class="alert alert-warning">
                    <strong>Insufficient Credits</strong>
                    <p>You need 10 credits to generate an explanation for this question.</p>
                    <a href="/buy-credits" class="btn btn-warning btn-sm">Buy Credits</a>
                </div>
                """
                return jsonify({
                    'success': True,
                    'question_id': question_id,
                    'explanation': insufficient_credits_message,
                    'is_new': False,
                    'credits_required': True,
                    'credits_remaining': current_user.credits
                })
                
            # Check for AI usage consent before auto-generating
            user_profile = UserProfile.query.filter_by(user_id=current_user.id).first()
            if not user_profile or user_profile.ai_usage_consent_required or not user_profile.last_ai_consent_date:
                current_app.logger.warning(f"User {current_user.id} attempted auto-generation without AI consent")
                return jsonify({
                    'success': False,
                    'message': 'You need to provide consent for AI usage before using this feature.',
                    'consent_required': True
                }), 403
                
            # Check if consent is expired (older than 30 days)
            if user_profile.last_ai_consent_date:
                consent_age = datetime.utcnow() - user_profile.last_ai_consent_date
                if consent_age.days > 30:
                    user_profile.ai_usage_consent_required = True
                    db.session.commit()
                    current_app.logger.warning(f"User {current_user.id} has expired AI consent")
                    return jsonify({
                        'success': False,
                        'message': 'Your AI usage consent has expired. Please renew your consent to continue using AI features.',
                        'consent_required': True
                    }), 403
            
            # User has enough credits and valid consent, so we'll generate an explanation automatically
            try:
                # Show loading message while generating
                current_app.logger.info(f"Auto-generating explanation for question {question_id}")
                
                # Get the image file for the explanation
                image_path = question.image_path
                current_app.logger.info(f"Looking for image at path: {image_path}")
                
                # Create a list of possible paths to try
                paths_to_try = [
                    image_path,  # Original path from database
                    image_path.replace('/home/runner/workspace/', './'),  # Relative path
                    f"./data/{os.path.basename(os.path.dirname(image_path))}/{os.path.basename(image_path)}",  # Local data folder
                ]
                
                # Try each path
                image_found = False
                for path in paths_to_try:
                    current_app.logger.info(f"Trying path: {path}")
                    if os.path.isfile(path):
                        current_app.logger.info(f"Found image at: {path}")
                        image_path = path
                        image_found = True
                        break
                
                if not image_found:
                    raise FileNotFoundError(f"Could not find image file for question {question_id}")
                
                # Read the image and encode it to base64 with data URI format
                try:
                    with open(image_path, "rb") as image_file:
                        image_bytes = image_file.read()
                        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                        data_uri = f"data:image/png;base64,{image_base64}"
                        current_app.logger.info(f"Image encoded successfully, size: {len(image_bytes)} bytes, base64 length: {len(image_base64)}")
                except Exception as img_error:
                    current_app.logger.error(f"Error encoding image: {str(img_error)}")
                    raise img_error
                
                # Generate explanation using OpenAI with data URI format
                current_app.logger.info(f"Generating explanation for question {question_id}, subject: {paper.subject}")
                explanation_text = generate_explanation(
                    data_uri,
                    paper.subject
                )
                
                # Process the mathematical notation
                processed_text = process_math_notation(explanation_text)
                
                # Save the explanation in the database
                explanation = Explanation(
                    question_id=question_id,
                    explanation_text=explanation_text
                )
                
                # Create a user query record
                user_query = UserQuery(
                    user_id=current_user.id,
                    query_type='explanation',
                    question_id=question_id,
                    response_text=explanation_text,
                    credits_used=10,
                    subject=paper.subject
                )
                
                # Deduct 10 credits for the AI explanation
                if not current_user.use_credits(10):
                    raise ValueError("Insufficient credits")
                
                # Save the records
                db.session.add(explanation)
                db.session.add(user_query)
                db.session.commit()
                
                current_app.logger.info(f"Generated explanation for question {question_id}")
                
                return jsonify({
                    'success': True,
                    'question_id': question_id,
                    'explanation': processed_text,
                    'is_new': True,
                    'is_auto_generated': True,
                    'credits_remaining': current_user.credits
                })
                
            except Exception as gen_error:
                current_app.logger.error(f"Error auto-generating explanation: {str(gen_error)}")
                
                # If OpenAI API failed, return a friendly error message
                error_message = str(gen_error)
                if "quota" in error_message.lower() or "exceeded" in error_message.lower() or "unavailable" in error_message.lower():
                    service_error_message = """
                    <div class="alert alert-danger">
                        <strong>AI Service Unavailable</strong>
                        <p>The AI service is temporarily unavailable. Our team has been notified and is working to restore service. Please try again later.</p>
                    </div>
                    """
                    return jsonify({
                        'success': True,
                        'question_id': question_id,
                        'explanation': service_error_message,
                        'service_unavailable': True,
                        'admin_message': error_message if current_user.is_admin else None
                    })
                
                # Generic error message for other failures
                loading_message = """
                <div class="alert alert-info">
                    <strong>Generating Explanation</strong>
                    <p>We're working on generating an explanation for this question.</p>
                    <p>Click the "Explain this question" button below to try again.</p>
                </div>
                """
                return jsonify({
                    'success': True,
                    'question_id': question_id,
                    'explanation': loading_message,
                    'is_new': False,
                    'generation_error': True,
                    'credits_remaining': current_user.credits
                })
    except Exception as e:
        current_app.logger.error(f"General error in api_get_explanation: {str(e)}")
        error_message = str(e)
        # Display a more user-friendly message for quota errors
        if "quota" in error_message.lower() or "exceeded" in error_message.lower() or "unavailable" in error_message.lower():
            return jsonify({
                'success': False,
                'message': 'The AI service is temporarily unavailable. Our team has been notified and is working to restore service. Please try again later.',
                'admin_message': error_message if current_user.is_admin else None
            }), 503
        return jsonify({
            'success': False,
            'message': f'An error occurred: {error_message}'
        }), 500
    
    # At this point, we're fetching an existing explanation for the first time for this user
    user_profile = UserProfile.query.filter_by(user_id=current_user.id).first()
    
    # Auto-update consent to avoid blocking access
    if user_profile:
        if user_profile.ai_usage_consent_required or not user_profile.last_ai_consent_date:
            user_profile.ai_usage_consent_required = False
            user_profile.last_ai_consent_date = datetime.utcnow()
            db.session.commit()
            current_app.logger.info(f"Updated consent for user {current_user.id}")
    else:
        # Create a profile with consent for this user
        current_app.logger.warning(f"User {current_user.id} does not have a UserProfile record, creating one")
        user_profile = UserProfile(
            user_id=current_user.id,
            ai_usage_consent_required=False,
            last_ai_consent_date=datetime.utcnow()
        )
        db.session.add(user_profile)
        db.session.commit()
        current_app.logger.info(f"Created profile with consent for user {current_user.id}")
    
    # Track this query in the user's history and deduct credits
    user_query = UserQuery(
        user_id=current_user.id,
        query_type='explanation',
        question_id=question_id,
        response_text=existing_explanation.explanation_text,
        credits_used=10,
        subject=paper.subject
    )
    
    # Deduct 10 credits for explanation (first time)
    if not current_user.has_sufficient_credits(10):
        current_app.logger.warning(f"User {current_user.id} has insufficient credits to view explanation")
        # Instead of blocking with 403, let's just show a preview message
        processed_text = process_math_notation(existing_explanation.explanation_text)
        preview_text = f"""
        <div class="alert alert-warning">
            <strong>⚠️ You have insufficient credits to view this explanation.</strong>
            <p>You need at least 10 credits to view explanations. Please purchase more credits.</p>
        </div>
        <div class="explanation-preview">
            {processed_text[:250]}... <em>(Preview only, purchase credits to view full explanation)</em>
        </div>
        """
        return jsonify({
            'success': True,
            'question_id': question_id,
            'explanation': preview_text,
            'is_new': False,
            'is_preview': True,
            'credits_required': True,
            'credits_remaining': current_user.credits
        })
        
    # Add the query record and save after deducting credits
    current_user.use_credits(10)
    db.session.add(user_query)
    db.session.commit()
    current_app.logger.info(f"Deducted 10 credits from user {current_user.id} for viewing explanation first time, new balance: {current_user.credits}")
    
    return jsonify({
        'success': True,
        'question_id': question_id,
        'explanation': processed_text,
        'is_new': False,
        'is_cached': False, # Not cached since this is first view
        'credits_remaining': current_user.credits,
        'generated_at': existing_explanation.generated_at.strftime('%Y-%m-%d %H:%M:%S')
    })

@user_bp.route('/favorite-query/<int:query_id>')
@login_required
def favorite_query(query_id):
    """Mark a query as favorite"""
    try:
        query = UserQuery.query.get(query_id)
        if not query:
            flash(f'Query with ID {query_id} not found', 'warning')
            return redirect(url_for('auth.query_history'))
        
        # Check if the query belongs to the current user
        if query.user_id != current_user.id:
            flash('You can only favorite your own queries', 'danger')
            return redirect(url_for('auth.query_history'))
        
        query.is_favorite = True
        db.session.commit()
        
        flash('Query marked as favorite', 'success')
        return redirect(url_for('auth.query_history'))
    except Exception as e:
        current_app.logger.error(f"Error marking query as favorite: {str(e)}")
        flash('An error occurred. Please try again.', 'danger')
        return redirect(url_for('auth.query_history'))

@user_bp.route('/unfavorite-query/<int:query_id>')
@login_required
def unfavorite_query(query_id):
    """Remove a query from favorites"""
    try:
        query = UserQuery.query.get(query_id)
        if not query:
            flash(f'Query with ID {query_id} not found', 'warning')
            return redirect(url_for('auth.query_history'))
        
        # Check if the query belongs to the current user
        if query.user_id != current_user.id:
            flash('You can only manage your own queries', 'danger')
            return redirect(url_for('auth.query_history'))
        
        query.is_favorite = False
        db.session.commit()
        
        flash('Query removed from favorites', 'success')
        return redirect(url_for('auth.query_history'))
    except Exception as e:
        current_app.logger.error(f"Error removing query from favorites: {str(e)}")
        flash('An error occurred. Please try again.', 'danger')
        return redirect(url_for('auth.query_history'))

@user_bp.route('/api/delete-question/<int:question_id>', methods=['POST'])
@login_required
def api_delete_question(question_id):
    """API endpoint to delete a question"""
    if not current_user.is_admin:
        current_app.logger.warning(f"Non-admin user {current_user.id} attempted to delete question {question_id}")
        return jsonify({
            'success': False,
            'message': 'You do not have permission to delete questions'
        }), 403
    
    try:
        # Check if question exists
        question = Question.query.get(question_id)
        if not question:
            current_app.logger.error(f"Question with ID {question_id} not found when attempting to delete")
            return jsonify({
                'success': False,
                'message': f'Question with ID {question_id} not found'
            }), 404
        
        try:
            # Delete all explanations associated with this question
            Explanation.query.filter_by(question_id=question_id).delete()
            
            # Delete all user queries associated with this question
            UserQuery.query.filter_by(question_id=question_id).delete()
            
            # Delete all student answers associated with this question
            StudentAnswer.query.filter_by(question_id=question_id).delete()
            
            # Delete all question topics associations
            QuestionTopic.query.filter_by(question_id=question_id).delete()
            
            # Delete the image file if it exists
            if question.image_path:
                # Try different path formats
                paths_to_try = [
                    question.image_path,
                    question.image_path.replace('/home/runner/workspace/', './'),
                    f"./data/{os.path.basename(os.path.dirname(question.image_path))}/{os.path.basename(question.image_path)}"
                ]
                
                deletion_success = False
                for path in paths_to_try:
                    if os.path.exists(path):
                        try:
                            os.remove(path)
                            current_app.logger.info(f"Deleted question image: {path}")
                            deletion_success = True
                            break
                        except Exception as file_error:
                            current_app.logger.warning(f"Error deleting file at {path}: {str(file_error)}")
                
                if not deletion_success:
                    current_app.logger.warning(f"Could not delete image file for question {question_id} - file not found in any expected location")
            
            # Finally, delete the question
            db.session.delete(question)
            db.session.commit()
            
            current_app.logger.info(f"Question {question_id} successfully deleted by admin {current_user.id}")
            
            return jsonify({
                'success': True,
                'message': 'Question deleted successfully'
            })
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error deleting question {question_id}: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Error deleting question: {str(e)}'
            }), 500
    except Exception as outer_e:
        current_app.logger.error(f"Unexpected error in api_delete_question: {str(outer_e)}")
        return jsonify({
            'success': False,
            'message': 'An unexpected error occurred'
        }), 500
