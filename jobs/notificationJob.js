const { scheduleJob } = require('node-schedule');
const Event = require('../models/Event');
const mailService = require('../services/mailService');

module.exports = {
    start: () => {
        // Ejecutar diariamente a las 00:05
        scheduleJob('5 0 * * *', async () => {
            try {
                const events = await Event.getUpcomingEvents();
                for (const event of events) {
                    const users = await User.getAllUsers();
                    for (const user of users) {
                        await mailService.sendNotification(
                            user.email,
                            event.name,
                            event.event_date
                        );
                    }
                }
            } catch (error) {
                console.error('Error en notificationJob:', error);
            }
        });
    }
};