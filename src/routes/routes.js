const express = require('express');
const router = express.Router();

// Rutas aquí
router.get('/', (req, res) => {
    res.send('Ruta principal');
});

module.exports = router;