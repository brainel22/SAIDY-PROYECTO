const bcrypt = require('bcryptjs');
const { pool } = require('../config/database');
const mailService = require('../services/mailService');

module.exports = {
    showLoginForm: (req, res) => {
        res.render('login/login');
    },

    login: async (req, res) => {
        const { email, password } = req.body;

        try {
            const [rows] = await pool.execute(
                'SELECT * FROM user WHERE email = ?',
                [email]
            );

            if (rows.length === 0) {
                req.flash('error', 'Usuario o contraseña incorrectos');
                return res.redirect('/auth/login');
            }

            const user = rows[0];
            const validPassword = await bcrypt.compare(password, user.password);

            if (!validPassword) {
                req.flash('error', 'Usuario o contraseña incorrectos');
                return res.redirect('/auth/login');
            }

            req.session.loggedIn = true;
            req.session.userId = user.id;
            req.session.roleId = user.id_role;
            req.session.username = user.username;

            // Redirección basada en roles
            if (user.id_role === 1) {
                return res.redirect('/admin/dashboard');
            } else if (user.id_role === 2) {
                return res.redirect('/profile');
            } else if (user.id_role === 3) {
                return res.redirect('/admin/events');
            }

        } catch (error) {
            console.error('Error en login:', error);
            req.flash('error', 'Error en el servidor');
            res.redirect('/auth/login');
        }
    },

    showResetRequestForm: (req, res) => {
        res.render('login/reset');
    },

    requestReset: async (req, res) => {
        const { email } = req.body;

        try {
            const [rows] = await pool.execute(
                'SELECT * FROM user WHERE email = ?',
                [email]
            );

            if (rows.length === 0) {
                req.flash('error', 'El correo no está registrado');
                return res.redirect('/auth/reset');
            }

            const resetToken = require('crypto').randomBytes(32).toString('hex');
            const expiresAt = new Date(Date.now() + 3600000); // 1 hora

            await pool.execute(
                'UPDATE user SET reset_token = ?, reset_token_expires = ? WHERE email = ?',
                [resetToken, expiresAt, email]
            );

            await mailService.sendResetEmail(email, resetToken);

            req.flash('success', 'Se ha enviado un correo con instrucciones');
            res.redirect('/auth/reset');

        } catch (error) {
            console.error('Error en reset request:', error);
            req.flash('error', 'Error al procesar la solicitud');
            res.redirect('/auth/reset');
        }
    },

    showResetForm: async (req, res) => {
        const { token } = req.params;

        try {
            const [rows] = await pool.execute(
                'SELECT * FROM user WHERE reset_token = ? AND reset_token_expires > NOW()',
                [token]
            );

            if (rows.length === 0) {
                req.flash('error', 'Token inválido o expirado');
                return res.redirect('/auth/reset');
            }

            res.render('login/change_password', { token });

        } catch (error) {
            console.error('Error verificando token:', error);
            req.flash('error', 'Error en el servidor');
            res.redirect('/auth/reset');
        }
    },

    resetPassword: async (req, res) => {
        const { token } = req.params;
        const { password } = req.body;

        try {
            const [rows] = await pool.execute(
                'SELECT * FROM user WHERE reset_token = ? AND reset_token_expires > NOW()',
                [token]
            );

            if (rows.length === 0) {
                req.flash('error', 'Token inválido o expirado');
                return res.redirect('/auth/reset');
            }

            const hashedPassword = await bcrypt.hash(password, 10);
            const userId = rows[0].id;

            await pool.execute(
                'UPDATE user SET password = ?, reset_token = NULL, reset_token_expires = NULL WHERE id = ?',
                [hashedPassword, userId]
            );

            req.flash('success', 'Contraseña restablecida correctamente');
            res.redirect('/auth/login');

        } catch (error) {
            console.error('Error resetting password:', error);
            req.flash('error', 'Error al restablecer la contraseña');
            res.redirect(`/auth/reset/${token}`);
        }
    },

    logout: (req, res) => {
        req.session.destroy(err => {
            if (err) {
                console.error('Error al cerrar sesión:', err);
            }
            res.redirect('/');
        });
    }
};