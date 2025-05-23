import os
import stripe
import logging
from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from models import User, CreditTransaction, UserProfile, UserQuery, StudentAnswer
from forms import LoginForm, SignupForm, ProfileEditForm
from sqlalchemy import func

auth_bp = Blueprint('auth', __name__)

# Initialize Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

# Set up logging
logger = logging.getLogger(__name__)

# Credit pricing options
CREDIT_PACKAGES = [
    {'id': 'credits_100', 'credits': 100, 'price': 100},  # £1.00
    {'id': 'credits_200', 'credits': 200, 'price': 200},  # £2.00
    {'id': 'credits_500', 'credits': 500, 'price': 500}   # £5.00
]

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if current_user.is_authenticated:
        return redirect(url_for('user.index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            flash('Please check your login details and try again.', 'danger')
            return render_template('auth/login.html')
            
        login_user(user, remember=remember)
        user.last_login = db.func.current_timestamp()
        db.session.commit()
        
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(url_for('user.index'))
        
    return render_template('auth/login.html')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handle user registration with Terms and Conditions consent"""
    if current_user.is_authenticated:
        return redirect(url_for('user.index'))
    
    form = SignupForm()
    
    if form.validate_on_submit():
        # Check if email already exists
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash('Email address already exists', 'danger')
            return render_template('auth/signup.html', form=form)
        
        # Check if username already exists
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            flash('Username already exists', 'danger')
            return render_template('auth/signup.html', form=form)
        
        # Create the new user
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            credits=50  # New users start with 50 free credits
        )
        new_user.set_password(form.password.data)
        
        # Add a transaction for the initial free credits
        transaction = CreditTransaction(
            user=new_user,
            amount=50,
            transaction_type='bonus'
        )
        
        # Create a profile with consent records
        current_time = datetime.utcnow()
        profile = UserProfile(
            user=new_user,
            terms_accepted=True,
            privacy_accepted=True,
            marketing_consent=form.marketing_consent.data,
            age_confirmed=True,
            terms_accepted_date=current_time,
            privacy_accepted_date=current_time,
            ai_usage_consent_required=True,
            last_ai_consent_date=None  # Will be set when they first use AI features
        )
        
        db.session.add(new_user)
        db.session.add(transaction)
        db.session.add(profile)
        db.session.commit()
        
        flash('Account created successfully! You received 50 free credits to start.', 'success')
        login_user(new_user)
        return redirect(url_for('user.index'))
    
    return render_template('auth/signup.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout"""
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
@login_required
def profile():
    """Display user profile and credit information"""
    transactions = current_user.transactions.order_by(CreditTransaction.transaction_date.desc()).limit(10).all()
    
    # Get user queries count
    query_count = UserQuery.query.filter_by(user_id=current_user.id).count()
    
    # Get user profile with consent information
    user_profile = UserProfile.query.filter_by(user_id=current_user.id).first()
    
    # Check consent status
    ai_consent_status = "Not given"
    consent_expiry = None
    days_remaining = 0
    
    if user_profile and user_profile.last_ai_consent_date:
        if not user_profile.ai_usage_consent_required:
            # Calculate days until expiration
            consent_age = datetime.utcnow() - user_profile.last_ai_consent_date
            days_remaining = 30 - consent_age.days
            
            if days_remaining > 0:
                ai_consent_status = "Active"
                consent_expiry = user_profile.last_ai_consent_date + timedelta(days=30)
            else:
                ai_consent_status = "Expired"
                user_profile.ai_usage_consent_required = True
                db.session.commit()
        else:
            ai_consent_status = "Renewal required"
    
    return render_template('auth/profile.html', 
                           user=current_user, 
                           transactions=transactions,
                           query_count=query_count,
                           user_profile=user_profile,
                           ai_consent_status=ai_consent_status,
                           consent_expiry=consent_expiry,
                           days_remaining=days_remaining)

@auth_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def profile_edit():
    """Edit user profile information"""
    # Get or create user profile
    user_profile = UserProfile.query.filter_by(user_id=current_user.id).first()
    if not user_profile:
        user_profile = UserProfile(user_id=current_user.id)
        db.session.add(user_profile)
        db.session.commit()
    
    form = ProfileEditForm()
    
    if request.method == 'GET':
        # Pre-populate form with existing data
        if user_profile:
            form.first_name.data = user_profile.first_name
            form.last_name.data = user_profile.last_name
            form.school_name.data = user_profile.school_name
            form.grade_year.data = user_profile.grade_year
            if user_profile.preferred_subjects:
                form.preferred_subjects.data = user_profile.get_preferred_subjects_list()
    
    if form.validate_on_submit():
        # Update user profile with form data
        user_profile.first_name = form.first_name.data
        user_profile.last_name = form.last_name.data
        user_profile.school_name = form.school_name.data
        user_profile.grade_year = form.grade_year.data
        user_profile.set_preferred_subjects_list(form.preferred_subjects.data)
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/profile_edit.html', form=form, user=current_user)

@auth_bp.route('/history')
@login_required
def query_history():
    """Display user's query history"""
    page = request.args.get('page', 1, type=int)
    queries = UserQuery.query.filter_by(user_id=current_user.id)\
        .order_by(UserQuery.created_at.desc())\
        .paginate(page=page, per_page=10)
    
    return render_template('auth/query_history.html', 
                           queries=queries, 
                           user=current_user)

@auth_bp.route('/answer-history')
@login_required
def answer_history():
    """Display user's submitted answers and feedback history"""
    page = request.args.get('page', 1, type=int)
    
    # Get paginated answers
    answers = StudentAnswer.query.filter_by(user_id=current_user.id)\
        .order_by(StudentAnswer.created_at.desc())\
        .paginate(page=page, per_page=10)
    
    # Calculate performance statistics
    avg_score = db.session.query(func.avg(
        (StudentAnswer.score * 100) / StudentAnswer.max_score
    )).filter_by(user_id=current_user.id).scalar() or 0
    
    high_score = db.session.query(func.max(
        (StudentAnswer.score * 100) / StudentAnswer.max_score
    )).filter_by(user_id=current_user.id).scalar() or 0
    
    # Get subject statistics
    student_answers = StudentAnswer.query.filter_by(user_id=current_user.id).all()
    subjects = set()
    subject_counts = {}
    
    for answer in student_answers:
        subject = None
        if answer.question and answer.question.paper and answer.question.paper.subject:
            subject = answer.question.paper.subject
        elif answer.user_query and answer.user_query.subject:
            subject = answer.user_query.subject
            
        if subject:
            subjects.add(subject)
            subject_counts[subject] = subject_counts.get(subject, 0) + 1
    
    return render_template('auth/answer_history.html',
                          answers=answers,
                          avg_score=avg_score,
                          high_score=high_score,
                          subjects=subjects,
                          subject_counts=subject_counts,
                          user=current_user)

@auth_bp.route('/buy-credits')
@login_required
def buy_credits():
    """Show the credit purchase options"""
    return render_template('auth/buy_credits.html', packages=CREDIT_PACKAGES)

@auth_bp.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    """Create a Stripe checkout session for credit purchase"""
    package_id = request.form.get('package_id')
    
    # Validate package selection
    selected_package = next((p for p in CREDIT_PACKAGES if p['id'] == package_id), None)
    if not selected_package:
        flash('Invalid package selection', 'danger')
        return redirect(url_for('auth.buy_credits'))
    
    domain_url = request.host_url.rstrip('/')
    
    try:
        # Create new Checkout Session for the order
        checkout_session = stripe.checkout.Session.create(
            customer_email=current_user.email,
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'gbp',
                    'product_data': {
                        'name': f"{selected_package['credits']} AI Assistant Credits",
                        'description': f"Purchase {selected_package['credits']} credits for the A-Level AI Assistant",
                    },
                    'unit_amount': selected_package['price'],  # in pence (100 = £1.00)
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=domain_url + url_for('auth.payment_success') + f"?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=domain_url + url_for('auth.payment_cancel'),
            metadata={
                'user_id': current_user.id,
                'credits': selected_package['credits']
            }
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('auth.buy_credits'))

@auth_bp.route('/webhook', methods=['POST'])
def webhook():
    """Stripe webhook to handle successful payments"""
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    logger.info(f"Received Stripe webhook with signature: {sig_header[:10]}...")
    
    if not webhook_secret:
        logger.error("STRIPE_WEBHOOK_SECRET is not configured properly")
        return jsonify({'status': 'error', 'message': 'Webhook secret not configured'}), 500

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        logger.error(f"Invalid payload in Stripe webhook: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Invalid payload'}), 400
    except Exception as e:
        # This catches all Stripe exceptions including SignatureVerificationError
        logger.error(f"Error verifying Stripe webhook: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Verification error'}), 400

    # Log the event type
    logger.info(f"Processing Stripe event: {event['type']} with ID: {event['id']}")
    
    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        session_id = session.get('id')
        
        try:
            # Check for idempotency - don't process the same payment twice
            existing_transaction = CreditTransaction.query.filter_by(stripe_payment_id=session_id).first()
            if existing_transaction:
                logger.info(f"Payment {session_id} already processed. Skipping.")
                return jsonify({'status': 'success', 'message': 'Payment already processed'}), 200
            
            # Add credits to the user's account
            user_id = session['metadata'].get('user_id')
            credits = int(session['metadata'].get('credits', 0))
            
            if not user_id or not credits:
                logger.error(f"Missing metadata in Stripe session: {session_id}")
                return jsonify({'status': 'error', 'message': 'Missing metadata'}), 400
            
            user = User.query.get(user_id)
            if not user:
                logger.error(f"User not found for ID: {user_id}")
                return jsonify({'status': 'error', 'message': 'User not found'}), 404
            
            # Create the transaction and add credits
            transaction = CreditTransaction(
                user_id=user_id,
                amount=credits,
                transaction_type='purchase',
                stripe_payment_id=session_id
            )
            user.credits += credits
            db.session.add(transaction)
            db.session.commit()
            
            logger.info(f"Added {credits} credits to user {user_id} via webhook")
        except Exception as e:
            logger.error(f"Error processing payment {session_id}: {str(e)}")
            db.session.rollback()
            return jsonify({'status': 'error', 'message': f'Error processing payment: {str(e)}'}), 500
    
    return jsonify({'status': 'success'})

@auth_bp.route('/payment-success')
@login_required
def payment_success():
    """Successful payment page"""
    session_id = request.args.get('session_id')
    
    if not session_id:
        logger.warning(f"Payment success page accessed without session_id by user {current_user.id}")
        flash('No payment session found. If you completed a payment, it may still be processing.', 'info')
        return render_template('auth/payment_success.html')
        
    logger.info(f"Payment success page accessed with session_id: {session_id} by user {current_user.id}")
    
    try:
        # First check if this payment was already processed
        existing_transaction = CreditTransaction.query.filter_by(stripe_payment_id=session_id).first()
        
        if existing_transaction:
            # Already processed by webhook or previous visit
            logger.info(f"Payment {session_id} already processed for user {current_user.id}")
            credits = existing_transaction.amount
            flash(f'Payment successful! {credits} credits have been added to your account.', 'success')
            return render_template('auth/payment_success.html', credits=credits)
            
        # If not processed yet, verify with Stripe
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        
        # Verify the payment belongs to this user
        if str(checkout_session.metadata.get('user_id')) != str(current_user.id):
            logger.warning(f"User {current_user.id} attempted to access payment for user {checkout_session.metadata.get('user_id')}")
            flash('This payment does not belong to your account.', 'danger')
            return redirect(url_for('auth.profile'))
            
        if checkout_session and checkout_session.payment_status == 'paid':
            # Process payment if webhook hasn't done it yet
            credits = int(checkout_session.metadata.get('credits', 0))
            
            # Create transaction record
            transaction = CreditTransaction(
                user_id=current_user.id,
                amount=credits,
                transaction_type='purchase',
                stripe_payment_id=session_id
            )
            
            # Add credits to user account
            current_user.credits += credits
            db.session.add(transaction)
            db.session.commit()
            
            logger.info(f"Added {credits} credits to user {current_user.id} via success page")
            flash(f'Payment successful! {credits} credits have been added to your account.', 'success')
            return render_template('auth/payment_success.html', credits=credits)
        else:
            # Payment exists but isn't paid
            logger.warning(f"Unpaid session accessed: {session_id}, status: {checkout_session.payment_status}")
            flash('Your payment is still being processed. Please check back shortly.', 'info')
            return render_template('auth/payment_success.html')
            
    except Exception as e:
        logger.error(f"Error processing payment session {session_id}: {str(e)}")
        db.session.rollback()
        flash('There was an issue verifying your payment. If you completed a payment but don\'t see credits added, please contact support.', 'warning')
        return render_template('auth/payment_success.html')

@auth_bp.route('/payment-cancel')
@login_required
def payment_cancel():
    """Cancelled payment page"""
    flash('Payment was cancelled. No credits have been purchased.', 'warning')
    return render_template('auth/payment_cancel.html')