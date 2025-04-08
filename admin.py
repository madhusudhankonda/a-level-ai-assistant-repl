from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
import os
import uuid
from werkzeug.utils import secure_filename
from models import db, QuestionPaper, Question

# Create admin blueprint
admin_bp = Blueprint('admin', __name__, template_folder='templates/admin')

def get_data_folder():
    """Get or create the data folder for storing papers and questions"""
    data_dir = os.path.join(os.getcwd(), 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return data_dir

@admin_bp.route('/')
def index():
    """Admin dashboard showing papers"""
    papers = QuestionPaper.query.order_by(QuestionPaper.created_at.desc()).all()
    return render_template('admin/index.html', papers=papers)

@admin_bp.route('/paper/create', methods=['GET', 'POST'])
def create_paper():
    """Create a new question paper"""
    if request.method == 'POST':
        title = request.form.get('title')
        subject = request.form.get('subject')
        description = request.form.get('description', '')
        
        if not title or not subject:
            flash('Title and subject are required', 'danger')
            return redirect(url_for('admin.create_paper'))
        
        # Create new paper in the database
        paper = QuestionPaper(
            title=title,
            subject=subject,
            description=description
        )
        
        db.session.add(paper)
        db.session.commit()
        
        # Create folder for storing questions for this paper
        paper_dir = os.path.join(get_data_folder(), f'paper_{paper.id}')
        if not os.path.exists(paper_dir):
            os.makedirs(paper_dir)
        
        flash(f'Paper "{title}" created successfully', 'success')
        return redirect(url_for('admin.manage_questions', paper_id=paper.id))
    
    return render_template('admin/create_paper.html')

@admin_bp.route('/paper/<int:paper_id>/questions')
def manage_questions(paper_id):
    """Manage questions for a paper"""
    paper = QuestionPaper.query.get_or_404(paper_id)
    questions = Question.query.filter_by(paper_id=paper_id).order_by(Question.question_number).all()
    
    return render_template('admin/manage_questions.html', paper=paper, questions=questions)

@admin_bp.route('/paper/<int:paper_id>/question/add', methods=['GET', 'POST'])
def add_question(paper_id):
    """Add a question to a paper"""
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
def delete_question(question_id):
    """Delete a question"""
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
def delete_paper(paper_id):
    """Delete a paper and all its questions"""
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
