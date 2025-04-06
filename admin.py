import os
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from werkzeug.utils import secure_filename
from models import db, QuestionPaper, Question, Answer, ProcessingLog
from utils.image_processor import process_question_paper, get_data_folder
from utils.openai_helper import generate_answer

# Create admin blueprint
admin_bp = Blueprint('admin', __name__, template_folder='templates/admin')

@admin_bp.route('/')
def index():
    """Admin dashboard showing papers and processing status"""
    papers = QuestionPaper.query.order_by(QuestionPaper.created_at.desc()).all()
    return render_template('admin/index.html', papers=papers)

@admin_bp.route('/upload', methods=['POST'])
def upload_paper():
    """Handle uploading of question papers"""
    if 'paper_file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('admin.index'))
    
    file = request.files['paper_file']
    
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('admin.index'))
    
    if file:
        # Get form data
        title = request.form.get('title', 'Untitled Paper')
        subject = request.form.get('subject', 'General')
        
        # Create data folders if they don't exist
        data_folder = get_data_folder()
        papers_folder = os.path.join(data_folder, 'papers')
        
        os.makedirs(papers_folder, exist_ok=True)
        
        # Save file
        filename = secure_filename(file.filename)
        file_path = os.path.join(papers_folder, filename)
        file.save(file_path)
        
        # Create paper record
        new_paper = QuestionPaper(
            title=title,
            subject=subject,
            original_filename=filename,
            processed=False
        )
        
        db.session.add(new_paper)
        db.session.commit()
        
        # Log the upload
        log_entry = ProcessingLog(
            paper_id=new_paper.id,
            action="Upload",
            status="Success",
            message=f"Paper uploaded: {filename}"
        )
        
        db.session.add(log_entry)
        db.session.commit()
        
        flash(f'Paper "{title}" uploaded successfully', 'success')
        return redirect(url_for('admin.index'))
    
    flash('Failed to upload paper', 'danger')
    return redirect(url_for('admin.index'))

@admin_bp.route('/process/<int:paper_id>')
def process_paper(paper_id):
    """View for processing a specific paper"""
    paper = QuestionPaper.query.get_or_404(paper_id)
    logs = ProcessingLog.query.filter_by(paper_id=paper_id).order_by(ProcessingLog.timestamp.desc()).all()
    return render_template('admin/process.html', paper=paper, logs=logs)

@admin_bp.route('/process/<int:paper_id>/clip', methods=['POST'])
def clip_questions(paper_id):
    """API endpoint to clip questions from a paper"""
    paper = QuestionPaper.query.get_or_404(paper_id)
    
    try:
        # Get data folder path
        data_folder = get_data_folder()
        paper_path = os.path.join(data_folder, 'papers', paper.original_filename)
        
        # Process the paper (clip questions)
        result = process_question_paper(paper_path, paper_id)
        
        # Create database entries for each question
        for q_number, img_path in result['questions'].items():
            question = Question(
                question_number=q_number,
                image_path=img_path,
                paper_id=paper_id
            )
            db.session.add(question)
        
        # Log the processing
        log_entry = ProcessingLog(
            paper_id=paper_id,
            action="Clip Questions",
            status="Success",
            message=f"Processed {len(result['questions'])} questions"
        )
        db.session.add(log_entry)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Successfully clipped {len(result["questions"])} questions',
            'question_count': len(result['questions'])
        })
        
    except Exception as e:
        current_app.logger.error(f"Error clipping questions: {str(e)}")
        
        # Log the error
        log_entry = ProcessingLog(
            paper_id=paper_id,
            action="Clip Questions",
            status="Error",
            message=str(e)
        )
        db.session.add(log_entry)
        db.session.commit()
        
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@admin_bp.route('/process/<int:paper_id>/generate_answers', methods=['POST'])
def generate_answers(paper_id):
    """API endpoint to generate answers for the questions in a paper"""
    paper = QuestionPaper.query.get_or_404(paper_id)
    questions = Question.query.filter_by(paper_id=paper_id).all()
    
    try:
        processed_count = 0
        
        for question in questions:
            # Skip if already has an answer
            if Answer.query.filter_by(question_id=question.id).first():
                continue
                
            # Generate answer using GPT-4o
            answer_text = generate_answer(question.image_path, paper.subject)
            
            # Create answer record
            answer = Answer(
                question_id=question.id,
                answer_text=answer_text
            )
            
            db.session.add(answer)
            processed_count += 1
            
            # Commit after each answer to avoid losing all work if one fails
            db.session.commit()
        
        # Mark paper as fully processed
        paper.processed = True
        
        # Log the processing
        log_entry = ProcessingLog(
            paper_id=paper_id,
            action="Generate Answers",
            status="Success",
            message=f"Generated {processed_count} answers"
        )
        db.session.add(log_entry)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Successfully generated {processed_count} answers',
            'processed_count': processed_count
        })
        
    except Exception as e:
        current_app.logger.error(f"Error generating answers: {str(e)}")
        
        # Log the error
        log_entry = ProcessingLog(
            paper_id=paper_id,
            action="Generate Answers",
            status="Error",
            message=str(e)
        )
        db.session.add(log_entry)
        db.session.commit()
        
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@admin_bp.route('/view_logs/<int:paper_id>')
def view_logs(paper_id):
    """API endpoint to get logs for a paper"""
    logs = ProcessingLog.query.filter_by(paper_id=paper_id).order_by(ProcessingLog.timestamp.desc()).all()
    
    logs_data = [{
        'action': log.action,
        'status': log.status,
        'message': log.message,
        'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    } for log in logs]
    
    return jsonify(logs_data)
