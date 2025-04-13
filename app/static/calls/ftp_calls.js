document.getElementById('ftpForm').addEventListener('submit', async function (e) {
    e.preventDefault(); // Evitar el comportamiento predeterminado del formulario

    // Obtener los datos del formulario
    const name = document.getElementById('ftpName').value;
    const host = document.getElementById('ftpHost').value;
    const port = document.getElementById('ftpPort').value;
    const username = document.getElementById('ftpUsername').value;
    const password = document.getElementById('ftpPassword').value;

    // Crear el cuerpo de la solicitud
    const requestData = {
        name: name,
        host: host,
        port: port,
        username: username,
        password: password
    };

    try {
        // Mostrar un indicador de carga (opcional)
        const submitButton = document.querySelector('#ftpForm button[type="submit"]');
        submitButton.disabled = true;
        submitButton.textContent = 'Guardando...';

        // Realizar la solicitud al backend
        const response = await fetch('storage/add_connection/ftp', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });

        const data = await response.json();

        // Manejar la respuesta del backend
        if (response.ok) {
            alert('Conexión FTP añadida con éxito');
            // Opcional: Recargar la lista de conexiones o limpiar el formulario
            document.getElementById('ftpForm').reset();
        } else {
            alert(`Error: ${data.error}`);
        }
    } catch (error) {
        alert(`Error al añadir la conexión FTP: ${error.message}`);
    } finally {
        // Restaurar el estado del botón
        submitButton.disabled = false;
        submitButton.textContent = 'Guardar Conexión';
    }
});