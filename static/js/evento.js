const searchInput = document.getElementById('searchInput');
const searchResults = document.getElementById('searchResults');

searchInput.addEventListener('input', function () {
    const query = this.value.trim();
    if (query === '') {
        searchResults.innerHTML = '';
        return;
    }
    fetch('/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `query=${query}`
    })
        .then(response => response.json())
        .then(data => {
            searchResults.innerHTML = '';
            data.forEach(result => {
                const li = document.createElement('li');
                li.textContent = result.columna; // Cambia 'columna' por el nombre de la columna que deseas mostrar
                searchResults.appendChild(li);
            });
        })
        .catch(error => console.error('Error:', error));
});

