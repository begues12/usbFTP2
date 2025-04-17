document.addEventListener('DOMContentLoaded', function () {
    const setPasswordModal = new bootstrap.Modal(document.getElementById('setPasswordModal'));
    const newPasswordInput = document.getElementById('newPasswordInput');
    const confirmPasswordInput = document.getElementById('confirmPasswordInput');
    const savePasswordButton = document.getElementById('savePasswordButton');

    let currentConnectionId = null;

    // Abrir el modal para configurar la contraseña
    document.querySelectorAll('.set-password').forEach(button => {
        button.addEventListener('click', function () {
            currentConnectionId = this.getAttribute('data-id');
            newPasswordInput.value = '';
            confirmPasswordInput.value = '';
            setPasswordModal.show();
        });
    });

    // Guardar la contraseña y obtener el token
    savePasswordButton.addEventListener('click', async function () {
        const newPassword = newPasswordInput.value.trim();
        const confirmPassword = confirmPasswordInput.value.trim();

        if (newPassword === '' || confirmPassword === '') {
            showModal('danger', 'Por favor, complete todos los campos.');
            return;
        }

        if (newPassword !== confirmPassword) {
            showModal('danger', 'Las contraseñas no coinciden.');
            return;
        }

        try {
            const response = await fetch(`/storage/set_password/${currentConnectionId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ password: newPassword })
            });

            const data = await response.json();

            if (response.ok) {
                // Guardar el token en el almacenamiento local
                localStorage.setItem(`token_${currentConnectionId}`, data.token);
                showModal('success', 'Contraseña configurada con éxito.');
                setPasswordModal.hide();
            } else {
                showModal('danger', data.message || 'Error al configurar la contraseña.');
            }
        } catch (error) {
            console.error('Error al configurar la contraseña:', error);
            showModal('danger', 'Error inesperado al configurar la contraseña.');
        }
    });
});