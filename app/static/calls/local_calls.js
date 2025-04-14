document.addEventListener('DOMContentLoaded', function () {
    const localForm = document.getElementById('localForm');
    const errorModal = new bootstrap.Modal(document.getElementById('errorModal'));
    const errorModalBody = document.getElementById('errorModalBody');

    if (localForm) {
        localForm.addEventListener('submit', async function (event) {
            event.preventDefault(); // Evitar el envío predeterminado del formulario

            const formData = new FormData(localForm);

            try {
                // Enviar la solicitud al backend
                const response = await fetch(localForm.action, {
                    method: 'POST',
                    body: formData
                });

                if (response.ok) {
                    // Mostrar un mensaje de éxito
                    const toast = new bootstrap.Toast(document.getElementById('successLocalConnToast'));
                    toast.show();

                    // Recargar la página después de 2 segundos
                    setTimeout(() => location.reload(), 2000);
                } else {
                    // Manejar errores del backend
                    const toast = new bootstrap.Toast(document.getElementById('errorLocalConnToast'));
                    toast.show();
                }
            } catch (error) {
                console.error('Error al añadir la conexión local:', error);
                errorModalBody.textContent = 'Ocurrió un error inesperado. Por favor, inténtalo de nuevo.';
                errorModal.show();
            }
        });
    }
});