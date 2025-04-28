const { pool } = require('../config/database');

module.exports = {
    getAllUsers: async () => {
        const [rows] = await pool.query('SELECT email FROM user');
        return rows;
    },

    findByUsername: async (username) => {
        const [rows] = await pool.query(
            'SELECT * FROM user WHERE username = ?',
            [username]
        );
        return rows[0];
    }
};