from flask import render_template, request, redirect, url_for, session, flash, jsonify
from app import app, db
from models import User, MiningSession, Deposit, AdminUser, Announcement
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
        
        # Validate input
        if not all([data.get('name'), data.get('email'), data.get('password'), data.get('country')]):
            flash('All fields are required', 'error')
            return redirect(url_for('auth'))
        
        # Check if user exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            flash('Email already registered', 'error')
            return redirect(url_for('auth'))
        
        # Create new user
        user = User(
            name=data['name'],
            email=data['email'],
            country=data['country']
        )
        user.set_password(data['password'])
        
        # Handle referral
        if data.get('referral_code'):
            referrer = User.query.filter_by(referral_code=data['referral_code']).first()
            if referrer:
                user.referred_by = referrer.id
        
        db.session.add(user)
        db.session.commit()
        
        session['user_id'] = user.id
        flash('Registration successful!', 'success')
        return redirect(url_for('mining'))
        
    except Exception as e:
        flash(f'Registration failed: {str(e)}', 'error')
        return redirect(url_for('auth'))

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.form
        
        user = User.query.filter_by(email=data['email']).first()
        if user and user.check_password(data['password']):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('mining'))
        else:
            flash('Invalid email or password', 'error')
            return redirect(url_for('auth'))
            
    except Exception as e:
        flash(f'Login failed: {str(e)}', 'error')
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
    
    return render_template('mining.html', user=user, active_session=active_session, announcements=announcements)

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
    
    if amount <= 0:
        flash('Invalid amount', 'error')
        return redirect(url_for('mining'))
    
    # Create deposit record
    deposit = Deposit(
        user_id=user.id,
        amount=amount
    )
    db.session.add(deposit)
    db.session.commit()
    
    flash('Upgrade request submitted. Please upload payment screenshot.', 'info')
    return redirect(url_for('mining'))

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
    
    return render_template('profile.html', user=user, mining_logs=mining_logs, referrals=referrals, announcements=announcements)

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
    
    return render_template('admin.html', 
                         admin_dashboard=True,
                         total_users=total_users,
                         total_deposits=total_deposits,
                         pending_deposits=pending_deposits,
                         today_mining=today_mining,
                         users=users,
                         deposits=deposits)

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
    user.plan_type = 'paid'
    user.plan_amount = deposit.amount
    user.daily_reward = deposit.amount * 1.2  # 1.2x multiplier
    
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
