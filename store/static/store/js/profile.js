function toggleProfileForm() {
    const form = document.getElementById('profile-edit-form');
    form.hidden = !form.hidden;
}

const ordersButton = document.querySelector('.orders-button');
const ordersSection = document.getElementById('orders-section');

if (ordersButton && ordersSection) {
    ordersButton.addEventListener('click', function () {
        ordersSection.hidden = !ordersSection.hidden;
    });
}

$('.ajax-order-status-form').on('submit', function (event) {
    event.preventDefault();

    const form = $(this);
    const orderCard = form.closest('.order-card');
    const statusBadge = orderCard.find('.order-status');

    $.ajax({
        type: 'POST',
        url: form.attr('action'),
        data: form.serialize(),
        success: function (response) {
            statusBadge
                .removeClass('status-pending status-completed status-cancelled')
                .addClass('status-' + response.status)
                .text(response.status_display);
        }
    });
});

$('#ajax-add-category-form').on('submit', function (event) {
    event.preventDefault();

    const form = $(this);

    $.ajax({
        type: 'POST',
        url: form.attr('action'),
        data: form.serialize(),
        success: function (response) {
            $('#category-message')
                .text('Category added.')
                .removeClass('error-message')
                .addClass('success-message');

            const row = `
                <div class="category-row" data-category-id="${response.id}">
                    <form class="ajax-edit-category-form" method="POST" action="/categories/${response.id}/edit/">
                        ${form.find('input[name="csrfmiddlewaretoken"]').prop('outerHTML')}
                        <input class="form-control" type="text" name="name" value="${response.name}">
                        <button class="btn btn-dark btn-sm" type="submit">Save</button>
                    </form>

                    <form class="ajax-delete-category-form" method="POST" action="/categories/${response.id}/delete/">
                        ${form.find('input[name="csrfmiddlewaretoken"]').prop('outerHTML')}
                        <button class="btn btn-danger btn-sm" type="submit">Delete</button>
                    </form>
                </div>
            `;

            $('.category-panel').append(row);
            form.find('input[name="name"]').val('');
        },
        error: function (response) {
            $('#category-message')
                .text(response.responseJSON.message)
                .removeClass('success-message')
                .addClass('error-message');
        }
    });
});

$(document).on('submit', '.ajax-edit-category-form', function (event) {
    event.preventDefault();

    const form = $(this);

    $.ajax({
        type: 'POST',
        url: form.attr('action'),
        data: form.serialize(),
        success: function () {
            $('#category-message')
                .text('Category updated.')
                .removeClass('error-message')
                .addClass('success-message');
        },
        error: function (response) {
            $('#category-message')
                .text(response.responseJSON.message)
                .removeClass('success-message')
                .addClass('error-message');
        }
    });
});

$(document).on('submit', '.ajax-delete-category-form', function (event) {
    event.preventDefault();

    const form = $(this);
    const row = form.closest('.category-row');

    $.ajax({
        type: 'POST',
        url: form.attr('action'),
        data: form.serialize(),
        success: function () {
            row.remove();

            $('#category-message')
                .text('Category deleted.')
                .removeClass('error-message')
                .addClass('success-message');
        },
        error: function (response) {
            $('#category-message')
                .text(response.responseJSON.message)
                .removeClass('success-message')
                .addClass('error-message');
        }
    });
});
