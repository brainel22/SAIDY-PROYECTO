const nodemailer = require('nodemailer');
const transporter = require('../config/mail');

module.exports = {
    sendWelcomeEmail: async (email) => {
        try {
            await transporter.sendMail({
                from: process.env.MAIL_FROM,
                to: email,
                subject: 'Bienvenido a Boolings',
                text: 'Gracias por registrarte en nuestro sistema!'
            });
        } catch (error) {
            console.error('Error enviando email:', error);
        }
    },

    sendNotification: async (email, eventName, eventDate) => {
        // Implementación similar
    }
};