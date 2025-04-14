/**
 * Crea y muestra un modal dinámico.
 * @param {string} type - El tipo de modal ("success", "error", "info", "warning").
 * @param {string} message - El mensaje que se mostrará en el modal.
 */
function showModal(type, message) {
    // Elimina cualquier modal existente
    const existingModal = document.getElementById('dynamicModal');
    if (existingModal) {
        existingModal.remove();
    }

    // Define los colores y los íconos según el tipo de modal
    const modalConfig = {
        success: {
            bgColor: 'bg-success',
            icon: '✔️'
        },
        error: {
            bgColor: 'bg-danger',
            icon: '⚠️'
        },
        info: {
            bgColor: 'bg-info',
            icon: 'ℹ️'
        },
        warning: {
            bgColor: 'bg-warning',
            icon: '⚠️'
        }
    };

    const config = modalConfig[type] || modalConfig.info;

    // Crear el contenedor del modal
    const modal = document.createElement('div');
    modal.id = 'dynamicModal';
    modal.className = `toast align-items-center text-white ${config.bgColor} border-0 position-fixed top-0 end-0 m-3`;    modal.style.zIndex = 1055;
    modal.style.minWidth = '300px';

    // Contenido del modal
    modal.innerHTML = `
        <div class="d-flex">
            <div class="toast-body d-flex align-items-center">
                <span class="me-2 fs-4">${config.icon}</span>
                <span>${message}</span>
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;

    // Agregar el modal al cuerpo del documento
    document.body.appendChild(modal);

    // Mostrar el modal usando Bootstrap
    const toast = new bootstrap.Toast(modal);
    toast.show();

    // Eliminar el modal automáticamente después de 5 segundos
    setTimeout(() => {
        modal.remove();
    }, 5000);
}