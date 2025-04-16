$(document).ready(function () {
    const setPasswordModal = new bootstrap.Modal(document.getElementById('setPasswordModal'));
    const newPasswordInput = $('#newPasswordInput'); // Convertir a objeto jQuery
    const confirmPasswordInput = $('#confirmPasswordInput'); // Convertir a objeto jQuery
    const savePasswordButton = $('#savePasswordButton');

    let currentConnectionId = null; // Guardar el ID de la conexión actual para configurar la contraseña

    // Asignar evento dinámico al botón "Configurar Contraseña"
    $(document).on('click', '.set-password', function (event) {
        event.preventDefault();
        currentConnectionId = $(this).data('id'); // Obtener el ID de la conexión
        newPasswordInput.val(''); // Limpiar el campo de nueva contraseña
        confirmPasswordInput.val(''); // Limpiar el campo de confirmación
        setPasswordModal.show(); // Mostrar el modal
    });

    // Manejar el guardado de la contraseña
    savePasswordButton.on('click', async function () {
        const newPassword = newPasswordInput.val().trim();
        const confirmPassword = confirmPasswordInput.val().trim();

        if (newPassword === '' || confirmPassword === '') {
            showModal('warning', 'Por favor, completa ambos campos.');
            return;
        }

        if (newPassword !== confirmPassword) {
            showModal('error', 'Las contraseñas no coinciden.');
            return;
        }

        try {
            // Enviar la solicitud al servidor para configurar la contraseña
            const response = await fetch(`/storage/set_password/${currentConnectionId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ password: newPassword }) // Enviar la contraseña como JSON
            });

            if (response.ok) {
                showModal('success', 'Contraseña configurada con éxito.');
                setPasswordModal.hide(); // Cerrar el modal
            } else {
                const errorData = await response.json();
                showModal('error', errorData.error || 'Error al configurar la contraseña.');
            }
        } catch (error) {
            console.error('Error al configurar la contraseña:', error);
            showModal('error', 'Error inesperado al configurar la contraseña.');
        }
    });
});