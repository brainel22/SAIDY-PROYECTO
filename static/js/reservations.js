// Configuración inicial al cargar la página
document.addEventListener('DOMContentLoaded', function () {
    // Obtener fecha actual en formato YYYY-MM-DD
    const today = new Date();
    const todayStr = today.toISOString().split('T')[0];

    // 1. Configurar campo visible (date_false)
    const dateVisible = document.getElementById('date_false');
    dateVisible.min = todayStr;

    // 2. Configurar campo oculto (date) con fecha actual
    const dateHidden = document.getElementById('date');
    dateHidden.value = todayStr; // Siempre guardará la fecha actual

    // 3. Configurar campo de pago (payment_date)
    const paymentDate = document.getElementById('payment_date');
    paymentDate.min = todayStr;
    paymentDate.value = todayStr;

    // Si hay una fecha de evento, mostrarla en el campo visible
    if (dateVisible.dataset.eventDate) {
        dateVisible.value = dateVisible.dataset.eventDate;
    }
});

// Validación del formulario
document.querySelector('form').addEventListener('submit', function (e) {
    const dateVisible = document.getElementById('date_false');
    const today = new Date().toISOString().split('T')[0];

    // Validar que se haya seleccionado fecha visible
    if (!dateVisible.value) {
        alert('Debes seleccionar una fecha para el evento');
        e.preventDefault();
        return;
    }

    // Validar que la fecha visible no sea anterior a hoy
    if (dateVisible.value < today) {
        alert('La fecha del evento no puede ser anterior a hoy');
        e.preventDefault();
        return;
    }

    // El campo oculto 'date' ya tiene la fecha actual y siempre será válido
});

// Formatear número de tarjeta (manteniendo espacios cada 4 dígitos)
document.getElementById('card_number').addEventListener('input', function (e) {
    this.value = this.value.replace(/\s/g, '')
        .replace(/(\d{4})/g, '$1 ')
        .trim();
});

// Validar CVV (solo números, máximo 4 dígitos)
document.getElementById('card_cvv').addEventListener('input', function (e) {
    this.value = this.value.replace(/\D/g, '')
        .substring(0, 4);
});

// Cerrar alertas con animación
document.querySelectorAll('.close').forEach(button => {
    button.addEventListener('click', function () {
        this.parentElement.style.transition = 'all 0.3s ease';
        this.parentElement.style.opacity = '0';
        setTimeout(() => {
            this.parentElement.remove();
        }, 300);
    });
});

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