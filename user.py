from flask import Blueprint, render_template, request, jsonify, redirect, url_for, current_app, send_file
import os
from models import QuestionPaper, Question, Answer
from utils.openai_helper import generate_explanation
import base64

# Create user blueprint
user_bp = Blueprint('user', __name__, template_folder='templates/user')

@user_bp.route('/')
def index():
    """User dashboard showing available papers"""
    # Get all processed papers
    papers = QuestionPaper.query.filter_by(processed=True).order_by(QuestionPaper.created_at.desc()).all()
    return render_template('user/index.html', papers=papers)

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

@user_bp.route('/api/answer/<int:question_id>', methods=['GET'])
def get_answer(question_id):
    """API endpoint to get the answer for a question"""
    question = Question.query.get_or_404(question_id)
    answer = Answer.query.filter_by(question_id=question_id).first()
    
    if answer:
        return jsonify({
            'success': True,
            'question_id': question_id,
            'answer': answer.answer_text
        })
    else:
        return jsonify({
            'success': False,
            'message': 'No answer available for this question'
        }), 404

@user_bp.route('/api/explain/<int:question_id>', methods=['GET'])
def explain_answer(question_id):
    """API endpoint to get an explanation for a question's answer"""
    question = Question.query.get_or_404(question_id)
    answer = Answer.query.filter_by(question_id=question_id).first()
    
    if not answer:
        return jsonify({
            'success': False,
            'message': 'No answer available to explain'
        }), 404
    
    try:
        # Read the image and encode it to base64
        with open(question.image_path, "rb") as image_file:
            image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Get the paper details for context
        paper = QuestionPaper.query.get(question.paper_id)
        
        # Generate explanation using OpenAI
        explanation = generate_explanation(
            image_base64, 
            answer.answer_text, 
            paper.subject
        )
        
        return jsonify({
            'success': True,
            'question_id': question_id,
            'explanation': explanation
        })
        
    except Exception as e:
        current_app.logger.error(f"Error generating explanation: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error generating explanation: {str(e)}'
        }), 500
