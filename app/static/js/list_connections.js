document.addEventListener('DOMContentLoaded', function () {
    let previousStates = {};

    async function fetchConnections() {
        try {
            const response = await fetch('/storage/connections', {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (response.ok) {
                const connections = await response.json();
                const connectionsTable = document.querySelector('#connectionsTableBody');

                if (!connectionsTable) {
                    console.error('El elemento #connectionsTableBody no existe en el DOM.');
                    return;
                }

                connectionsTable.innerHTML = '';

                connections.forEach(connection => {
                    const row = document.createElement('tr');
                    row.classList.add('clickable-row');
                    row.setAttribute('data-url', `/storage/${connection.type}/${connection.id}/list`);
                    row.innerHTML = `
                        <td>
                            <span class="status-dot ${
                                connection.status === 'mount' ? 'bg-success blinking' :
                                connection.status === 'success' ? 'bg-success' :
                                connection.status === 'error' ? 'bg-danger' : 'bg-warning'
                            }"></span>
                        </td>
                        <td>${connection.name}</td>
                        <td>${connection.type.charAt(0).toUpperCase() + connection.type.slice(1)}</td>
                        <td>
                            <div class="dropdown">
                                <button class="btn btn-sm btn-secondary dropdown-toggle" type="button" id="dropdownMenuButton${connection.id}" data-bs-toggle="dropdown" aria-expanded="false">
                                    <i class="bi bi-three-dots-vertical"></i>
                                </button>
                                <ul class="dropdown-menu" aria-labelledby="dropdownMenuButton${connection.id}">
                                    <li><a class="dropdown-item mount-folder" href="#" data-id="${connection.id}">${connection.status === 'mount' ? 'Desmontar' : 'Montar'}</a></li>
                                    <li><a class="dropdown-item edit-connection" href="#" data-id="${connection.id}">Editar</a></li>
                                    <li><a class="dropdown-item delete-connection" href="#" data-id="${connection.id}" data-type="${connection.type}">Borrar</a></li>
                                </ul>
                            </div>
                        </td>
                    `;
                    connectionsTable.appendChild(row);
                });

                // Manejar las acciones del menú desplegable
                document.querySelectorAll('.mount-folder').forEach(item => {
                    item.addEventListener('click', async function (event) {
                        event.preventDefault();
                        const connectionId = this.getAttribute('data-id');
                        try {
                            const mountResponse = await fetch(`/storage/mount/${connectionId}`, {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json'
                                }
                            });
                            if (mountResponse.ok) {
                                showToast('success', 'Operación de montaje/desmontaje realizada con éxito.');
                                fetchConnections(); // Actualizar la lista de conexiones
                            } else {
                                showToast('error', 'Error al realizar la operación de montaje/desmontaje.');
                            }
                        } catch (error) {
                            console.error('Error al montar/desmontar la carpeta:', error);
                            showToast('error', 'Error inesperado al realizar la operación.');
                        }
                    });
                });

                document.querySelectorAll('.edit-connection').forEach(item => {
                    item.addEventListener('click', function (event) {
                        event.preventDefault();
                        const connectionId = this.getAttribute('data-id');
                        alert(`Editar conexión con ID: ${connectionId}`);
                        // Aquí puedes implementar la lógica para editar la conexión
                    });
                });

                document.querySelectorAll('.delete-connection').forEach(item => {
                    item.addEventListener('click', async function (event) {
                        event.preventDefault();
                        const connectionId = this.getAttribute('data-id');
                        const connectionType = this.getAttribute('data-type'); // Obtener el tipo de conexión
                        if (confirm('¿Estás seguro de que deseas borrar esta conexión?')) {
                            try {
                                const deleteResponse = await fetch(`/storage/${connectionType}/${connectionId}/delete`, {
                                    method: 'DELETE',
                                    headers: {
                                        'Content-Type': 'application/json'
                                    }
                                });
                                if (deleteResponse.ok) {
                                    showToast('success', 'Conexión borrada con éxito.');
                                    fetchConnections(); // Actualizar la lista de conexiones
                                } else {
                                    showToast('error', 'Error al borrar la conexión.');
                                }
                            } catch (error) {
                                console.error('Error al borrar la conexión:', error);
                                showToast('error', 'Error inesperado al borrar la conexión.');
                            }
                        }
                    });
                });

                // Verificar cambios de estado
                connections.forEach(connection => {
                    if (previousStates[connection.id] && previousStates[connection.id] !== connection.status) {
                        showToast('success', `La conexión "${connection.name}" cambió de estado: ${connection.status}`);
                    }
                    previousStates[connection.id] = connection.status;
                });
            } else {
                console.error('Error al obtener las conexiones:', response.statusText);
            }
        } catch (error) {
            console.error('Error al realizar la solicitud:', error);
        } finally {
            // Esperar 5 segundos antes de realizar la siguiente llamada
            setTimeout(fetchConnections, 5000);
        }
    }

    function showToast(type, message) {
        const toast = type === 'success' ? document.getElementById('successToast') : document.getElementById('errorToast');
        const toastBody = type === 'success' ? document.getElementById('successToastBody') : document.getElementById('errorToastBody');
        if (toast && toastBody) {
            toastBody.textContent = message;
            const bootstrapToast = new bootstrap.Toast(toast);
            bootstrapToast.show();
        } else {
            console.error('No se encontró el elemento del toast.');
        }
    }

    // Llamar a fetchConnections al cargar la página
    fetchConnections();
});