const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const fs = require('fs');

const app = express();
const server = http.createServer(app);
const io = socketIo(server);

const config = JSON.parse(fs.readFileSync('config.json', 'utf8'));

// Store last 100 messages in memory
let last100Messages = [];

app.get('/', (req, res) => {
    res.redirect('/chat');
});

app.get('/chat', (req, res) => {
    res.sendFile(__dirname + '/templates/chat.html');
});

app.get('/sign-in', (req, res) => {
    res.sendFile(__dirname + '/templates/signin.html');
});

app.get('/sign-up', (req, res) => {
    res.sendFile(__dirname + '/templates/signup.html');
});

app.get('/config', (req, res) => {
    res.json(config);
});

io.on('connection', (socket) => {
    console.log('A user connected');
    socket.emit('load messages', last100Messages);
    socket.on('chat message', (msg) => {
        const fullMessage = { text: msg.text, user: msg.user, timestamp: new Date() };
        if (last100Messages.length >= 100) {
            last100Messages.shift();
        }
        last100Messages.push(fullMessage);
        io.emit('chat message', fullMessage);
    });
    socket.on('disconnect', () => {
        console.log('User disconnected');
    });
});

server.listen(3000, () => {
    console.log('Listening on *:3000');
});
