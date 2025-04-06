from app import db
from datetime import datetime

class QuestionPaper(db.Model):
    """Model representing a question paper"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed = db.Column(db.Boolean, default=False)
    
    # Relationship with questions
    questions = db.relationship('Question', backref='paper', lazy=True)
    
    def __repr__(self):
        return f"<QuestionPaper {self.title}>"

class Question(db.Model):
    """Model representing an individual question from a paper"""
    id = db.Column(db.Integer, primary_key=True)
    question_number = db.Column(db.String(20), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    paper_id = db.Column(db.Integer, db.ForeignKey('question_paper.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with answers
    answer = db.relationship('Answer', backref='question', lazy=True, uselist=False)
    
    def __repr__(self):
        return f"<Question {self.question_number} from paper {self.paper_id}>"

class Answer(db.Model):
    """Model representing an answer to a question"""
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    answer_text = db.Column(db.Text, nullable=False)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Answer for question {self.question_id}>"

class ProcessingLog(db.Model):
    """Model for logging processing activities"""
    id = db.Column(db.Integer, primary_key=True)
    paper_id = db.Column(db.Integer, db.ForeignKey('question_paper.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Log {self.action} for paper {self.paper_id}>"
