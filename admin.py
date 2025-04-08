import os
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from werkzeug.utils import secure_filename
from models import db, QuestionPaper, Question, Explanation

# Create admin blueprint
admin_bp = Blueprint('admin', __name__, template_folder='templates/admin')

# Helper function to get data folder
def get_data_folder():
    """Get or create the data folder for storing papers and questions"""
    data_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    os.makedirs(data_folder, exist_ok=True)
    return data_folder

@admin_bp.route('/')
def index():
    """Admin dashboard showing papers"""
    papers = QuestionPaper.query.order_by(QuestionPaper.created_at.desc()).all()
    return render_template('admin/index.html', papers=papers)

@admin_bp.route('/create_paper', methods=['GET', 'POST'])
def create_paper():
    """Create a new question paper"""
    if request.method == 'POST':
        title = request.form.get('title')
        subject = request.form.get('subject')
        description = request.form.get('description', '')
        
        if not title or not subject:
            flash('Title and subject are required', 'danger')
            return redirect(url_for('admin.create_paper'))
        
        # Create new paper
        paper = QuestionPaper(
            title=title,
            subject=subject,
            description=description
        )
        
        db.session.add(paper)
        db.session.commit()
        
        flash(f'Paper "{title}" created successfully', 'success')
        return redirect(url_for('admin.manage_questions', paper_id=paper.id))
    
    return render_template('admin/create_paper.html')

@admin_bp.route('/paper/<int:paper_id>/manage')
def manage_questions(paper_id):
    """Manage questions for a paper"""
    paper = QuestionPaper.query.get_or_404(paper_id)
    questions = Question.query.filter_by(paper_id=paper_id).order_by(Question.question_number).all()
    return render_template('admin/manage_questions.html', paper=paper, questions=questions)

@admin_bp.route('/paper/<int:paper_id>/add_question', methods=['POST'])
def add_question(paper_id):
    """Add a question to a paper"""
    paper = QuestionPaper.query.get_or_404(paper_id)
    
    # Check if file was uploaded
    if 'question_image' not in request.files:
        flash('No image file provided', 'danger')
        return redirect(url_for('admin.manage_questions', paper_id=paper_id))
    
    file = request.files['question_image']
    question_number = request.form.get('question_number', '').strip()
    
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('admin.manage_questions', paper_id=paper_id))
    
    if not question_number:
        flash('Question number is required', 'danger')
        return redirect(url_for('admin.manage_questions', paper_id=paper_id))
    
    # Create questions directory if it doesn't exist
    data_folder = get_data_folder()
    questions_folder = os.path.join(data_folder, 'questions', f'paper_{paper_id}')
    os.makedirs(questions_folder, exist_ok=True)
    
    # Save the question image
    filename = secure_filename(f"question_{question_number}_{file.filename}")
    file_path = os.path.join(questions_folder, filename)
    file.save(file_path)
    
    # Create question record in database
    question = Question(
        question_number=question_number,
        image_path=file_path,
        paper_id=paper_id
    )
    
    db.session.add(question)
    db.session.commit()
    
    flash(f'Question {question_number} added successfully', 'success')
    return redirect(url_for('admin.manage_questions', paper_id=paper_id))

@admin_bp.route('/question/<int:question_id>/delete', methods=['POST'])
def delete_question(question_id):
    """Delete a question"""
    question = Question.query.get_or_404(question_id)
    paper_id = question.paper_id
    
    # Delete related explanations
    Explanation.query.filter_by(question_id=question_id).delete()
    
    # Delete the image file if it exists
    if os.path.exists(question.image_path):
        try:
            os.remove(question.image_path)
        except Exception as e:
            current_app.logger.error(f"Error deleting image file: {str(e)}")
    
    # Delete the question from database
    db.session.delete(question)
    db.session.commit()
    
    flash('Question deleted successfully', 'success')
    return redirect(url_for('admin.manage_questions', paper_id=paper_id))

@admin_bp.route('/paper/<int:paper_id>/delete', methods=['POST'])
def delete_paper(paper_id):
    """Delete a paper and all its questions"""
    paper = QuestionPaper.query.get_or_404(paper_id)
    
    # Get all questions for this paper
    questions = Question.query.filter_by(paper_id=paper_id).all()
    
    # Delete all explanations for questions in this paper
    for question in questions:
        Explanation.query.filter_by(question_id=question.id).delete()
        
        # Delete image file if it exists
        if os.path.exists(question.image_path):
            try:
                os.remove(question.image_path)
            except Exception as e:
                current_app.logger.error(f"Error deleting image file: {str(e)}")
    
    # Delete all questions
    Question.query.filter_by(paper_id=paper_id).delete()
    
    # Delete the paper
    db.session.delete(paper)
    db.session.commit()
    
    flash(f'Paper "{paper.title}" deleted successfully', 'success')
    return redirect(url_for('admin.index'))
