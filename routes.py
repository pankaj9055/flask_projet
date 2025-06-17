from flask import render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory
from app import app, db
from models import User, MiningSession, Deposit, AdminUser, Announcement, PaymentSettings
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import os

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/auth')
def auth():
    return render_template('auth.html')

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.form
        
        # Validate input with better error messages
        if not data.get('name') or len(data.get('name', '').strip()) < 2:
            flash('Name must be at least 2 characters long', 'error')
            return redirect(url_for('auth'))
            
        if not data.get('email') or '@' not in data.get('email', ''):
            flash('Please enter a valid email address', 'error')
            return redirect(url_for('auth'))
            
        if not data.get('password') or len(data.get('password', '')) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return redirect(url_for('auth'))
            
        if not data.get('country'):
            flash('Please select your country', 'error')
            return redirect(url_for('auth'))
        
        # Check if user exists
        existing_user = User.query.filter_by(email=data['email'].lower()).first()
        if existing_user:
            flash('Email already registered. Please login instead.', 'error')
            return redirect(url_for('auth'))
        
        # Create new user with error handling
        user = User(
            name=data['name'].strip(),
            email=data['email'].lower().strip(),
            country=data['country']
        )
        user.set_password(data['password'])
        
        # Handle referral with validation
        if data.get('referral_code'):
            referral_code = data['referral_code'].strip().upper()
            referrer = User.query.filter_by(referral_code=referral_code).first()
            if referrer:
                user.referred_by = referrer.id
            else:
                flash('Invalid referral code, but registration continues', 'warning')
        
        db.session.add(user)
        db.session.commit()
        
        session['user_id'] = user.id
        flash('Registration successful! Welcome to Oxin!', 'success')
        return redirect(url_for('mining'))
        
    except Exception as e:
        db.session.rollback()
        flash('Registration failed. Please try again.', 'error')
        return redirect(url_for('auth'))

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.form
        
        # Input validation
        if not data.get('email') or not data.get('password'):
            flash('Email and password are required', 'error')
            return redirect(url_for('auth'))
        
        # Normalize email for lookup
        email = data['email'].lower().strip()
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(data['password']):
            if not user.is_active:
                flash('Account is disabled. Contact support.', 'error')
                return redirect(url_for('auth'))
                
            session['user_id'] = user.id
            flash('Login successful! Welcome back!', 'success')
            return redirect(url_for('mining'))
        else:
            flash('Invalid email or password', 'error')
            return redirect(url_for('auth'))
            
    except Exception as e:
        flash('Login failed. Please try again.', 'error')
        return redirect(url_for('auth'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

@app.route('/mining')
def mining():
    if 'user_id' not in session:
        return redirect(url_for('auth'))
    
    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('auth'))
    
    active_session = user.get_active_mining_session()
    announcements = Announcement.query.filter_by(is_active=True).order_by(Announcement.created_at.desc()).limit(5).all()
    payment_settings = PaymentSettings.get_settings()
    
    return render_template('mining.html', user=user, active_session=active_session, announcements=announcements, payment_settings=payment_settings)

@app.route('/start_mining', methods=['POST'])
def start_mining():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if not user.can_start_mining():
        return jsonify({'error': 'Must wait 24 hours between mining sessions'}), 400
    
    # Create new mining session
    mining_session = MiningSession(user_id=user.id)
    db.session.add(mining_session)
    db.session.commit()
    
    return jsonify({'success': True, 'session_id': mining_session.id})

@app.route('/mining_status')
def mining_status():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = User.query.get(session['user_id'])
    active_session = user.get_active_mining_session()
    
    if not active_session:
        return jsonify({'active': False})
    
    progress = active_session.get_progress()
    time_remaining = active_session.get_time_remaining()
    
    # Auto-complete if time is up
    if progress >= 100 and active_session.is_active:
        active_session.complete_mining()
        return jsonify({'active': False, 'completed': True})
    
    return jsonify({
        'active': True,
        'progress': progress,
        'time_remaining': time_remaining
    })

@app.route('/upgrade_plan', methods=['POST'])
def upgrade_plan():
    if 'user_id' not in session:
        return redirect(url_for('auth'))
    
    user = User.query.get(session['user_id'])
    amount = float(request.form.get('amount', 0))
    
    settings = PaymentSettings.get_settings()
    
    if amount < settings.min_amount or amount > settings.max_amount:
        flash(f'Amount must be between ${settings.min_amount} and ${settings.max_amount}', 'error')
        return redirect(url_for('profile'))
    
    # Handle file upload
    screenshot_path = None
    if 'screenshot' in request.files:
        file = request.files['screenshot']
        if file and file.filename:
            import os
            import uuid
            from werkzeug.utils import secure_filename
            
            # Create uploads directory if it doesn't exist
            upload_dir = 'static/uploads'
            os.makedirs(upload_dir, exist_ok=True)
            
            # Generate unique filename
            file_ext = os.path.splitext(secure_filename(file.filename))[1]
            filename = f"{uuid.uuid4()}{file_ext}"
            screenshot_path = os.path.join(upload_dir, filename)
            file.save(screenshot_path)
            
            # Store relative path for template rendering
            screenshot_path = f"uploads/{filename}"
    
    # Create deposit record
    deposit = Deposit(
        user_id=user.id,
        amount=amount,
        screenshot_path=screenshot_path
    )
    db.session.add(deposit)
    db.session.commit()
    
    flash('Upgrade request submitted successfully! Wait for admin approval (24-48 hours).', 'success')
    return redirect(url_for('profile'))

@app.route('/wallet')
def wallet():
    if 'user_id' not in session:
        return redirect(url_for('auth'))
    
    user = User.query.get(session['user_id'])
    return render_template('wallet.html', user=user)

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('auth'))
    
    user = User.query.get(session['user_id'])
    mining_logs = MiningSession.query.filter_by(user_id=user.id).order_by(MiningSession.created_at.desc()).limit(10).all()
    referrals = User.query.filter_by(referred_by=user.id).all()
    announcements = Announcement.query.filter_by(is_active=True).order_by(Announcement.created_at.desc()).limit(5).all()
    payment_settings = PaymentSettings.get_settings()
    
    return render_template('profile.html', user=user, mining_logs=mining_logs, referrals=referrals, announcements=announcements, payment_settings=payment_settings)

