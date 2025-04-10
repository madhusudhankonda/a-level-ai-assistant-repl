from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

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


class User(UserMixin, db.Model):
    """Model representing a user of the system"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    credits = db.Column(db.Integer, default=50)  # New users receive 50 free credits
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    transactions = db.relationship('CreditTransaction', backref='user', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        """Set password hash for the user"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against stored hash"""
        return check_password_hash(self.password_hash, password)
        
    def add_credits(self, amount, transaction_type='purchase'):
        """Add credits to user account"""
        if amount <= 0:
            return False
            
        self.credits += amount
        transaction = CreditTransaction(
            user_id=self.id,
            amount=amount,
            transaction_type=transaction_type
        )
        db.session.add(transaction)
        return True
        
    def use_credits(self, amount=10):
        """Use credits for AI services (default 10 credits per query)"""
        if self.credits < amount:
            return False
            
        self.credits -= amount
        transaction = CreditTransaction(
            user_id=self.id,
            amount=-amount,
            transaction_type='usage'
        )
        db.session.add(transaction)
        return True
        
    def has_sufficient_credits(self, amount=10):
        """Check if user has sufficient credits"""
        return self.credits >= amount


class CreditTransaction(db.Model):
    """Model representing credit transactions"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)  # Can be positive (purchase) or negative (usage)
    transaction_type = db.Column(db.String(20), nullable=False)  # 'purchase', 'usage', 'bonus'
    stripe_payment_id = db.Column(db.String(100), nullable=True)  # For purchases via Stripe
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CreditTransaction {self.transaction_type} {self.amount} for User {self.user_id}>'
