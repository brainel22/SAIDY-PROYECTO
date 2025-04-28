const express = require('express');
const router = express.Router();
const authController = require('./controllers/authController');

router.get('/register', authController.showRegisterForm);
router.post('/register', authController.register);

module.exports = router;