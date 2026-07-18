document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.django-message').forEach(function (message) {
        message.style.display = 'block';

        setTimeout(function () {
            message.style.display = 'none';
        }, 3000);
    });
});