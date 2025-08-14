$(document).ready(function () {
    // Get CSRF token from the cookie
    function getCSRFToken() {
        let cookieValue = null;
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith('csrftoken=')) {
                cookieValue = cookie.substring('csrftoken='.length, cookie.length);
                break;
            }
        }
        return cookieValue;
    }

    const csrfToken = getCSRFToken();

    $(document).on('click', '.save-car-btn', function () {
        console.log("Save cart function called");
        const carId = $(this).data('car-id');
        const saveCarUrl = $(this).data('save-url');
        const button = $(this); // Reference to clicked button

        $.ajax({
            url: saveCarUrl,
            type: 'POST',
            headers: {
                'X-CSRFToken': csrfToken, // Include CSRF token
            },
            data: {
                car_id: carId, // Explicitly send car_id
            },
            success: function (response) {
                if (response.success) {
                    // Update button icon depending on action (added/removed)
                    const svgSaved = `
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-bookmark-check-fill" viewBox="0 0 16 16">
                            <path fill-rule="evenodd" d="M2 15.5V2a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v13.5a.5.5 0 0 1-.74.439L8 13.069l-5.26 2.87A.5.5 0 0 1 2 15.5m8.854-9.646a.5.5 0 0 0-.708-.708L7.5 7.793 6.354 6.646a.5.5 0 1 0-.708.708l1.5 1.5a.5.5 0 0 0 .708 0z"/>
                        </svg>`;
                    const svgUnsaved = `
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-bookmark" viewBox="0 0 16 16">
                            <path d="M2 2a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v13.5a.5.5 0 0 1-.777.416L8 13.101l-5.223 2.815A.5.5 0 0 1 2 15.5zm2-1a1 1 0 0 0-1 1v12.566l4.723-2.482a.5.5 0 0 1 .554 0L13 14.566V2a1 1 0 0 0-1-1z"/>
                        </svg>`;

                    // Update button icon and its state based on response action
                    if (response.action === 'added') {
                        button.html(svgSaved); // Update button to show saved icon
                    } else {
                        button.html(svgUnsaved); // Update button to show unsaved icon
                    }
                    button.data('is-saved', response.is_saved); // Update saved state

                    // Optionally trigger saved count update event (if necessary)
                    $(document).trigger('updateSavedCarCount', [response.saved_cars_count]);
                }
            },
            error: function (xhr, status, error) {
                console.error('Error:', error);
            },
        });
    });
});
$(document).ready(function () {
    // When the car icon is clicked
    $('#car-icon').on('click', function (e) {
        e.preventDefault();
        // AJAX request to fetch saved cars for the logged-in user
        $.ajax({
            url: carurl,  // URL to get saved cars (class-based view)
            type: 'GET',
success: function (response) {
    var carDetailsHTML = '';
    if (response.success) {
        if (response.saved_cars.length > 0) {
            // Inject saved car details into the slider
            response.saved_cars.forEach(function (car) {
                carDetailsHTML += `
                    <div class="car-detail card" style="width: 18rem;">
                        <img src="${car.image}" class="card-img-top" alt="${car.model}">
                        <div class="card-body">
                            <h5 class="card-title">${car.model}</h5>
                            <p class="card-text"><strong>Make:</strong> ${car.make}</p>
                            <p class="card-text"><strong>Price per Hour:</strong> ₹${car.price_per_hour}</p>
                            <p class="card-text"><strong>Discount:</strong> ${car.discount}%</p>
                            <p class="card-text"><strong>car Status:</strong> ${car.status}</p>
                            
                            <!-- Buttons -->
                            <a href="javascript:void(0);" class="btn btn-primary py-2 mr-1" onclick="window.location.href = '/car/car-booking/'+${car.id}+'/book'">Book Now</a>
                        <a href="javascript:void(0);" class="btn btn-secondary py-2 ml-1" onclick="window.location.href = '/car/car-single/' +'${car.id}'">Details</a>
                        </div>
                    </div>
                `;
            });
        } else {
            carDetailsHTML = '<p>No cars saved yet.</p>';
        }
    } else {
        carDetailsHTML = '<p>Error loading saved cars. Please try again later.</p>';
    }

    // Inject the car details or message into the slider
    $('#car-details').html(carDetailsHTML);

    // Show the slider
    $('#car-details-slider').css('right', '0');
},
error: function (xhr, status, error) {
    console.error("Error loading saved cars:", error);
    $('#car-details').html('<p>Error loading saved cars. Please try again later.</p>');
}

        });
    });

    // Close the slider when the close button is clicked
    $('#close-slider').on('click', function () {
        $('#car-details-slider').css('right', '-100%');
    });
});

