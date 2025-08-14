$(document).ready(function () {
    $(".view-car").click(function () {
        var carId = $(this).data("user-id");

        // Send AJAX request to fetch booking details
        $.ajax({
            url: bokoing_details, // URL to fetch booking details
            type: "GET",
            data: { car_id: carId },  // Pass the car ID in the request
            success: function (response) {
                if (response.success) {
                    // Populate the modal with the booking details
                    var bookingDetails = response.data;

                    var modalContent = `
                        <p><strong>Booking ID:</strong> ${bookingDetails.booking_id}</p>
                        <p><strong>User:</strong> ${bookingDetails.user}</p>
                        <p><strong>Driver:</strong> ${bookingDetails.driver}</p>
                        <p><strong>Car Number:</strong> ${bookingDetails.car_number}</p>
                        <p><strong>Car Model:</strong> ${bookingDetails.car_model}</p>
                        <p><strong>Pickup Date:</strong> ${bookingDetails.pickup_date}</p>
                        <p><strong>Drop Date:</strong> ${bookingDetails.drop_date}</p>
                        <p><strong>Booking Status:</strong> ${bookingDetails.booking_status}</p>
                        <p><strong>Payment Status:</strong> ${bookingDetails.payment_status}</p>

                    `;

                    // Insert the modal content
                    $("#modalBody").html(modalContent);

                    // Show the modal
                    $("#viewCarModal").modal("show");
                } else {
                    alert("Error: " + response.message);
                }
            },
            error: function () {
                alert("An error occurred while fetching booking details.");
            }
        });
    });
    $("#showAvailable").click(function () {
        filterTable("confirm");
    });

    $("#showPending").click(function () {
        filterTable("canceled");
    });

    $("#showNotAvailable").click(function () {
        filterTable("pending");
    });

    $("#showONServices").click(function () {
        filterTable("complete");
    });

    // Handle clear filter button
    $("#clearFilter").click(function () {
        clearFilter();
    });

    // Function to filter the table rows based on booking status
    function filterTable(status) {
        $("#carTableBody tr").each(function () {
            var rowStatus = $(this).attr("class").split(' ')[1];  // Get booking status class
            if (rowStatus === status) {
                $(this).show();  // Show the row
            } else {
                $(this).hide();  // Hide the row
            }
        });

        // Show the "clear filter" button
        $("#clearFilter").show();
    }

    // Function to clear the filter and show all rows
    function clearFilter() {
        $("#carTableBody tr").show();  // Show all rows
        $("#clearFilter").hide();  // Hide the clear filter button
    }

    // Open the modal when "Add New Booking" button is clicked
    $("#addCarButton").click(function () {
        $("#addBookingModal").modal("show");
    });

    let today = new Date().toISOString().split('T')[0];
    $("#pickupDate").attr("min", today).val(today);
    
    // Restrict drop date to be after pickup date
    $("#pickupDate").change(function () {
        let pickupDate = $(this).val();
        $("#dropDate").attr("min", pickupDate).val(pickupDate);
    });

    // Handle car selection and fetch price
    $('#carSelect').change(function () {
        var carId = $(this).val();

        if (carId) {
            $.ajax({
                url: user_details_url.replace("0", carId), // Ensure this matches Django URL
                type: 'GET',
                dataType: 'json',
                success: function (data) {
                    if (data) {
                        $('#pricePerHour').text("$" + data.price_per_hour);
                        $('#pricePerDay').text("$" + data.price_per_day);
                        $('#pricePerMonth').text("$" + data.price_per_month);
                        $('#discountPrice').text(data.discount + "%");
                    } else {
                        alert("Invalid car data.");
                    }
                }
            });
        } else {
            $('#pricePerHour, #pricePerDay, #pricePerMonth, #discountPrice').text("-");
        }
    });

    // Calculate cost when dates are selected
    function calculateCost() {
        let pickupDate = $("#pickupDate").val();
        let dropDate = $("#dropDate").val();
        let pickupTime = $("#pickupTime").val();
        let dropTime = $("#dropTime").val();
        
        if (pickupDate && dropDate && pickupTime && dropTime) {
            let pickupDateTime = new Date(`${pickupDate}T${pickupTime}`);
            let dropDateTime = new Date(`${dropDate}T${dropTime}`);
            
            if (dropDateTime < pickupDateTime) {
                alert("Drop-off date/time must be after pickup date/time.");
                $("#dropDate, #dropTime").val(""); // Reset invalid values
                return;
            }

            let durationMs = dropDateTime - pickupDateTime;
            let durationHours = durationMs / (1000 * 60 * 60);
            let durationDays = durationHours / 24;
            let durationMonths = durationDays / 30;

            let pricePerHour = parseFloat($('#pricePerHour').text().replace('$', '')) || 0;
            let pricePerDay = parseFloat($('#pricePerDay').text().replace('$', '')) || 0;
            let pricePerMonth = parseFloat($('#pricePerMonth').text().replace('$', '')) || 0;

            let totalCost = 0;
            let durationText = "";
            let totalDuration = 0;

            if (durationHours < 24) {
                totalCost = durationHours * pricePerHour;
                durationText = `${durationHours.toFixed(1)} hours`;
                totalDuration = durationHours;
            } else if (durationDays < 30) {
                totalCost = durationDays * pricePerDay;
                durationText = `${durationDays.toFixed(1)} days`;
                totalDuration = durationDays;
            } else {
                totalCost = durationMonths * pricePerMonth;
                durationText = `${durationMonths.toFixed(1)} months`;
                totalDuration = durationMonths;
            }

            // Display calculated values in table
            $('#duration').text(durationText);
            $('#totalCost').text("$" + totalCost.toFixed(2));
            $("#totalCostInTable").text("$" + totalCost.toFixed(2)); // Update table td with total cost
            $('#receiptAmmount').val(totalCost.toFixed(2)); // Set the receipt amount in the hidden field
        } else {
            alert("All date/time fields must be filled correctly.");
        }
    }

    // Trigger calculation on date/time change
    $("#pickupDate, #dropDate, #pickupTime, #dropTime").change(calculateCost);

    // Trigger calculation when form is submitted
    $("#addBookingForm").submit(function(event) {
        // Ensure the receipt amount is set before submitting
        calculateCost();
        var totalCost = $('#receiptAmmount').val();
        if (!totalCost) {
            alert("Please calculate the total cost first.");
            event.preventDefault(); // Prevent form submission if the total cost is not set
        }

        return true; // Submit form after validation
    });

});