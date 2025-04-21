document.addEventListener('DOMContentLoaded', function () {
    const localForm = document.getElementById('localForm');

    if (localForm) {
        localForm.addEventListener('submit', async function (event) {
            event.preventDefault();

            const formData = new FormData(localForm);

            try {
                const response = await fetch(localForm.action, {
                    method: 'POST',
                    body: formData
                });

                if (response.ok) {
                    const toast = new bootstrap.Toast(document.getElementById('successLocalConnToast'));
                    toast.show();

                    setTimeout(() => location.reload(), 2000);
                } else {
                    const toast = new bootstrap.Toast(document.getElementById('errorLocalConnToast'));
                    toast.show();
                }
            } catch (error) {
                const toast = new bootstrap.Toast(document.getElementById('errorLocalConnToast'));
                toast.show();
            }
        });
    }
});