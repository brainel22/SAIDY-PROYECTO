document.addEventListener("DOMContentLoaded", function () {
    // Hacer la solicitud AJAX para obtener los datos
    fetch('/reservas_json')
        .then(response => response.json())
        .then(data => {
            // Obtener los nombres de los eventos y el número total de tickets reservados
            const eventos = data.map(reserva => reserva.name);
            const ticketsReservados = data.map(reserva => reserva.total_tickets);

            // Configurar el gráfico de barras
            var ctx = document.getElementById('myChart').getContext('2d');
            var myChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: eventos,
                    datasets: [{
                        label: 'Número de Tickets Reservados por Evento',
                        data: ticketsReservados,
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error al obtener los datos de las reservas:', error);
        });
});
