import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

# Create the SQLAlchemy extension
db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)

# Setup a secret key, required by sessions
app.secret_key = os.environ.get("SESSION_SECRET", "a-level-ai-assistant-secret-key")

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# Create database tables
with app.app_context():
    # Import models to ensure they're registered with SQLAlchemy
    import models  # noqa: F401
    
    # Create all tables
    db.create_all()
    logger.info("Database tables created")

# Register blueprints
from admin import admin_bp
from user import user_bp
from auth import auth_bp

app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(user_bp, url_prefix='/')
app.register_blueprint(auth_bp, url_prefix='/auth')

# Landing page (home) is the default for non-authenticated users
@app.route('/')
@app.route('/home')
def landing():
    from flask import render_template, redirect, url_for, request
    from flask_login import current_user
    
    # Add a show_landing query parameter to force showing the landing page
    show_landing = request.args.get('landing', 'false').lower() == 'true'
    
    # If user is already logged in and not explicitly asking for landing page, redirect to dashboard
    if current_user.is_authenticated and not show_landing:
        return redirect(url_for('user.index'))
    
    # Otherwise show the landing page
    return render_template('landing.html')

# Route for the mobile app design showcase
@app.route('/mobile')
def mobile_design():
    from flask import send_from_directory
    return send_from_directory('mobile_design', 'index.html')

# Serve mobile design static files
@app.route('/mobile/<path:filename>')
def mobile_design_files(filename):
    from flask import send_from_directory
    return send_from_directory('mobile_design', filename)
