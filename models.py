from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import json

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
    image_url = db.Column(db.String(255), nullable=True)  # URL-based storage reference
    paper_id = db.Column(db.Integer, db.ForeignKey('question_paper.id'), nullable=False)
    difficulty_level = db.Column(db.Integer, nullable=True)  # 1-5 scale
    marks = db.Column(db.Integer, nullable=True)  # Number of marks for the question
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    topics = db.relationship('QuestionTopic', back_populates='question')
    
    def __repr__(self):
        return f'<Question {self.question_number} - Paper {self.paper_id}>'
        
    def get_topic_names(self):
        """Get list of topic names associated with this question"""
        return [question_topic.topic.name for question_topic in self.topics]


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


class UserProfile(db.Model):
    """Enhanced user profile information"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    school_name = db.Column(db.String(100), nullable=True)
    grade_year = db.Column(db.String(20), nullable=True)  # e.g., "Year 12", "Year 13"
    preferred_subjects = db.Column(db.String(255), nullable=True)  # Comma-separated list
    subscription_tier = db.Column(db.String(20), default="free")  # free, standard, premium
    profile_image_path = db.Column(db.String(255), nullable=True)
    
    # Consent tracking fields
    terms_accepted = db.Column(db.Boolean, default=False)
    privacy_accepted = db.Column(db.Boolean, default=False)
    marketing_consent = db.Column(db.Boolean, default=False)
    age_confirmed = db.Column(db.Boolean, default=False)
    terms_accepted_date = db.Column(db.DateTime, nullable=True)
    privacy_accepted_date = db.Column(db.DateTime, nullable=True)
    
    # AI usage consent - will be required for each session
    ai_usage_consent_required = db.Column(db.Boolean, default=True)
    last_ai_consent_date = db.Column(db.DateTime, nullable=True)
    
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with User
    user = db.relationship('User', backref=db.backref('profile', uselist=False, lazy=True))
    
    def __repr__(self):
        return f'<UserProfile for User {self.user_id}>'
    
    def get_preferred_subjects_list(self):
        """Convert preferred_subjects string to list"""
        if not self.preferred_subjects:
            return []
        return [subject.strip() for subject in self.preferred_subjects.split(',')]
    
    def set_preferred_subjects_list(self, subjects_list):
        """Convert list to preferred_subjects string"""
        if not subjects_list:
            self.preferred_subjects = None
        else:
            self.preferred_subjects = ','.join(subjects_list)


class Topic(db.Model):
    """Model for academic topics/subtopics within subjects"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    parent_topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=True)  # For hierarchical topics
    description = db.Column(db.Text, nullable=True)
    difficulty_level = db.Column(db.Integer, nullable=True)  # 1-5 scale
    
    # Relationships
    subject = db.relationship('Subject', backref='topics')
    subtopics = db.relationship('Topic', 
                               backref=db.backref('parent_topic', remote_side=[id]),
                               lazy=True)
    questions = db.relationship('QuestionTopic', back_populates='topic')
    
    # Composite unique constraint
    __table_args__ = (db.UniqueConstraint('name', 'subject_id', 'parent_topic_id', name='_topic_subject_parent_uc'),)
    
    def __repr__(self):
        return f'<Topic {self.name} - Subject {self.subject_id}>'


class QuestionTopic(db.Model):
    """Junction table for many-to-many relationship between Questions and Topics"""
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)
    
    # Relationships
    question = db.relationship('Question', back_populates='topics')
    topic = db.relationship('Topic', back_populates='questions')
    
    # Composite unique constraint
    __table_args__ = (db.UniqueConstraint('question_id', 'topic_id', name='_question_topic_uc'),)
    
    def __repr__(self):
        return f'<QuestionTopic {self.question_id}-{self.topic_id}>'


class UserQuery(db.Model):
    """Model for tracking user queries to the AI"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    query_type = db.Column(db.String(20), nullable=False)  # 'explanation', 'answer_feedback', 'custom'
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=True)  # Optional, if related to a specific question
    query_text = db.Column(db.Text, nullable=True)  # For custom queries
    image_path = db.Column(db.String(255), nullable=True)  # For captured images
    response_text = db.Column(db.Text, nullable=False)  # AI response
    credits_used = db.Column(db.Integer, nullable=False, default=10)
    subject = db.Column(db.String(50), nullable=True)
    is_favorite = db.Column(db.Boolean, default=False)  # User can mark favorite responses
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='queries')
    question = db.relationship('Question', backref='user_queries')
    
    def __repr__(self):
        return f'<UserQuery {self.query_type} by User {self.user_id}>'
    
    def get_truncated_response(self, length=100):
        """Get a truncated version of the response for display"""
        if len(self.response_text) <= length:
            return self.response_text
        return self.response_text[:length] + '...'


class StudentAnswer(db.Model):
    """Model for tracking student answers and feedback"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=True)  # Optional, if related to a standard question
    user_query_id = db.Column(db.Integer, db.ForeignKey('user_query.id'), nullable=True)  # If answer is for a custom query
    answer_image_path = db.Column(db.String(255), nullable=True)  # Path to student's answer image
    answer_text = db.Column(db.Text, nullable=True)  # Optional typed answer
    feedback_text = db.Column(db.Text, nullable=False)  # AI feedback on the answer
    score = db.Column(db.Float, nullable=True)  # Score given by AI (e.g., 8/10)
    max_score = db.Column(db.Float, nullable=True)  # Maximum possible score
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='answers')
    question = db.relationship('Question', backref='student_answers')
    user_query = db.relationship('UserQuery', backref='student_answers')
    
    def __repr__(self):
        return f'<StudentAnswer by User {self.user_id} for Question {self.question_id or self.user_query_id}>'
    
    def get_score_percentage(self):
        """Calculate percentage score"""
        if self.score is None or self.max_score is None or self.max_score == 0:
            return None
        return (self.score / self.max_score) * 100


class UserFeedback(db.Model):
    """Model for capturing user feedback, issues, and feature requests"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Optional, anonymous feedback allowed
    feedback_type = db.Column(db.String(50), nullable=False)  # 'issue', 'feature', 'general'
    subject = db.Column(db.String(200), nullable=False)  # Brief subject/title
    feedback_text = db.Column(db.Text, nullable=False)  # The actual feedback content
    
    # Optional fields
    impact_level = db.Column(db.String(50), nullable=True)  # 'low', 'medium', 'high', 'critical'
    page_url = db.Column(db.String(255), nullable=True)  # Where the feedback was submitted from
    browser_info = db.Column(db.String(255), nullable=True)  # Browser/device information
    screenshot_path = db.Column(db.String(255), nullable=True)  # Path to attached screenshot if any
    
    # Status tracking fields for admins
    status = db.Column(db.String(50), default='new')  # 'new', 'in-review', 'planned', 'implemented', 'declined'
    admin_notes = db.Column(db.Text, nullable=True)  # Internal notes for admins
    admin_response = db.Column(db.Text, nullable=True)  # Response to send to the user
    
    # Tracking fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='feedback')
    
    def __repr__(self):
        return f'<UserFeedback {self.feedback_type} - {self.subject}>'
