#Auth file
import sqlite3
from flask import render_template, request, flash, redirect, url_for, session
from db import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash


def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        pass_confirm = request.form['confirm_password']

        if not username or not password:
            flash('All fields are required!')
            return render_template('register.html')

        if password != pass_confirm:
            flash('Password dont match with each other')
            return render_template('register.html')

        # Hash the password (VERY IMPORTANT for security)
        hashed_password = generate_password_hash(password)  

        with get_db_connection() as conn:
            try:
                conn.execute(
                    'INSERT INTO users (username, password) VALUES (?, ?)',
                    (username, hashed_password)
                )
                conn.commit()
                flash('Registration successful!')
                return redirect(url_for('index'))  
            except sqlite3.IntegrityError:
                flash('Username already exists!')
                return render_template('register.html')
    else:
        return render_template('register.html')


def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with get_db_connection() as conn:
            user = conn.execute(
                'SELECT * FROM users WHERE username = ?', (username,)
            ).fetchone()

            if user and check_password_hash(user['password'], password):
                session['username'] = user['username']
                session['user_id'] = user['id']
                return redirect(url_for('dashboard'))   
            else:
                flash('Incorrect username or password.')

    return render_template('login.html')


