require('dotenv').config();
const express = require('express');
const path = require('path');
const bodyParser = require('body-parser');
const session = require('express-session');
const flash = require('connect-flash');

const app = express();

// Configuración básica
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'ejs');

// Middlewares
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, 'public')));
app.use(session(require('./config/session')));
app.use(flash());

// Rutas
app.use('/', require('./routes/index'));
app.use('/auth', require('./routes/authRoutes'));
app.use('/events', require('./routes/eventRoutes'));

// Iniciar servidor
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Servidor corriendo en http://localhost:${PORT}`);
    require('./jobs/notificationJob').start(); // Iniciar jobs
});