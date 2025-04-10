import os
import stripe
from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from models import User, CreditTransaction

auth_bp = Blueprint('auth', __name__)

# Initialize Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

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
    """Handle user registration"""
    if current_user.is_authenticated:
        return redirect(url_for('user.index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists', 'danger')
            return render_template('auth/signup.html')
            
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists', 'danger')
            return render_template('auth/signup.html')
            
        new_user = User(
            username=username,
            email=email,
            credits=50  # New users start with 50 free credits
        )
        new_user.set_password(password)
        
        # Add a transaction for the initial free credits
        transaction = CreditTransaction(
            user=new_user,
            amount=50,
            transaction_type='bonus'
        )
        
        db.session.add(new_user)
        db.session.add(transaction)
        db.session.commit()
        
        flash('Account created successfully! You received 50 free credits to start.', 'success')
        login_user(new_user)
        return redirect(url_for('user.index'))
        
    return render_template('auth/signup.html')

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
    return render_template('auth/profile.html', user=current_user, transactions=transactions)

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

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.environ.get('STRIPE_WEBHOOK_SECRET', '')
        )
    except ValueError as e:
        # Invalid payload
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return jsonify({'status': 'error', 'message': str(e)}), 400

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Add credits to the user's account
        user_id = session['metadata']['user_id']
        credits = int(session['metadata']['credits'])
        
        user = User.query.get(user_id)
        if user:
            transaction = CreditTransaction(
                user_id=user_id,
                amount=credits,
                transaction_type='purchase',
                stripe_payment_id=session['id']
            )
            user.credits += credits
            db.session.add(transaction)
            db.session.commit()
    
    return jsonify({'status': 'success'})

@auth_bp.route('/payment-success')
@login_required
def payment_success():
    """Successful payment page"""
    session_id = request.args.get('session_id')
    if session_id:
        try:
            # Verify the session with Stripe
            checkout_session = stripe.checkout.Session.retrieve(session_id)
            if checkout_session and checkout_session.payment_status == 'paid':
                # Check if this payment was already processed via webhook
                transaction = CreditTransaction.query.filter_by(stripe_payment_id=session_id).first()
                if not transaction:
                    # Webhook hasn't processed this yet, do it manually
                    credits = int(checkout_session.metadata.credits)
                    transaction = CreditTransaction(
                        user_id=current_user.id,
                        amount=credits,
                        transaction_type='purchase',
                        stripe_payment_id=session_id
                    )
                    current_user.credits += credits
                    db.session.add(transaction)
                    db.session.commit()
                    
                flash(f'Payment successful! {credits} credits have been added to your account.', 'success')
                return render_template('auth/payment_success.html', credits=credits)
        except Exception as e:
            flash(f'Error verifying payment: {str(e)}', 'danger')
    
    # If we get here, either there was no session ID or verification failed
    flash('Your payment is being processed. Credits will be added to your account shortly.', 'info')
    return render_template('auth/payment_success.html')

@auth_bp.route('/payment-cancel')
@login_required
def payment_cancel():
    """Cancelled payment page"""
    flash('Payment was cancelled. No credits have been purchased.', 'warning')
    return render_template('auth/payment_cancel.html')