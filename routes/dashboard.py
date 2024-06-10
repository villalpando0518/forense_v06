#Dashboard file
from flask import render_template, redirect, url_for, session

def dashboard():
    if 'username' in session:
        username = session['username']
        return render_template('dashboard.html', username=username)
    else:
        flash('You need to be logged in to access the dashboard.')
        return redirect(url_for('login'))
