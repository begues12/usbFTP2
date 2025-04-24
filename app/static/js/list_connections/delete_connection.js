connectionsTable.addEventListener('click', async function (event) {
    const target = event.target.closest('.delete-connection');
    if (!target) return;

    event.preventDefault();

    const connectionId = target.getAttribute('data-id');
    const connectionType = target.getAttribute('data-type');

    if (!connectionId) {
        console.error('No se encontró el ID de la conexión.');
        return;
    }

    // Mostrar el modal de confirmación
    showConfirmModal(
        'Confirmar eliminación',
        `¿Estás seguro de que deseas eliminar la conexión "${connectionType}" con ID ${connectionId}?`,
        async () => {
            try {
                const response = await fetch(`/storage/delete_connection/${connectionId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });

                if (response.ok) {
                    showModal('success', 'Conexión eliminada con éxito.');
                    fetchConnections(); // Actualiza la lista de conexiones
                } else {
                    const data = await response.json();
                    showModal('error', data.error || 'Error al eliminar la conexión.');
                }
            } catch (error) {
                console.error('Error al eliminar la conexión:', error);
                showModal('error', 'Error inesperado al eliminar la conexión.');
            }
        }
    );
});