# Admin Routes
@app.route('/admin')
def admin_login():
    return render_template('admin.html')

@app.route('/admin/login', methods=['POST'])
def admin_login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    
    admin = AdminUser.query.filter_by(email=email).first()
    if admin and admin.check_password(password):
        session['admin_id'] = admin.id
        return redirect(url_for('admin_dashboard'))
    
    flash('Invalid admin credentials', 'error')
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    # Get statistics
    total_users = User.query.count()
    total_deposits = Deposit.query.count()
    pending_deposits = Deposit.query.filter_by(status='pending').count()
    today_mining = MiningSession.query.filter(
        MiningSession.created_at >= datetime.utcnow().date()
    ).count()
    
    users = User.query.order_by(User.created_at.desc()).all()
    deposits = Deposit.query.order_by(Deposit.created_at.desc()).all()
    payment_settings = PaymentSettings.get_settings()
    
    return render_template('admin.html', 
                         admin_dashboard=True,
                         total_users=total_users,
                         total_deposits=total_deposits,
                         pending_deposits=pending_deposits,
                         today_mining=today_mining,
                         users=users,
                         deposits=deposits,
                         payment_settings=payment_settings)

@app.route('/admin/approve_deposit/<int:deposit_id>')
def approve_deposit(deposit_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    deposit = Deposit.query.get_or_404(deposit_id)
    deposit.status = 'approved'
    deposit.approved_at = datetime.utcnow()
    deposit.approved_by = session['admin_id']
    
    # Update user plan
    user = deposit.user
    payment_settings = PaymentSettings.get_settings()
    user.plan_type = 'paid'
    user.plan_amount = deposit.amount
    user.daily_reward = deposit.amount * payment_settings.reward_multiplier
    
    db.session.commit()
    flash('Deposit approved successfully', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/reject_deposit/<int:deposit_id>')
def reject_deposit(deposit_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    deposit = Deposit.query.get_or_404(deposit_id)
    deposit.status = 'rejected'
    
    db.session.commit()
    flash('Deposit rejected', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    return redirect(url_for('admin_login'))

@app.route('/admin/upgrade_user/<int:user_id>', methods=['POST'])
def admin_upgrade_user(user_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    try:
        user = User.query.get_or_404(user_id)
        
        # Set default paid plan values
        payment_settings = PaymentSettings.get_settings()
        user.plan_type = 'paid'
        user.plan_amount = 50.0  # Default upgrade amount
        user.daily_reward = 50.0 * payment_settings.reward_multiplier
        
        db.session.commit()
        flash(f'User {user.name} upgraded to paid plan successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Failed to upgrade user plan', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/downgrade_user/<int:user_id>', methods=['POST'])
def admin_downgrade_user(user_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    try:
        user = User.query.get_or_404(user_id)
        
        # Reset to free plan
        user.plan_type = 'free'
        user.plan_amount = 0.0
        user.daily_reward = 0.5  # Default free plan reward
        
        db.session.commit()
        flash(f'User {user.name} downgraded to free plan successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Failed to downgrade user plan', 'error')
    
    return redirect(url_for('admin_dashboard'))

# Removed problematic payment settings route - functionality is now in admin dashboard

@app.route('/admin/update_payment_settings', methods=['POST'])
def admin_update_payment_settings():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    try:
        settings = PaymentSettings.get_settings()
        
        settings.usdt_address = request.form.get('usdt_address', settings.usdt_address)
        settings.qr_code_url = request.form.get('qr_code_url', settings.qr_code_url)
        settings.network = request.form.get('network', settings.network)
        settings.min_amount = float(request.form.get('min_amount', settings.min_amount))
        settings.max_amount = float(request.form.get('max_amount', settings.max_amount))
        settings.reward_multiplier = float(request.form.get('reward_multiplier', settings.reward_multiplier))
        settings.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('Payment settings updated successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Failed to update payment settings', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/edit_user_plan/<int:user_id>', methods=['POST'])
def admin_edit_user_plan(user_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    try:
        user = User.query.get_or_404(user_id)
        
        plan_type = request.form.get('plan_type', 'free')
        daily_reward = float(request.form.get('daily_reward', 0.5))
        plan_amount = float(request.form.get('plan_amount', 0.0))
        
        user.plan_type = plan_type
        user.daily_reward = daily_reward
        user.plan_amount = plan_amount
        
        db.session.commit()
        flash(f'User {user.name} plan updated successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Failed to update user plan', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/edit_user_balance/<int:user_id>', methods=['POST'])
def admin_edit_user_balance(user_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    try:
        user = User.query.get_or_404(user_id)
        
        new_balance = float(request.form.get('balance', 0.0))
        user.balance = new_balance
        
        db.session.commit()
        flash(f'User {user.name} balance updated to {new_balance} OXC!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Failed to update user balance', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/update_plan_settings', methods=['POST'])
def admin_update_plan_settings():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    try:
        plan_type = request.form.get('plan_type')
        
        if plan_type == 'free':
            daily_reward = float(request.form.get('daily_reward', 0.5))
            fragments_per_coin = int(request.form.get('fragments_per_coin', 1000))
            flash(f'Free plan settings updated: {daily_reward} OXC daily, {fragments_per_coin} fragments per coin', 'success')
        
        elif plan_type == 'paid':
            reward_multiplier = float(request.form.get('reward_multiplier', 1.2))
            fragments_per_coin = int(request.form.get('fragments_per_coin', 800))
            
            # Update payment settings with new multiplier
            settings = PaymentSettings.get_settings()
            settings.reward_multiplier = reward_multiplier
            db.session.commit()
            
            flash(f'Paid plan settings updated: {reward_multiplier}x multiplier, {fragments_per_coin} fragments per coin', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Failed to update plan settings', 'error')
    
    return redirect(url_for('admin_dashboard'))

# Template filters
@app.template_filter('timeago')
def timeago(dt):
    if not dt:
        return ''
    
    now = datetime.utcnow()
    diff = now - dt
    
    if diff.days > 0:
        return f"{diff.days} days ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hours ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minutes ago"
    else:
        return "Just now"

@app.template_filter('format_seconds')
def format_seconds(seconds):
    if seconds <= 0:
        return "00:00:00"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('static/uploads', filename)
