from flask import Flask, render_template, session, redirect, url_for
from flask_socketio import SocketIO, emit
from utils import db_utils

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

@app.route('/')
def index():
    if not db_utils.check_user_exists(session['username']):
        return render_template('login.html')
    return render_template('chat.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if db_utils.authenticate_user(username, password):
        session['username'] = username
        return redirect(url_for('index'))
    else:
        return render_template('login.html', error_message="Invalid username or password")

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    if db_utils.register_user(username, password):
        return redirect(url_for('index'))
    else:
        return render_template('login.html', error_message="Username already exists")

@socketio.on('connect')
def handle_connect():
    username = session['username']
    emit('user_joined', username)

@socketio.on('message')
def handle_message(data):
    username = session['username']
    message = data['message']
    emit('message_received', {'username': username, 'message': message})

if __name__ == '__main__':
    socketio.run(app)