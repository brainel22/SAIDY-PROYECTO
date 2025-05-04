document.addEventListener('DOMContentLoaded', function () {
    // Cerrar mensajes al hacer clic en el botón de cerrar
    document.querySelectorAll('.close-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const message = this.closest('.flash-message');
            message.style.animation = 'fadeOut 0.5s forwards';
            setTimeout(() => message.remove(), 500);
        });
    });

    // Eliminar mensajes automáticamente después de 5 segundos
    document.querySelectorAll('.flash-message').forEach(message => {
        setTimeout(() => {
            message.style.animation = 'fadeOut 0.5s forwards';
            setTimeout(() => message.remove(), 500);
        }, 5000);
    });

    // Esto es un ejemplo, necesitarías adaptarlo a cómo Flask envía los mensajes
    document.querySelectorAll('.flash-message').forEach(message => {
        const text = message.textContent.trim().toLowerCase();
        if (text.includes('error') || text.includes('fail')) {
            message.classList.add('error');
        } else if (text.includes('success') || text.includes('éxito')) {
            message.classList.add('success');
        } else if (text.includes('warning') || text.includes('advertencia')) {
            message.classList.add('warning');
        } else {
            message.classList.add('info');
        }
    });
});