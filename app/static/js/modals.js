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
            icon: '✔️',
            text_color: 'text-ligth'
        },
        error: {
            bgColor: 'bg-danger',
            icon: '⚠️',
            text_color: 'text-ligth'
        },
        info: {
            bgColor: 'bg-info',
            icon: 'ℹ️',
            text_color: 'text-black'
        },
        warning: {
            bgColor: 'bg-warning',
            icon: '⚠️',
            text_color: 'text-black'
        }
    };

    const config = modalConfig[type] || modalConfig.info;

    // Crear el contenedor del modal
    const modal = document.createElement('div');
    modal.id = 'dynamicModal';
    modal.className = `toast align-items-center text-white ${config.bgColor} border-0 position-fixed top-0 end-0 m-3`;
    modal.style.zIndex = 1055;
    modal.style.minWidth = '300px';

    // Contenido del modal
    modal.innerHTML = `
        <div class="d-flex">
            <div class="toast-body d-flex align-items-center">
                <span class="me-2 fs-4">${config.icon}</span>
                <span class="${config.text_color}">${message}</span>
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

/**
 * Crea y muestra un modal de confirmación.
 * @param {string} title - El título del modal.
 * @param {string} message - El mensaje que se mostrará en el modal.
 * @param {function} onConfirm - Función que se ejecutará si el usuario confirma.
 */
function showConfirmModal(title, message, onConfirm) {
    // Elimina cualquier modal existente
    const existingModal = document.getElementById('confirmModal');
    if (existingModal) {
        existingModal.remove();
    }

    // Crear el contenedor del modal
    const modal = document.createElement('div');
    modal.id = 'confirmModal';
    modal.className = 'modal fade';
    modal.tabIndex = -1;
    modal.setAttribute('aria-labelledby', 'confirmModalLabel');
    modal.setAttribute('aria-hidden', 'true');

    // Contenido del modal
    modal.innerHTML = `
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="confirmModalLabel">${title}</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <p>${message}</p>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                    <button type="button" class="btn btn-danger" id="confirmButton">Confirmar</button>
                </div>
            </div>
        </div>
    `;

    // Agregar el modal al cuerpo del documento
    document.body.appendChild(modal);

    // Mostrar el modal usando Bootstrap
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();

    // Manejar el botón de confirmación
    const confirmButton = document.getElementById('confirmButton');
    confirmButton.addEventListener('click', () => {
        bootstrapModal.hide();
        onConfirm(); // Ejecutar la función de confirmación
    });

    // Eliminar el modal del DOM después de cerrarlo
    modal.addEventListener('hidden.bs.modal', () => {
        modal.remove();
    });
}