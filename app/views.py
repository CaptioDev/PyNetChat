from flask import Blueprint, render_template, request, session, redirect, url_for

views = Blueprint('views', __name__)

@views.route('/')
def index():
    if not session.get('username'):
        return redirect(url_for('login'))
    return render_template('chat.html')

@views.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if db_utils.authenticate_user(username, password):
            session['username'] = username
            return redirect(url_for('views.index'))
        else:
            return render_template('login.html', error_message="Invalid username or password")
    return render_template('login.html')

@views.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if db_utils.register_user(username, password):
            return redirect(url_for('views.login'))
        else:
            return render_template('login.html', error_message="Username already exists")
    return render_template('login.html')