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
        const submitButton = document.querySelector('#ftpForm button[type="submit"]');
        submitButton.disabled = true;
        submitButton.textContent = 'Guardando...';

        const response = await fetch('/storage/add_connection/ftp', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });

        const data = await response.json();

        if (response.ok) {
            showModal('success', 'Conexión FTP añadida con éxito.');
            document.getElementById('ftpForm').reset();
        } else {
            showModal('error', `Error al añadir la conexión FTP: ${data.error}`);
        }
    } catch (error) {
        showModal('error', 'Error inesperado al añadir la conexión FTP.');
    } finally {
        const submitButton = document.querySelector('#ftpForm button[type="submit"]');
        submitButton.disabled = false;
        submitButton.textContent = 'Guardar Conexión';
    }
});