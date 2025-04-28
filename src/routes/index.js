const express = require('express');
const router = express.Router();

// Importar otras rutas
const authRoutes = require('./authRoutes');
const eventRoutes = require('./eventRoutes');

// Rutas principales
router.get('/', (req, res) => {
    res.render('index');
});

// Usar las rutas adicionales
router.use('/auth', authRoutes);
router.use('/events', eventRoutes);

module.exports = router;