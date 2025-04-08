from app import db
from datetime import datetime

class QuestionPaper(db.Model):
    """Model representing a question paper"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with questions
    questions = db.relationship('Question', backref='paper', lazy=True, order_by='Question.question_number')
    
    def __repr__(self):
        return f"<QuestionPaper {self.title}>"

class Question(db.Model):
    """Model representing an individual question from a paper"""
    id = db.Column(db.Integer, primary_key=True)
    question_number = db.Column(db.String(20), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    paper_id = db.Column(db.Integer, db.ForeignKey('question_paper.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Question {self.question_number} from paper {self.paper_id}>"

class Explanation(db.Model):
    """Model representing a generated explanation for a question"""
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    explanation_text = db.Column(db.Text, nullable=False)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with question
    question = db.relationship('Question', backref='explanations')
    
    def __repr__(self):
        return f"<Explanation for question {self.question_id}>"
