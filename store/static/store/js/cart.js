$('.ajax-cart-form').on('submit', function (event) {
    event.preventDefault();

    const form = $(this);
    const cartItem = form.closest('.cart-item');

    $.ajax({
        type: 'POST',
        url: form.attr('action'),
        data: form.serialize(),
        success: function (response) {
            if (response.removed) {
                cartItem.remove();
            } else {
                cartItem.find('.cart-item-quantity').text(response.quantity);
                cartItem.find('.cart-item-subtotal').text('Subtotal: ' + response.item_subtotal + ' EUR');
            }

            $('#cart-total').text(response.cart_total);

            if ($('.cart-item').length === 0) {
                $('.cart-list').html('<p>Your cart is empty.</p>');
                $('#cart-checkout-form').hide();
            }
        },
        error: function (response) {
            $('#cart-message')
                .text(response.responseJSON.message)
                .removeClass('success-message')
                .addClass('error-message');
        }
    });
});
