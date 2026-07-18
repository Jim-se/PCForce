const stars = $('.star-button');
const ratingInput = $('#rating-input');

stars.on('click', function () {
    const rating = $(this).data('rating');

    ratingInput.val(rating);

    stars.each(function () {
        if ($(this).data('rating') <= rating) {
            $(this).addClass('selected');
        } else {
            $(this).removeClass('selected');
        }
    });
});

$('#ajax-review-form').on('submit', function (event) {
    event.preventDefault();

    const form = $(this);

    $.ajax({
        type: 'POST',
        url: form.attr('action'),
        data: form.serialize(),
        success: function (response) {
            $('#review-message').text(response.message).removeClass('error-message').addClass('success-message');
            $('#average-rating').text('Average rating: ' + response.average_rating + '/5');

            $('#no-reviews-message').remove();

            const reviewCard = $('<div>').addClass('review-card card');
            reviewCard.append($('<p>').text(response.rating + '/5'));
            reviewCard.append($('<p>').text(response.comment));
            reviewCard.append($('<p>').text('By ' + response.username));

            $('#reviews-list').prepend(reviewCard);

            form.hide();
            $('#review-form-title').hide();
        },
        error: function (response) {
            $('#review-message').text(response.responseJSON.message).removeClass('success-message').addClass('error-message');
        }
    });
});
