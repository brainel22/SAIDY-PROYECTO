document.addEventListener('DOMContentLoaded', function () {
    // Manejar clic en botones de favorito
    document.querySelectorAll('.favorite-btn').forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            const eventId = this.getAttribute('data-event-id');
            toggleFavorite(eventId, this);
        });
    });

    // Verificar estado inicial de favoritos
    checkFavorites();
});

function toggleFavorite(eventId, button) {
    fetch('/add_favorite', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `event_id=${eventId}`
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Actualizar el botón
                const icon = button.querySelector('i');
                if (data.action === 'added') {
                    button.classList.add('active');
                    icon.classList.replace('bx-heart', 'bxs-heart');
                    button.innerHTML = '<i class="bx bxs-heart nav__icon"></i> En favoritos';
                } else {
                    button.classList.remove('active');
                    icon.classList.replace('bxs-heart', 'bx-heart');
                    button.innerHTML = '<i class="bx bx-heart nav__icon"></i> Favorito';
                }

                // Mostrar notificación
                showNotification(data.message);

                // Actualizar el historial de favoritos
                updateFavoritesList();
            } else {
                showNotification(data.message || 'Error al actualizar');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Error de conexión');
        });
}

function updateFavoritesList() {
    fetch('/historial')
        .then(response => response.text())
        .then(html => {
            // Actualizar solo la sección de historial
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const newContent = doc.querySelector('.historial-items').innerHTML;
            document.querySelector('.historial-items').innerHTML = newContent;
        })
        .catch(error => {
            console.error('Error al actualizar historial:', error);
        });
}

function showNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 3000);
}

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

    // Opcional: Añadir clases según el tipo de mensaje (necesitarías modificar tu backend)
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

// Mostrar alerta personalizada
document.getElementById('searchbox').addEventListener('keyup', function () {
    const query = this.value;

    fetch('/search', {
        method: 'POST',
        body: new URLSearchParams('search=' + query),
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
    })
        .then(response => response.json())
        .then(data => {
            const resultsContainer = document.getElementById('results');
            resultsContainer.innerHTML = '';
            data.forEach(item => {
                const li = document.createElement('li');
                li.textContent = item[0];
                resultsContainer.appendChild(li);
            });
        })
        .catch(error => console.error('Error:', error));
});

document.addEventListener("DOMContentLoaded", function () {
    const inicioText = document.querySelector('.inicio');
    inicioText.innerHTML = inicioText.textContent.replace(/\S/g, "<span>$&</span>");

    const spans = inicioText.querySelectorAll('span');
    spans.forEach((span, index) => {
        span.style.animationDelay = `${index * 50}ms`;
    });

    // Hacer visible el texto gradualmente
    setTimeout(() => {
        inicioText.parentElement.style.opacity = 1;
    }, 100);
});
