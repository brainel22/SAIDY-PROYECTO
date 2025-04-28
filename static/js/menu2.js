window.onload = function () {
    alert("¡Bienvenido a nuestra página!");
};

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
