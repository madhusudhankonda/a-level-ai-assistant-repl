from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from datetime import datetime
import os
import uuid
from werkzeug.utils import secure_filename
from models import db, QuestionPaper, Question, Subject, ExamBoard, PaperCategory, QuestionTopic, Explanation, UserQuery, StudentAnswer, UserFeedback
from flask_login import login_required, current_user
from generate_mock_questions import generate_mock_paper

# Create admin blueprint
admin_bp = Blueprint('admin', __name__, template_folder='templates/admin')

# Add template context processors
@admin_bp.context_processor
def inject_current_year():
    return {'current_year': datetime.now().year}

def get_data_folder():
    """Get or create the data folder for storing papers and questions"""
    data_dir = os.path.join(os.getcwd(), 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return data_dir

@admin_bp.route('/')
@login_required
def index():
    """Admin dashboard showing papers"""
    # Verify user is an admin
    if not current_user.is_admin:
        flash('You do not have permission to access the admin area.', 'danger')
        return redirect(url_for('user.index'))
    
    # Get sort parameter (default to exam_period if not specified)
    sort_by = request.args.get('sort', 'exam_period')
    
    # Order papers based on sort parameter
    if sort_by == 'exam_period':
        # Order by exam_period descending (most recent first)
        papers = QuestionPaper.query.order_by(QuestionPaper.exam_period.desc()).all()
    elif sort_by == 'title':
        papers = QuestionPaper.query.order_by(QuestionPaper.title).all()
    elif sort_by == 'subject':
        papers = QuestionPaper.query.order_by(QuestionPaper.subject).all()
    elif sort_by == 'created':
        papers = QuestionPaper.query.order_by(QuestionPaper.created_at.desc()).all()
    else:
        # Default to ordering by exam_period
        papers = QuestionPaper.query.order_by(QuestionPaper.exam_period.desc()).all()
    
    subjects = Subject.query.all()
    
    # Get user feedback count
    user_feedback = UserFeedback.query.all()
    
    return render_template('admin/index.html', 
                          papers=papers, 
                          subjects=subjects, 
                          user_feedback=user_feedback,
                          current_sort=sort_by)

@admin_bp.route('/paper/create', methods=['GET', 'POST'])
@login_required
def create_paper():
    """Create a new question paper"""
    # Verify user is an admin
    if not current_user.is_admin:
        flash('You do not have permission to access the admin area.', 'danger')
        return redirect(url_for('user.index'))
        
    # Get subjects, boards, and categories for form
    subjects = Subject.query.all()
    
    if request.method == 'POST':
        title = request.form.get('title')
        subject_id = request.form.get('subject')
        board_id = request.form.get('board_id')
        category_id = request.form.get('category_id')
        exam_period = request.form.get('exam_period', 'Unknown')
        paper_type = request.form.get('paper_type', 'QP')
        description = request.form.get('description', '')
        
        # Debug print to see all form data
        current_app.logger.info(f"Form data: {request.form}")
        current_app.logger.info(f"Category ID from form: '{category_id}'")
        
        if not title or not subject_id:
            flash('Title and subject are required', 'danger')
            return redirect(url_for('admin.create_paper'))
        
        # Get subject name from subject_id
        subject = Subject.query.get(subject_id)
        if not subject:
            flash('Invalid subject selected', 'danger')
            return redirect(url_for('admin.create_paper'))
            
        subject_name = subject.name
        
        current_app.logger.info(f"Creating paper: {title}, Subject ID: {subject_id}, Subject Name: {subject_name}, Board ID: {board_id}, Category ID: {category_id}")
        
        # Create new paper in the database
        paper = QuestionPaper(
            title=title,
            subject=subject_name,
            exam_period=exam_period,
            paper_type=paper_type,
            description=description
        )
        
        # Set category_id if provided
        if category_id and category_id.strip():
            try:
                # Convert to integer
                category_id_int = int(category_id)
                if category_id_int > 0:  # Ensure it's a positive integer
                    paper.category_id = category_id_int
                    current_app.logger.info(f"Paper assigned to category ID: {category_id_int}")
                else:
                    flash('Please select a valid category for the paper', 'danger')
                    return redirect(url_for('admin.create_paper'))
            except ValueError:
                current_app.logger.warning(f"Invalid category_id format: {category_id}")
                flash('Invalid category format. Please select a proper category.', 'danger')
                return redirect(url_for('admin.create_paper'))
        else:
            current_app.logger.warning("No category ID provided")
            flash('Please select a category for the paper', 'danger')
            return redirect(url_for('admin.create_paper'))
        
        db.session.add(paper)
        db.session.commit()
        
        # Create folder for storing questions for this paper
        paper_dir = os.path.join(get_data_folder(), f'paper_{paper.id}')
        if not os.path.exists(paper_dir):
            os.makedirs(paper_dir)
        
        flash(f'Paper "{title}" created successfully', 'success')
        return redirect(url_for('admin.manage_questions', paper_id=paper.id))
    
    return render_template('admin/create_paper.html', subjects=subjects)

@admin_bp.route('/api/get-boards/<int:subject_id>')
@login_required
def get_boards(subject_id):
    """API endpoint to get exam boards for a subject"""
    current_app.logger.info(f"Getting boards for subject ID: {subject_id}")
    
    if not current_user.is_admin:
        current_app.logger.warning(f"Unauthorized access attempt to get_boards by user {current_user.id}")
        return jsonify({'error': 'Not authorized'}), 403
    
    try:
        boards = ExamBoard.query.filter_by(subject_id=subject_id).all()
        current_app.logger.info(f"Found {len(boards)} boards for subject ID {subject_id}")
        board_list = [{'id': board.id, 'name': board.name} for board in boards]
        return jsonify(board_list)
    except Exception as e:
        current_app.logger.error(f"Error getting boards for subject {subject_id}: {str(e)}")
        return jsonify({'error': f'Error loading boards: {str(e)}'}), 500

# Add a non-authenticated endpoint for the admin form (for AJAX usage)
@admin_bp.route('/get-form-data/boards/<int:subject_id>')
def get_form_boards(subject_id):
    """Public API endpoint to get exam boards for the admin form"""
    current_app.logger.info(f"Getting form boards for subject ID: {subject_id}")
    
    # Simple validation to ensure we're dealing with a valid subject ID
    if not isinstance(subject_id, int) or subject_id <= 0:
        return jsonify({'error': 'Invalid subject ID'}), 400
    
    try:
        # Fetch boards for this subject
        boards = ExamBoard.query.filter_by(subject_id=subject_id).all()
        current_app.logger.info(f"Found {len(boards)} boards for subject ID {subject_id}")
        
        # Format the response
        board_list = [{'id': board.id, 'name': board.name} for board in boards]
        return jsonify(board_list)
    except Exception as e:
        current_app.logger.error(f"Error getting form boards for subject {subject_id}: {str(e)}")
        return jsonify({'error': f'Error loading boards: {str(e)}'}), 500

@admin_bp.route('/api/get-categories/<int:board_id>')
@login_required
def get_categories(board_id):
    """API endpoint to get paper categories for an exam board"""
    current_app.logger.info(f"Getting categories for board ID: {board_id}")
    
    if not current_user.is_admin:
        current_app.logger.warning(f"Unauthorized access attempt to get_categories by user {current_user.id}")
        return jsonify({'error': 'Not authorized'}), 403
    
    try:
        categories = PaperCategory.query.filter_by(board_id=board_id).all()
        current_app.logger.info(f"Found {len(categories)} categories for board ID {board_id}")
        category_list = [{'id': category.id, 'name': category.name} for category in categories]
        return jsonify(category_list)
    except Exception as e:
        current_app.logger.error(f"Error getting categories for board {board_id}: {str(e)}")
        return jsonify({'error': f'Error loading categories: {str(e)}'}), 500

# Add a non-authenticated endpoint for the admin form (for AJAX usage)
@admin_bp.route('/get-form-data/categories/<int:board_id>')
def get_form_categories(board_id):
    """Public API endpoint to get paper categories for the admin form"""
    current_app.logger.info(f"Getting form categories for board ID: {board_id}")
    
    # Simple validation to ensure we're dealing with a valid board ID
    if not isinstance(board_id, int) or board_id <= 0:
        return jsonify({'error': 'Invalid board ID'}), 400
    
    try:
        # Fetch categories for this board
        categories = PaperCategory.query.filter_by(board_id=board_id).all()
        current_app.logger.info(f"Found {len(categories)} categories for board ID {board_id}")
        
        # Format the response
        category_list = [{'id': category.id, 'name': category.name} for category in categories]
        return jsonify(category_list)
    except Exception as e:
        current_app.logger.error(f"Error getting form categories for board {board_id}: {str(e)}")
        return jsonify({'error': f'Error loading categories: {str(e)}'}), 500

@admin_bp.route('/paper/<int:paper_id>/questions')
@login_required
def manage_questions(paper_id):
    """Manage questions for a paper"""
    # Verify user is an admin
    if not current_user.is_admin:
        flash('You do not have permission to access the admin area.', 'danger')
        return redirect(url_for('user.index'))
        
    paper = QuestionPaper.query.get_or_404(paper_id)
    questions = Question.query.filter_by(paper_id=paper_id).order_by(Question.question_number).all()
    
    # Get all papers for mock generation dropdown
    all_papers = QuestionPaper.query.order_by(QuestionPaper.title).all()
    
    return render_template('admin/manage_questions.html', paper=paper, questions=questions, all_papers=all_papers)

@admin_bp.route('/paper/<int:paper_id>/generate-mock', methods=['GET', 'POST'])
@login_required
def generate_mock(paper_id):
    """Generate mock questions based on an existing paper"""
    # Verify user is an admin
    if not current_user.is_admin:
        flash('You do not have permission to access the admin area.', 'danger')
        return redirect(url_for('user.index'))
    
    source_paper = QuestionPaper.query.get_or_404(paper_id)
    
    # Get all papers for marking scheme source dropdown
    all_papers = QuestionPaper.query.filter(QuestionPaper.id != paper_id).order_by(QuestionPaper.title).all()
    
    # Find papers with questions to show as dropdown options
    papers_with_questions = []
    for p in QuestionPaper.query.order_by(QuestionPaper.title).all():
        question_count = Question.query.filter_by(paper_id=p.id).count()
        if question_count > 0:
            papers_with_questions.append((p, question_count))
    
    # Get the question count for the current paper to display a warning if needed
    current_paper_question_count = Question.query.filter_by(paper_id=paper_id).count()
    
    if request.method == 'POST':
        mock_paper_name = request.form.get('mock_paper_name')
        num_questions = request.form.get('num_questions', '5')
        transform_level = request.form.get('transform_level', '2')
        include_mark_scheme = request.form.get('include_mark_scheme') == 'on'
        source_mark_scheme_paper_id = request.form.get('source_mark_scheme_paper_id')
        
        # Validate inputs
        if not mock_paper_name:
            flash('Mock paper name is required', 'danger')
            return redirect(url_for('admin.generate_mock', paper_id=paper_id))
        
        try:
            num_questions = int(num_questions)
            if num_questions < 1 or num_questions > 15:
                flash('Number of questions must be between 1 and 15', 'danger')
                return redirect(url_for('admin.generate_mock', paper_id=paper_id))
        except ValueError:
            flash('Invalid number of questions', 'danger')
            return redirect(url_for('admin.generate_mock', paper_id=paper_id))
        
        try:
            transform_level = int(transform_level)
            if transform_level < 1 or transform_level > 5:
                flash('Transform level must be between 1 and 5', 'danger')
                return redirect(url_for('admin.generate_mock', paper_id=paper_id))
        except ValueError:
            flash('Invalid transform level', 'danger')
            return redirect(url_for('admin.generate_mock', paper_id=paper_id))
        
        # Convert source_mark_scheme_paper_id to int if provided
        ms_paper_id = None
        if source_mark_scheme_paper_id and source_mark_scheme_paper_id.strip():
            try:
                ms_paper_id = int(source_mark_scheme_paper_id)
            except ValueError:
                flash('Invalid marking scheme paper selected', 'warning')
                # Continue without marking scheme
        
        # Get the current paper's question count
        current_question_count = Question.query.filter_by(paper_id=paper_id).count()
        
        # Check if the paper has questions before attempting to generate
        if current_question_count == 0:
            current_app.logger.error(f"Cannot generate mock paper: No questions found in paper ID {paper_id}")
            flash(f"Cannot generate mock questions: The source paper (ID: {paper_id}) doesn't have any questions. Please first add questions to this paper or select a different paper with existing questions.", 'danger')
            return redirect(url_for('admin.manage_questions', paper_id=paper_id))

        # Generate the mock paper
        current_app.logger.info(f"Generating mock paper based on paper ID {paper_id} with {current_question_count} questions")
        result = generate_mock_paper(
            source_paper_id=paper_id,
            mock_paper_name=mock_paper_name,
            num_questions=num_questions,
            transform_level=transform_level,
            include_mark_scheme=include_mark_scheme,
            source_mark_scheme_paper_id=ms_paper_id
        )
        
        if result['success']:
            current_app.logger.info(f"Successfully generated mock paper: {result}")
            flash(f"Successfully created mock paper '{mock_paper_name}' with {result['questions_created']} questions and {result['mark_schemes_created']} mark schemes", 'success')
            return redirect(url_for('admin.manage_questions', paper_id=result['paper_id']))
        else:
            error_message = result['error']
            current_app.logger.error(f"Error generating mock paper: {error_message}")
            
            # Provide more helpful error messages
            if "No source questions found" in error_message:
                flash(f"Error: {error_message} Please add questions to the paper first, or select a different paper that already has questions.", 'danger')
            else:
                flash(f"Error generating mock paper: {error_message}", 'danger')
                
            return redirect(url_for('admin.generate_mock', paper_id=paper_id))
    
    return render_template('admin/generate_mock.html', 
                       paper=source_paper, 
                       all_papers=all_papers,
                       papers_with_questions=papers_with_questions,
                       current_paper_question_count=current_paper_question_count)

@admin_bp.route('/paper/<int:paper_id>/question/add', methods=['GET', 'POST'])
@login_required
def add_question(paper_id):
    """Add a question to a paper"""
    # Verify user is an admin
    if not current_user.is_admin:
        flash('You do not have permission to access the admin area.', 'danger')
        return redirect(url_for('user.index'))
        
    paper = QuestionPaper.query.get_or_404(paper_id)
    
    if request.method == 'POST':
        question_number = request.form.get('question_number')
        question_image = request.files.get('question_image')
        difficulty_level = request.form.get('difficulty_level')
        marks = request.form.get('marks')
        
        if not question_number or not question_image:
            flash('Question number and image are required', 'danger')
            return redirect(url_for('admin.add_question', paper_id=paper_id))
        
        # Save the question image
        if question_image and question_image.filename:
            if not allowed_file(question_image.filename):
                flash('Invalid file type. Only PNG, JPG, and GIF are allowed.', 'danger')
                return redirect(url_for('admin.add_question', paper_id=paper_id))
                
            # Create paper directory if it doesn't exist
            paper_dir = os.path.join(get_data_folder(), f'paper_{paper_id}')
            if not os.path.exists(paper_dir):
                os.makedirs(paper_dir)
                current_app.logger.info(f"Created directory: {paper_dir}")
            
            # Generate a unique filename
            filename = f"q{secure_filename(question_number)}_{uuid.uuid4().hex}.png"
            image_path = os.path.join(paper_dir, filename)
            
            # Log the attempt to save
            current_app.logger.info(f"Attempting to save image to: {image_path}")
            
            # Save the image
            try:
                question_image.save(image_path)
                current_app.logger.info(f"Image saved successfully to: {image_path}")
                
                # Verify the file exists after saving
                if os.path.exists(image_path):
                    current_app.logger.info(f"Verified: File exists at {image_path}")
                    
                    # Also create a copy with a simple name for easier debugging
                    debug_path = os.path.join(paper_dir, f"q{question_number}_debug.png")
                    try:
                        import shutil
                        shutil.copy(image_path, debug_path)
                        current_app.logger.info(f"Created debug copy at: {debug_path}")
                    except Exception as copy_err:
                        current_app.logger.warning(f"Failed to create debug copy: {str(copy_err)}")
                else:
                    current_app.logger.error(f"Error: File was not found at {image_path} after saving!")
                    flash("Error: Question image was not saved correctly. Please try again.", "danger")
                    return redirect(url_for('admin.add_question', paper_id=paper_id))
            except Exception as save_error:
                current_app.logger.error(f"Failed to save image: {str(save_error)}")
                flash(f"Error saving image: {str(save_error)}", "danger")
                return redirect(url_for('admin.add_question', paper_id=paper_id))
            
            # Generate a URL for the image
            domain = os.environ.get('REPLIT_DEV_DOMAIN') or os.environ.get('REPLIT_DOMAINS', 'localhost:5000').split(',')[0]
            
            # Create question in database
            question = Question(
                question_number=question_number,
                image_path=image_path,
                image_url=f"https://{domain}/user/question-image/",  # Will be updated with ID after creation
                paper_id=paper_id
            )
            
            # Add optional fields if provided
            if difficulty_level:
                try:
                    question.difficulty_level = int(difficulty_level)
                except ValueError:
                    flash('Invalid difficulty level. Please provide a number.', 'warning')
            
            if marks:
                try:
                    question.marks = int(marks)
                except ValueError:
                    flash('Invalid marks value. Please provide a number.', 'warning')
            
            try:
                db.session.add(question)
                db.session.commit()
                
                # Update the image_url with the question ID now that we have it
                question.image_url = f"{question.image_url}{question.id}"
                db.session.commit()
                
                current_app.logger.info(f"Question {question_number} added successfully to paper {paper_id}")
                current_app.logger.info(f"Image URL set to: {question.image_url}")
                
                flash(f'Question {question_number} added successfully', 'success')
                return redirect(url_for('admin.manage_questions', paper_id=paper_id))
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Error adding question: {str(e)}")
                flash(f'Error adding question: {str(e)}', 'danger')
                return redirect(url_for('admin.add_question', paper_id=paper_id))
    
    return render_template('admin/add_question.html', paper=paper)

@admin_bp.route('/paper/<int:paper_id>/auto-generate-questions', methods=['POST'])
@login_required
def auto_generate_questions(paper_id):
    """Auto-generate basic questions for a paper"""
    # Verify user is an admin
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'You do not have permission to access this function.'}), 403
    
    paper = QuestionPaper.query.get_or_404(paper_id)
    current_app.logger.info(f"Auto-generating questions for paper ID {paper_id}: {paper.title}")
    
    try:
        # Run the script as a subprocess to avoid blocking
        import subprocess
        import sys
        result = subprocess.run(
            [sys.executable, 'add_questions_to_paper.py', str(paper_id)],
            capture_output=True,
            text=True,
            timeout=60  # Set a timeout to prevent hanging
        )
        
        if result.returncode == 0:
            # Count how many questions were added
            question_count = Question.query.filter_by(paper_id=paper_id).count()
            return jsonify({
                'success': True, 
                'message': f'Successfully generated questions for this paper. New question count: {question_count}'
            })
        else:
            current_app.logger.error(f"Error generating questions: {result.stderr}")
            return jsonify({
                'success': False, 
                'message': f'Error generating questions: {result.stderr}'
            })
    except Exception as e:
        current_app.logger.error(f"Exception when generating questions: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@admin_bp.route('/question/<int:question_id>/delete', methods=['POST', 'GET'])
@login_required
def delete_question(question_id):
    """Delete a question"""
    # Verify user is an admin
    if not current_user.is_admin:
        flash('You do not have permission to access the admin area.', 'danger')
        return redirect(url_for('user.index'))
    
    # Check if the question exists using get() instead of get_or_404()
    question = Question.query.get(question_id)
    if not question:
        current_app.logger.error(f"Question with ID {question_id} not found for deletion")
        flash(f'Question with ID {question_id} not found.', 'danger')
        return redirect(url_for('admin.index'))
    paper_id = question.paper_id
    
    # Clean up all dependencies first
    if not clean_up_question_dependencies(question_id):
        flash('Error cleaning up question dependencies', 'danger')
        return redirect(url_for('admin.manage_questions', paper_id=paper_id))
    
    # Delete the image file
    try:
        if question.image_path and os.path.exists(question.image_path):
            os.remove(question.image_path)
            current_app.logger.info(f"Deleted question image: {question.image_path}")
    except Exception as e:
        current_app.logger.error(f"Error deleting question image: {str(e)}")
    
    # Delete the question itself
    try:
        db.session.delete(question)
        db.session.commit()
        current_app.logger.info(f"Question {question_id} deleted successfully")
        flash('Question deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting question: {str(e)}")
        flash(f'Error deleting question: {str(e)}', 'danger')
    
    return redirect(url_for('admin.manage_questions', paper_id=paper_id))

@admin_bp.route('/paper/<int:paper_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_paper(paper_id):
    """Edit an existing question paper"""
    # Verify user is an admin
    if not current_user.is_admin:
        flash('You do not have permission to access the admin area.', 'danger')
        return redirect(url_for('user.index'))
    
    # Check if the paper exists using get() instead of get_or_404()
    paper = QuestionPaper.query.get(paper_id)
    if not paper:
        current_app.logger.error(f"Paper with ID {paper_id} not found for editing")
        flash(f'Paper with ID {paper_id} not found.', 'danger')
        return redirect(url_for('admin.index'))
    subjects = Subject.query.all()
    
    # Get the paper's current category and board information
    current_category = None
    current_board = None
    current_subject = None
    
    if paper.category_id:
        current_category = PaperCategory.query.get(paper.category_id)
        if current_category:
            current_board = ExamBoard.query.get(current_category.board_id)
            if current_board:
                current_subject = Subject.query.get(current_board.subject_id)
    
    if request.method == 'POST':
        title = request.form.get('title')
        subject_id = request.form.get('subject')
        board_id = request.form.get('board_id')
        category_id = request.form.get('category_id')
        exam_period = request.form.get('exam_period', 'Unknown')
        paper_type = request.form.get('paper_type', 'QP')
        description = request.form.get('description', '')
        
        # Debug print to see all form data
        current_app.logger.info(f"Form data for edit: {request.form}")
        current_app.logger.info(f"Category ID from edit form: '{category_id}'")
        
        if not title or not subject_id:
            flash('Title and subject are required', 'danger')
            return redirect(url_for('admin.edit_paper', paper_id=paper_id))
        
        # Get subject name from subject_id
        subject = Subject.query.get(subject_id)
        if not subject:
            flash('Invalid subject selected', 'danger')
            return redirect(url_for('admin.edit_paper', paper_id=paper_id))
            
        subject_name = subject.name
        
        current_app.logger.info(f"Updating paper: {title}, Subject ID: {subject_id}, Subject Name: {subject_name}, Board ID: {board_id}, Category ID: {category_id}")
        
        # Update paper in the database
        paper.title = title
        paper.subject = subject_name
        paper.exam_period = exam_period
        paper.paper_type = paper_type
        paper.description = description
        
        # Set category_id if provided
        if category_id and category_id.strip():
            try:
                # Convert to integer
                category_id_int = int(category_id)
                if category_id_int > 0:  # Ensure it's a positive integer
                    paper.category_id = category_id_int
                    current_app.logger.info(f"Paper assigned to category ID: {category_id_int}")
                else:
                    flash('Please select a valid category for the paper', 'danger')
                    return redirect(url_for('admin.edit_paper', paper_id=paper_id))
            except ValueError:
                current_app.logger.warning(f"Invalid category_id format: {category_id}")
                flash('Invalid category format. Please select a proper category.', 'danger')
                return redirect(url_for('admin.edit_paper', paper_id=paper_id))
        else:
            current_app.logger.warning("No category ID provided")
            flash('Please select a category for the paper', 'danger')
            return redirect(url_for('admin.edit_paper', paper_id=paper_id))
        
        try:
            db.session.commit()
            flash(f'Paper "{title}" updated successfully', 'success')
            return redirect(url_for('admin.manage_questions', paper_id=paper.id))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating paper: {str(e)}")
            flash(f'Error updating paper: {str(e)}', 'danger')
            return redirect(url_for('admin.edit_paper', paper_id=paper_id))
    
    return render_template('admin/edit_paper.html', 
                          paper=paper, 
                          subjects=subjects, 
                          current_subject=current_subject,
                          current_board=current_board,
                          current_category=current_category)

@admin_bp.route('/paper/<int:paper_id>/delete', methods=['POST'])
@login_required
def delete_paper(paper_id):
    """Delete a paper and all its questions"""
    # Verify user is an admin
    if not current_user.is_admin:
        flash('You do not have permission to access the admin area.', 'danger')
        return redirect(url_for('user.index'))
    
    # Check if the paper exists using get() instead of get_or_404()
    paper = QuestionPaper.query.get(paper_id)
    if not paper:
        current_app.logger.error(f"Paper with ID {paper_id} not found for deletion")
        flash(f'Paper with ID {paper_id} not found.', 'danger')
        return redirect(url_for('admin.index'))
    paper_title = paper.title
    
    try:
        # Get all questions for this paper
        questions = Question.query.filter_by(paper_id=paper_id).all()
        
        # For each question, clean up dependencies and delete the image file
        for question in questions:
            # Clean up dependencies for each question
            clean_up_question_dependencies(question.id)
            
            # Delete the image file
            try:
                if question.image_path and os.path.exists(question.image_path):
                    os.remove(question.image_path)
                    current_app.logger.info(f"Deleted question image: {question.image_path}")
            except Exception as e:
                current_app.logger.error(f"Error deleting question image for question {question.id}: {str(e)}")
        
        # Delete the paper directory
        paper_dir = os.path.join(get_data_folder(), f'paper_{paper_id}')
        try:
            if os.path.exists(paper_dir):
                import shutil
                shutil.rmtree(paper_dir)
                current_app.logger.info(f"Deleted paper directory: {paper_dir}")
        except Exception as e:
            current_app.logger.error(f"Error deleting paper directory: {str(e)}")
        
        # Delete all questions for this paper
        question_count = Question.query.filter_by(paper_id=paper_id).delete()
        current_app.logger.info(f"Deleted {question_count} questions for paper {paper_id}")
        
        # Delete the paper itself
        db.session.delete(paper)
        db.session.commit()
        
        current_app.logger.info(f"Paper {paper_id} '{paper_title}' deleted successfully")
        flash(f'Paper "{paper_title}" and all its questions deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting paper {paper_id}: {str(e)}")
        flash(f'Error deleting paper: {str(e)}', 'danger')
    
    return redirect(url_for('admin.index'))

def allowed_file(filename):
    """Check if the file extension is allowed"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def clean_up_question_dependencies(question_id):
    """Clean up all dependencies for a question (called before update or delete)"""
    current_app.logger.info(f"Cleaning up dependencies for question {question_id}")
    try:
        # Delete all explanations associated with this question
        Explanation.query.filter_by(question_id=question_id).delete()
        
        # Delete all user queries associated with this question
        UserQuery.query.filter_by(question_id=question_id).delete()
        
        # Delete all student answers associated with this question
        StudentAnswer.query.filter_by(question_id=question_id).delete()
        
        # Delete all question topics associations
        QuestionTopic.query.filter_by(question_id=question_id).delete()
        
        db.session.commit()
        current_app.logger.info(f"Successfully cleaned up dependencies for question {question_id}")
        return True
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error cleaning up dependencies for question {question_id}: {str(e)}")
        return False

@admin_bp.route('/edit-question/<int:question_id>', methods=['GET', 'POST'])
@login_required
def edit_question(question_id):
    """Edit a question"""
    # Verify user is an admin
    if not current_user.is_admin:
        flash('You do not have permission to access the admin area.', 'danger')
        return redirect(url_for('user.index'))
    
    # Check if the question exists using get() instead of get_or_404()
    question = Question.query.get(question_id)
    if not question:
        current_app.logger.error(f"Question with ID {question_id} not found for editing")
        flash(f'Question with ID {question_id} not found.', 'danger')
        return redirect(url_for('admin.index'))
    
    # Check if the related paper exists using get() instead of get_or_404()
    paper = QuestionPaper.query.get(question.paper_id)
    if not paper:
        current_app.logger.error(f"Paper with ID {question.paper_id} not found for question {question_id}")
        flash(f'Paper with ID {question.paper_id} not found for this question.', 'danger')
        return redirect(url_for('admin.index'))
    
    if request.method == 'POST':
        question_number = request.form.get('question_number')
        difficulty_level = request.form.get('difficulty_level')
        marks = request.form.get('marks')
        
        # Check if the question number is being changed
        if question_number and question_number != question.question_number:
            # If the question number is changing, we need to clean up dependencies
            current_app.logger.info(f"Question number changing from {question.question_number} to {question_number}, cleaning up dependencies")
            if not clean_up_question_dependencies(question_id):
                flash('Error cleaning up question dependencies', 'danger')
                return redirect(url_for('admin.edit_question', question_id=question_id))
        
        # Check if a new image was uploaded
        if 'question_image' in request.files and request.files['question_image'].filename:
            file = request.files['question_image']
            if file and allowed_file(file.filename):
                # Generate a unique filename with UUID
                filename = secure_filename(file.filename)
                name, ext = os.path.splitext(filename)
                unique_filename = f"q{question_number}_{uuid.uuid4().hex.lower()}{ext}"
                
                # Create the paper directory if it doesn't exist
                paper_dir = os.path.join(get_data_folder(), f"paper_{paper.id}")
                if not os.path.exists(paper_dir):
                    os.makedirs(paper_dir)
                    current_app.logger.info(f"Created directory: {paper_dir}")
                
                # Save the file
                file_path = os.path.join(paper_dir, unique_filename)
                current_app.logger.info(f"Attempting to save edited image to: {file_path}")
                
                try:
                    file.save(file_path)
                    current_app.logger.info(f"Image saved successfully to: {file_path}")
                    
                    # Verify the file exists after saving
                    if os.path.exists(file_path):
                        current_app.logger.info(f"Verified: File exists at {file_path}")
                        
                        # Delete old image file if it exists
                        if question.image_path and os.path.exists(question.image_path):
                            try:
                                os.remove(question.image_path)
                                current_app.logger.info(f"Deleted old image: {question.image_path}")
                            except Exception as e:
                                current_app.logger.warning(f"Failed to delete old image: {str(e)}")
                        
                        # Update the question with the new image path
                        question.image_path = file_path
                        
                        # Update the image URL to point to the new image
                        domain = os.environ.get('REPLIT_DEV_DOMAIN') or os.environ.get('REPLIT_DOMAINS', 'localhost:5000').split(',')[0]
                        question.image_url = f"https://{domain}/user/question-image/{question.id}"
                        current_app.logger.info(f"Updated image URL to: {question.image_url}")
                    else:
                        current_app.logger.error(f"Error: File was not found at {file_path} after saving!")
                        flash("Error: Question image was not saved correctly. Please try again.", "danger")
                        return redirect(url_for('admin.edit_question', question_id=question_id))
                except Exception as e:
                    current_app.logger.error(f"Error saving image: {str(e)}")
                    flash(f"Error saving image: {str(e)}", "danger")
                    return redirect(url_for('admin.edit_question', question_id=question_id))
        
        # Update other question fields
        if question_number:
            question.question_number = question_number
        
        if difficulty_level:
            try:
                question.difficulty_level = int(difficulty_level)
            except ValueError:
                flash('Invalid difficulty level. Please provide a number.', 'danger')
                return redirect(url_for('admin.edit_question', question_id=question_id))
        
        if marks:
            try:
                question.marks = int(marks)
            except ValueError:
                flash('Invalid marks value. Please provide a number.', 'danger')
                return redirect(url_for('admin.edit_question', question_id=question_id))
        
        # Update or generate image_url if needed
        if not question.image_url:
            domain = os.environ.get('REPLIT_DEV_DOMAIN') or os.environ.get('REPLIT_DOMAINS', 'localhost:5000').split(',')[0]
            question.image_url = f"https://{domain}/user/question-image/{question.id}"
            current_app.logger.info(f"Generated missing image URL: {question.image_url}")
        
        try:
            db.session.commit()
            flash('Question updated successfully', 'success')
            return redirect(url_for('admin.manage_questions', paper_id=paper.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating question: {str(e)}', 'danger')
    
    return render_template('admin/edit_question.html', 
                          question=question, 
                          paper=paper)
