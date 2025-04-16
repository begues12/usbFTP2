document.addEventListener('DOMContentLoaded', function () {
    const refreshButton = document.getElementById('refreshConnectionsButton'); // Botón de "Actualizar"
    let previousStates = {};

    // Función para obtener y actualizar las conexiones
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
                            ${connection.credentials && connection.credentials.password ? 
                                '<i class="bi bi-lock-fill text-secondary ms-2" title="Protegido con contraseña"></i>' : ''}
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
                                    <li><a class="dropdown-item set-password" href="#" data-id="${connection.id}">Configurar Contraseña</a></li>
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

                document.querySelectorAll('.clickable-row').forEach(row => {
                    row.addEventListener('click', async function (event) {
                        if (event.target.closest('.dropdown')) {
                            return;
                        }
                        const url = this.getAttribute('data-url');
                        const connectionId = this.getAttribute('data-url').split('/')[3]; // Extraer el ID de la conexión
                
                        try {
                            // Obtener el token del almacenamiento local
                            const token = localStorage.getItem(`token_${connectionId}`);
                            if (!token) {
                                showModal('error', 'No se encontró un token válido. Por favor, ingrese la contraseña.');
                                return;
                            }
                
                            const response = await fetch(url, {
                                method: 'GET',
                                headers: {
                                    'Content-Type': 'application/json',
                                    'Authorization': token // Enviar el token en el encabezado
                                }
                            });
                
                            if (response.status === 403) {
                                showModal('error', 'Token inválido o expirado. Por favor, ingrese la contraseña nuevamente.');
                            } else if (response.ok) {
                                // Redirigir a la URL si el token es válido
                                window.location.href = url;
                            } else {
                                showModal('error', 'Error al abrir la conexión.');
                            }
                        } catch (error) {
                            console.error('Error al realizar la solicitud:', error);
                            showModal('error', 'Error inesperado al abrir la conexión.');
                        }
                    });
                });
                
                // Manejar el envío de la contraseña desde el modal
                document.getElementById('submitPasswordButton').addEventListener('click', async function () {
                    const connectionId = this.getAttribute('data-connection-id');
                    const password = document.getElementById('passwordInput').value;
                
                    try {
                        const response = await fetch(`/storage/submit_password`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({ connection_id: connectionId, password: password })
                        });
                
                        const data = await response.json();
                        if (response.ok) {
                            // Guardar el token en el almacenamiento local
                            localStorage.setItem(`token_${connectionId}`, data.token);
                            showModal('success', data.message);
                            location.reload(); // Recargar la página para mostrar el contenido
                        } else {
                            showModal('error', data.error || 'Contraseña incorrecta.');
                        }
                    } catch (error) {
                        console.error('Error al enviar la contraseña:', error);
                        showModal('error', 'Error inesperado al enviar la contraseña.');
                    }
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
                        showModal('info', `Editar conexión con ID: ${connectionId}`);
                    });
                });

                document.querySelectorAll('.delete-connection').forEach(item => {
                    item.addEventListener('click', function (event) {
                        event.preventDefault();
                        const connectionId = this.getAttribute('data-id');
                        if (confirm('¿Estás seguro de que deseas borrar esta conexión?')) {
                            fetch(`/storage/delete_connection/${connectionId}`, {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json'
                                }
                            })
                                .then(response => {
                                    if (response.ok) {
                                        showModal('success', 'Conexión borrada con éxito.');
                                        fetchConnections();
                                    } else {
                                        showModal('error', 'Error al borrar la conexión.');
                                    }
                                })
                                .catch(error => {
                                    showModal('error', 'Error inesperado al borrar la conexión.');
                                });
                        }
                    });
                });

                // Verificar cambios de estado
                connections.forEach(connection => {
                    if (previousStates[connection.id] && previousStates[connection.id] !== connection.status) {
                        showModal('info', `La conexión "${connection.name}" cambió de estado: ${connection.status}`);
                    }
                    previousStates[connection.id] = connection.status;
                });
            } else {
                console.error('Error al obtener las conexiones:', response.statusText);
                showModal('error', 'Error al obtener las conexiones.');
            }
        } catch (error) {
            console.error('Error al realizar la solicitud:', error);
            showModal('error', 'Error inesperado al obtener las conexiones.');
        }
    }

    // Vincular la función fetchConnections al botón de "Actualizar"
    refreshButton.addEventListener('click', fetchConnections);
    fetchConnections(); // Llamar a la función al cargar la página
});