$(document).ready(function(){
    $(".view-bookings").click(function(){
        var username = $(this).data("user"); // Get the username from the button
        $.ajax({
            url: user_bookings,  // URL for AJAX request
            type: "GET",
            data: { username: username },
            success: function(response) {
                var bookings = response.bookings;
                var bookingTable = "";
                
                if (bookings.length > 0) {
                    $.each(bookings, function(index, booking) {
                        bookingTable += "<tr>";
                        bookingTable += "<td>" + booking.car_name + "<br>"+booking.car_number+"</td>";
                        bookingTable+="<td>"+booking.pickup_location+"</td>";
                        bookingTable += "<td>" + booking.pickup_date + "</td>";
                        bookingTable += "<td>" + booking.drop_date + "</td>";
                        bookingTable += "<td> ₹ " + booking.receipt_amount + "</td>";
                        bookingTable += "</tr>";
                    });
                } else {
                    bookingTable = "<tr><td colspan='4' class='text-center'>No bookings found</td></tr>";
                }

                $("#bookingDetails").html(bookingTable);
                $("#bookingModal").modal("show");  // Show modal
            }
        });
        $('.close').on('click',function(){
          $("#bookingModal").modal("hide");  // Show modal


        });
    });
    $('#addBookingBtn').on('click',function(){
      $('#bookingFormModal').modal('show');
    });
});
$(document).ready(function() {
    // Set the minimum pickup date to today
    const pickupDateField = $("#pickupDate");
    const dropDateField = $("#dropDate");

    // Get today's date in YYYY-MM-DD format
    const today = new Date().toISOString().split('T')[0];
    pickupDateField.attr('min', today);

    // When the pickup date changes, update the drop date min value
    pickupDateField.on('change', function() {
        const selectedPickupDate = $(this).val();
        dropDateField.attr('min', selectedPickupDate);

        // If the current drop date is before the selected pickup date, reset it
        if (dropDateField.val() < selectedPickupDate) {
            dropDateField.val(selectedPickupDate);
        }
    });

    // Initialize drop date min value if pickup date is already selected
    if (pickupDateField.val()) {
        dropDateField.attr('min', pickupDateField.val());
    }
});
$(document).ready(function() {
    // When the car selection changes
    $('#carSelect').on('change', function() {
        const carId = $(this).val();  // Get the selected car ID
        alert(carId)
        // Send an AJAX request to fetch car det    ails
        $.ajax({
            url: get_car_details,
            data: {
                'car_id': carId,
            },
            dataType: 'json',
            success: function(response) {
                // Update the table with car details
                $('#rate_per_hour').text(`₹${response.rate_per_hour}`);
                $('#discount').text(`${response.discount}%`);
                $('#rate_per_day').text(`₹${response.rate_per_day}`);
                $('#rate_per_month').text(`₹${response.rate_per_month}`);

                // Store the car's pricing details in variables for calculations
                window.ratePerHour = parseFloat(response.rate_per_hour);
                window.ratePerDay = parseFloat(response.rate_per_day);
                window.ratePerMonth = parseFloat(response.rate_per_month);
                window.discount = parseFloat(response.discount);

                console.log('Car details loaded:', response);
            },
            error: function(response) {
                console.error('Error fetching car details:', response);
            }
        });
    });
        // Function to calculate the total cost
        function calculateTotalCost() {
            const pickupDate = $('#pickupDate').val();
            const pickupTime = $('#pickupTime').val();
            const dropDate = $('#dropDate').val();
            const dropTime = $('#dropTime').val();
    
            if (!pickupDate || !pickupTime || !dropDate || !dropTime || !window.ratePerHour) {
                console.log('Please fill all fields and select a car.');
                return;
            }
    
            // Combine date and time into DateTime objects
            const pickupDateTime = new Date(`${pickupDate}T${pickupTime}`);
            const dropDateTime = new Date(`${dropDate}T${dropTime}`);
            // Calculate the difference in milliseconds
            const timeDifference = dropDateTime - pickupDateTime;
    
            // Convert difference to hours, days, and months
            const hours = timeDifference / (1000 * 60 * 60);
            const days = hours / 24;
            const months = days / 30;
    
            let totalCost = 0;
            let perDetails = '';
    
            // Calculate cost based on duration
            if (months >= 1) {
                totalCost = months * window.ratePerMonth;
                perDetails = `Per Month (${months.toFixed(2)} months)`;
            } else if (days >= 1) {
                totalCost = days * window.ratePerDay;
                perDetails = `Per Day (${days.toFixed(2)} days)`;
            } else {
                totalCost = hours * window.ratePerHour;
                perDetails = `Per Hour (${hours.toFixed(2)} hours)`;
            }
    
            // Apply discount
            totalCost = totalCost - (totalCost * (window.discount / 100));
            // Update the receipt amount and per details in the table
            $('#receipt_amount').text(`$${totalCost.toFixed(2)}`);
            $('#per_details').text(perDetails);
            $('#receiptAmmount').val(totalCost.toFixed(2))

        }
    
        // Trigger calculation when dates or times change
        $('#pickupDate, #pickupTime, #dropDate, #dropTime').on('change', function() {
            calculateTotalCost();
        });
});