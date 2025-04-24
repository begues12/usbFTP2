document.addEventListener('DOMContentLoaded', function () {
    const refreshButton = document.getElementById('refreshConnectionsButton'); // Botón de "Actualizar"
    const viewContainer = document.getElementById('viewContainer'); // Contenedor donde se mostrará el contenido

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
                    row.setAttribute('data-url', `/storage/list/${connection.id}`);
                
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

                const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
                tooltipTriggerList.forEach(function (tooltipTriggerEl) {
                    new bootstrap.Tooltip(tooltipTriggerEl, {
                        html: true
                    });
                });

                document.querySelectorAll('.clickable-row').forEach(row => {
                    row.addEventListener('click', async function (event) {
                        if (event.target.closest('.dropdown')) {
                            return;
                        }
                
                        const url = this.getAttribute('data-url');
                        const connectionId = this.getAttribute('data-url').split('/')[3];
                
                        try {
                            const token = localStorage.getItem(`token_${connectionId}`);
                            const headers = {
                                'Content-Type': 'application/json'
                            };
                
                            if (token) {
                                headers['Authorization'] = `Bearer ${token}`;
                            }
                
                            const response = await fetch(url, {
                                method: 'POST',
                                headers: headers
                            });

                            if (response.ok) {
                                // Obtener el HTML directamente de la respuesta
                                const folderHtml = await response.text();
                                // Incrustar el HTML en el contenedor
                                viewContainer.innerHTML = folderHtml;
                            } else if (response.status === 403) {
                                await handlePasswordFlow(connectionId, url);
                            } else {
                                console.log('error', 'Error al abrir la conexión.', response.statusText);
                            }
                        } catch (error) {
                            console.error('Error al realizar la solicitud:', error);
                            showModal('error', 'Error inesperado al abrir la conexión.');
                        }
                    });
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

    async function handlePasswordFlow(connectionId, url) {
        const passwordModal = new bootstrap.Modal(document.getElementById('passwordModal'));
        const submitButton = document.getElementById('submitPasswordButton');
        const passwordInput = document.getElementById('passwordInput');

        submitButton.setAttribute('data-connection-id', connectionId);

        const handlePasswordSubmit = async () => {
            const password = passwordInput.value;

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
                    localStorage.setItem(`token_${connectionId}`, data.token);

                    showModal('success', 'Contraseña correcta. Token almacenado.');

                    const headers = {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${data.token}`
                    };

                    const retryResponse = await fetch(url, {
                        method: 'POST',
                        headers: headers
                    });

                    if (retryResponse.ok) {
                        // Obtener el HTML directamente de la respuesta
                        const folderHtml = await retryResponse.text();
                        // Incrustar el HTML en el contenedor
                        viewContainer.innerHTML = folderHtml;
                    } else {
                        console.log('error', 'Error al abrir la conexión.', retryResponse.statusText);
                    }

                    passwordModal.hide();
                } else {
                    showModal('error', data.error || 'Contraseña incorrecta.');
                }
            } catch (error) {
                console.error('Error al enviar la contraseña:', error);
                showModal('error', 'Error inesperado al enviar la contraseña.');
            }
        };

        submitButton.addEventListener('click', handlePasswordSubmit, { once: true });
        passwordModal.show();
    }

    refreshButton.addEventListener('click', fetchConnections);
    fetchConnections();
});