from flask import Blueprint, render_template, request, jsonify, redirect, url_for, current_app, send_file
import os
import base64
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
            
            # Save the explanation
            explanation = Explanation(
                question_id=question_id,
                explanation_text=explanation_text
            )
            
            db.session.add(explanation)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'question_id': question_id,
                'explanation': explanation_text,
                'is_new': True
            })
            
        except Exception as e:
            current_app.logger.error(f"Error generating explanation: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Error generating explanation: {str(e)}'
            }), 500
    
    # Return existing explanation for GET requests when one exists
    return jsonify({
        'success': True,
        'question_id': question_id,
        'explanation': existing_explanation.explanation_text,
        'is_new': False,
        'generated_at': existing_explanation.generated_at.strftime('%Y-%m-%d %H:%M:%S')
    })
