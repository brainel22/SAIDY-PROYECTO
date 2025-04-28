module.exports = {
    secret: process.env.SESSION_SECRET || 'tu-secreto-seguro',
    resave: false,
    saveUninitialized: true,
    cookie: { secure: false } // Cambiar a true si usas HTTPS
};