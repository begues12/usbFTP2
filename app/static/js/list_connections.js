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
                            <span 
                                class="status-dot ${
                                    connection.status === 'mount' ? 'bg-success blinking' :
                                    connection.status === 'success' ? 'bg-success' :
                                    connection.status === 'error' ? 'bg-danger' : 'bg-warning'
                                }"
                                data-bs-toggle="tooltip"
                                title="<div class='d-flex align-items-center'>
                                    <span class='status-dot ${
                                        connection.status === 'mount' ? 'bg-success blinking' :
                                        connection.status === 'success' ? 'bg-success' :
                                        connection.status === 'error' ? 'bg-danger' : 'bg-warning'
                                    } me-2'></span>
                                    ${connection.status === 'mount' ? 'Montado' :
                                        connection.status === 'success' ? 'Conexión exitosa' :
                                        connection.status === 'error' ? 'Error en la conexión' : 'Pendiente'}
                                </div>">
                            </span>
                            ${connection.name}
                        </td>
                        <td>${connection.type.charAt(0).toUpperCase() + connection.type.slice(1)}</td>
                        <td class="text-right justify-content-end">
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

                // Inicializar tooltips de Bootstrap
                const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
                tooltipTriggerList.forEach(function (tooltipTriggerEl) {
                    new bootstrap.Tooltip(tooltipTriggerEl, {
                        html: true // Permitir HTML en los tooltips
                    });
                });

                // Manejar clics en filas, excepto en el menú desplegable
                document.querySelectorAll('.clickable-row').forEach(row => {
                    row.addEventListener('click', function (event) {
                        // Evitar que el clic en el menú desplegable active la redirección
                        if (event.target.closest('.dropdown')) {
                            return;
                        }
                        const url = this.getAttribute('data-url');
                        if (url) {
                            window.location.href = url; // Redirigir a la URL
                        }
                    });
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
                                showModal('success', 'Operación de montaje/desmontaje realizada con éxito.');
                                fetchConnections(); // Actualizar la lista de conexiones
                            } else {
                                showModal('error', 'Error al realizar la operación de montaje/desmontaje.');
                            }
                        } catch (error) {
                            showModal('error', 'Error inesperado al realizar la operación de montaje/desmontaje.');
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
                    item.addEventListener('click', function (event) {
                        event.preventDefault();
                        const connectionId = this.getAttribute('data-id'); // Obtener el ID de la conexión
                
                        // Mostrar el modal de confirmación
                        showConfirmModal(
                            'Confirmar eliminación',
                            '¿Estás seguro de que deseas borrar esta conexión?',
                            async () => {
                                try {
                                    // Realizar la solicitud para eliminar la conexión
                                    const deleteResponse = await fetch(`/storage/delete_connection/${connectionId}`, {
                                        method: 'POST',
                                        headers: {
                                            'Content-Type': 'application/json'
                                        }
                                    });
                
                                    if (deleteResponse.ok) {
                                        showModal('success', 'Conexión borrada con éxito.');
                                        fetchConnections(); // Actualizar la lista de conexiones
                                    } else {
                                        const errorData = await deleteResponse.json();
                                        showModal('error', errorData.error || 'Error al borrar la conexión.');
                                    }
                                } catch (error) {
                                    showModal('error', 'Error inesperado al borrar la conexión.');
                                }
                            }
                        );
                    });
                });

                // Verificar cambios de estado
                connections.forEach(connection => {
                    if (previousStates[connection.id] && previousStates[connection.id] !== connection.status) {
                        showModal('success', `La conexión "${connection.name}" cambió de estado: ${connection.status}`);
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

    // Llamar a fetchConnections al cargar la página
    fetchConnections();
});