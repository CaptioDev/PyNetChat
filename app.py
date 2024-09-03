from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import xml.etree.ElementTree as ET
from flask_socketio import SocketIO, send, emit
import nmap # Yeah so this is a dependency, please do not forget to make people install this... Yeah.

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

DATA_FILE = 'data.xml'

# Ensure data.xml exists
if not os.path.exists(DATA_FILE):
    root = ET.Element('network_messenger')
    tree = ET.ElementTree(root)
    tree.write(DATA_FILE)


def get_tree():
    return ET.parse(DATA_FILE)


def save_tree(tree):
    tree.write(DATA_FILE)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/scan')
def scan():
    # Scan using nmap (more secure than socket.socket, also socket.socket didn't work sooooo, yeah.)
    nm = nmap.PortScanner()
    results = nm.scan(arguments='-sn 192.168.1.0/24')  # Scan subnet with -sn for ping sweep

    scanned_ips = []
    if results['scan'] is not None:
        for host, info in results['scan'].hosts.items():
            if info['status']['state'] == 'up':
                scanned_ips.append(host)

    return render_template('scan.html', scanned_ips=scanned_ips)


@app.route('/messages')
def messages():
    tree = get_tree()
    root = tree.getroot()
    conversations = {}
    for ip_section in root.findall('ip'):
        ip = ip_section.get('address')
        nickname = ip_section.find('nickname').text
        messages = [msg.text for msg in ip_section.find('messages').findall('message')]
        conversations[ip] = {'nickname': nickname, 'messages': messages}
    return render_template('messages.html', conversations=conversations)


@app.route('/file_transfer', methods=['GET', 'POST'])
def file_transfer():
    if request.method == 'POST':
        recipient_ip = request.form['recipient_ip']
        file = request.files['file']
        filename = file.filename

        # Validate filename to prevent security issues
        allowed_extensions = {'txt', 'pdf', 'jpg', 'png', 'doc', 'docx'}
        if filename.split('.')[-1].lower() not in allowed_extensions:
            return redirect(url_for('file_transfer', error="Invalid file type"))

        filepath = os.path.join('uploads', filename)
        file.save(filepath)

        # Logic to send file to recipient (handled by WebSocket)
        socketio.emit('file_transfer', {'filename': filename, 'filepath': filepath}, to=recipient_ip)
        return redirect(url_for('file_transfer'))
    return render_template('file_transfer.html')


@app.route('/mail')
def mail():
    return render_template('mail.html')


@socketio.on('connect')
def handle_connect():
    ip_address = request.remote_addr
    emit('connected', {'ip': ip_address})


@socketio.on('send_message')
def handle_send_message(data):
    ip = data['ip']
    message = data['message']
    tree = get_tree()
    root = tree.getroot()
    ip_section = root.find(f"./ip[@address='{ip}']")
    if ip_section is None:
        ip_section = ET.SubElement(root, 'ip', {'address': ip})
        nickname = ET.SubElement(ip_section, 'nickname')
        nickname.text = f"User {ip}"  # Default nickname
        messages_section = ET.SubElement(ip_section, 'messages')
    else:
        messages_section = ip_section.find('messages')
    new_message = ET.SubElement(messages_section, 'message')
    new_message.text = message
    save_tree(tree)