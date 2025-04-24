$(document).ready(function () {
    const setPasswordModal = new bootstrap.Modal(document.getElementById('setPasswordModal'));
    const currentPasswordInput  = $('#currentPasswordInput');
    const newPasswordInput      = $('#newPasswordInput');
    const confirmPasswordInput  = $('#confirmPasswordInput');
    const savePasswordButton    = $('#savePasswordButton');

    let currentConnectionId = null; 

    $(document).on('click', '.set-password', function (event) {
        event.preventDefault();
        currentConnectionId = $(this).data('id');
        currentPasswordInput.val('');
        newPasswordInput.val('');
        confirmPasswordInput.val('');
        setPasswordModal.show();
    });

    savePasswordButton.on('click', async function () {
        const currentPassword   = currentPasswordInput.val().trim();
        const newPassword       = newPasswordInput.val().trim();
        const confirmPassword   = confirmPasswordInput.val().trim();

        if (currentPassword === '' || newPassword === '' || confirmPassword === '') {
            showModal('warning', 'Por favor, completa todos los campos.');
            return;
        }

        if (newPassword !== confirmPassword) {
            showModal('error', 'Las nuevas contraseñas no coinciden.');
            return;
        }

        try {
            const response = await fetch(`/storage/set_password/${currentConnectionId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    current_password: currentPassword,
                    new_password    : newPassword
                })
            });

            if (response.ok) {
                showModal('success', 'Contraseña configurada con éxito.');
                setPasswordModal.hide();
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