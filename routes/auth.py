from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database.db import get_db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE email=? AND password=?', (email, password)).fetchone()
        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_role'] = user['role']
            return redirect(url_for('main.dashboard'))
        flash('Invalid email or password.', 'error')
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        phone = request.form.get('phone', '')
        location = request.form.get('location', '')
        db = get_db()
        existing = db.execute('SELECT id FROM users WHERE email=?', (email,)).fetchone()
        if existing:
            flash('Email already registered.', 'error')
            return render_template('register.html')
        db.execute('INSERT INTO users (name, email, password, role, phone, location) VALUES (?,?,?,?,?,?)',
                   (name, email, password, role, phone, location))
        db.commit()
        user = db.execute('SELECT * FROM users WHERE email=?', (email,)).fetchone()
        if role == 'volunteer':
            skills = request.form.get('skills', '')
            db.execute('INSERT INTO volunteers (user_id, skills) VALUES (?,?)', (user['id'], skills))
            db.commit()
        session['user_id'] = user['id']
        session['user_name'] = user['name']
        session['user_role'] = user['role']
        return redirect(url_for('main.dashboard'))
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
