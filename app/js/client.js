var socket = io();

socket.on('user_joined', function(username) {
    // Handle user joined event
});

socket.on('message_received', function(data) {
    // Handle message received event
});

function sendMessage() {
    var message = document.getElementById('message').value;
    socket.emit('message', { message: message });
    document.getElementById('message').value = '';
}