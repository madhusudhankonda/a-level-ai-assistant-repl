from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
import os
import uuid
from werkzeug.utils import secure_filename
from models import db, QuestionPaper, Question, Subject, ExamBoard, PaperCategory
from flask_login import login_required, current_user

# Create admin blueprint
admin_bp = Blueprint('admin', __name__, template_folder='templates/admin')

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
        
    papers = QuestionPaper.query.order_by(QuestionPaper.created_at.desc()).all()
    subjects = Subject.query.all()
    return render_template('admin/index.html', papers=papers, subjects=subjects)

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
    
    return render_template('admin/manage_questions.html', paper=paper, questions=questions)

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
        
        if not question_number or not question_image:
            flash('Question number and image are required', 'danger')
            return redirect(url_for('admin.add_question', paper_id=paper_id))
        
        # Save the question image
        if question_image and question_image.filename:
            # Create paper directory if it doesn't exist
            paper_dir = os.path.join(get_data_folder(), f'paper_{paper_id}')
            if not os.path.exists(paper_dir):
                os.makedirs(paper_dir)
            
            # Generate a unique filename
            filename = f"{secure_filename(question_number)}_{uuid.uuid4().hex}.png"
            image_path = os.path.join(paper_dir, filename)
            
            # Save the image
            question_image.save(image_path)
            
            # Create question in database
            question = Question(
                question_number=question_number,
                image_path=image_path,
                paper_id=paper_id
            )
            
            db.session.add(question)
            db.session.commit()
            
            flash(f'Question {question_number} added successfully', 'success')
            return redirect(url_for('admin.manage_questions', paper_id=paper_id))
    
    return render_template('admin/add_question.html', paper=paper)

@admin_bp.route('/question/<int:question_id>/delete', methods=['POST'])
@login_required
def delete_question(question_id):
    """Delete a question"""
    # Verify user is an admin
    if not current_user.is_admin:
        flash('You do not have permission to access the admin area.', 'danger')
        return redirect(url_for('user.index'))
        
    question = Question.query.get_or_404(question_id)
    paper_id = question.paper_id
    
    # Delete the image file
    try:
        if os.path.exists(question.image_path):
            os.remove(question.image_path)
    except Exception as e:
        current_app.logger.error(f"Error deleting question image: {str(e)}")
    
    # Delete from database
    db.session.delete(question)
    db.session.commit()
    
    flash('Question deleted successfully', 'success')
    return redirect(url_for('admin.manage_questions', paper_id=paper_id))

@admin_bp.route('/paper/<int:paper_id>/delete', methods=['POST'])
@login_required
def delete_paper(paper_id):
    """Delete a paper and all its questions"""
    # Verify user is an admin
    if not current_user.is_admin:
        flash('You do not have permission to access the admin area.', 'danger')
        return redirect(url_for('user.index'))
        
    paper = QuestionPaper.query.get_or_404(paper_id)
    
    # Delete all questions for this paper
    questions = Question.query.filter_by(paper_id=paper_id).all()
    for question in questions:
        try:
            if os.path.exists(question.image_path):
                os.remove(question.image_path)
        except Exception as e:
            current_app.logger.error(f"Error deleting question image: {str(e)}")
    
    # Delete paper directory
    paper_dir = os.path.join(get_data_folder(), f'paper_{paper_id}')
    try:
        if os.path.exists(paper_dir):
            import shutil
            shutil.rmtree(paper_dir)
    except Exception as e:
        current_app.logger.error(f"Error deleting paper directory: {str(e)}")
    
    # Delete from database
    db.session.query(Question).filter_by(paper_id=paper_id).delete()
    db.session.delete(paper)
    db.session.commit()
    
    flash(f'Paper "{paper.title}" and all its questions deleted successfully', 'success')
    return redirect(url_for('admin.index'))
