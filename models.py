from datetime import datetime
from app import db

class Subject(db.Model):
    """Model representing a subject (e.g., Maths, Physics)"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    
    # Relationships
    boards = db.relationship('ExamBoard', backref='subject', lazy=True)
    
    def __repr__(self):
        return f'<Subject {self.name}>'


class ExamBoard(db.Model):
    """Model representing an exam board (e.g., AQA, Edexcel)"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Relationships
    categories = db.relationship('PaperCategory', backref='board', lazy=True)
    
    # Composite unique constraint
    __table_args__ = (db.UniqueConstraint('name', 'subject_id', name='_board_subject_uc'),)
    
    def __repr__(self):
        return f'<ExamBoard {self.name} - {self.subject_id}>'


class PaperCategory(db.Model):
    """Model representing a paper category (e.g., Pure Maths, Pure and Statistics)"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    board_id = db.Column(db.Integer, db.ForeignKey('exam_board.id'), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Relationships
    papers = db.relationship('QuestionPaper', backref='category', lazy=True)
    
    # Composite unique constraint
    __table_args__ = (db.UniqueConstraint('name', 'board_id', name='_category_board_uc'),)
    
    def __repr__(self):
        return f'<PaperCategory {self.name} - {self.board_id}>'


class QuestionPaper(db.Model):
    """Model representing a question paper"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('paper_category.id'), nullable=True)
    subject = db.Column(db.String(50), nullable=False)  # Legacy field, kept for backwards compatibility
    exam_period = db.Column(db.String(50), nullable=True, default="Unknown")  # e.g., "June 2023", "Nov 2022"
    paper_type = db.Column(db.String(50), nullable=True, default="QP")  # QP, MS (mark scheme), etc.
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with Question
    questions = db.relationship('Question', backref='paper', lazy=True, order_by='Question.question_number')
    
    def __repr__(self):
        return f'<QuestionPaper {self.title}>'


class Question(db.Model):
    """Model representing an individual question from a paper"""
    id = db.Column(db.Integer, primary_key=True)
    question_number = db.Column(db.String(20), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    paper_id = db.Column(db.Integer, db.ForeignKey('question_paper.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Question {self.question_number} - Paper {self.paper_id}>'


class Explanation(db.Model):
    """Model representing a generated explanation for a question"""
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    explanation_text = db.Column(db.Text, nullable=False)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with questions
    question = db.relationship('Question', backref='explanations')
    
    def __repr__(self):
        return f'<Explanation for Question {self.question_id}>'
