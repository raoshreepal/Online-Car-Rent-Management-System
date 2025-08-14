$(document).ready(function () {
    $("#search-car").on("input", function () {
        
        var query = $(this).val();
        
        if (query.length >= 1) { 
            $.ajax({
                url: availablecar, 
                method: "GET",
                data: {
                    query: query
                },
                success: function (response) {

                    var cars = response.cars;

                    if (cars.length > 0) {
                        var suggestionHtml = "";
                        cars.forEach(function (car) {
                           suggestionHtml += `
                           <div title="click to show more details about ${car.model}" class="suggestion-item" data-id="${car.id}">
                           <img src="${car.image}" alt="${car.model}" class="suggestion-image">
                           <div class="suggestion-info">
                               <h5 class="text-dark">${car.model}</h5>
                               <p class="text-dark">${car.type} | ${car.seats} Seats</p>
                               <p class="text-dark"><strong>₹ ${car.price}</strong>/hour</p>
                               <span> less ₹${car.discount}% Per Day</span>
                           </div>                                                                          
                           <!-- Corrected booking link using JavaScript -->
                           <a href="javascript:void(0);" class="btn btn-primary py-2 mr-1" onclick="window.location.href = 'car/car-booking/'+${car.id}+'/book'">Book now</a>
                           <a href="#" class="btn btn-secondary py-2 ml-1" onclick="window.location.href = '/car/car-single/' + encodeURIComponent('${car.id}')">
                               Details
                           </a>              
                       </div>
                `;         
              
            
            });
                

                        $("#car-suggestions").html(suggestionHtml).show();
                    } else {
                        $("#car-suggestions").html(`
                            <div class="text-center p-3">
                            <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" fill="currentColor" class="bi bi-car-front-fill" viewBox="0 0 16 16">
  <path d="M2.52 3.515A2.5 2.5 0 0 1 4.82 2h6.362c1 0 1.904.596 2.298 1.515l.792 1.848c.075.175.21.319.38.404.5.25.855.715.965 1.262l.335 1.679q.05.242.049.49v.413c0 .814-.39 1.543-1 1.997V13.5a.5.5 0 0 1-.5.5h-2a.5.5 0 0 1-.5-.5v-1.338c-1.292.048-2.745.088-4 .088s-2.708-.04-4-.088V13.5a.5.5 0 0 1-.5.5h-2a.5.5 0 0 1-.5-.5v-1.892c-.61-.454-1-1.183-1-1.997v-.413a2.5 2.5 0 0 1 .049-.49l.335-1.68c.11-.546.465-1.012.964-1.261a.8.8 0 0 0 .381-.404l.792-1.848ZM3 10a1 1 0 1 0 0-2 1 1 0 0 0 0 2m10 0a1 1 0 1 0 0-2 1 1 0 0 0 0 2M6 8a1 1 0 0 0 0 2h4a1 1 0 1 0 0-2zM2.906 5.189a.51.51 0 0 0 .497.731c.91-.073 3.35-.17 4.597-.17s3.688.097 4.597.17a.51.51 0 0 0 .497-.731l-.956-1.913A.5.5 0 0 0 11.691 3H4.309a.5.5 0 0 0-.447.276L2.906 5.19Z"/>
</svg>
                                <p class="text-danger fw-bold">
                                No cars available </p>
                            </div>
                        `).show(); 
                    }
                },
                error: function () {
                    alert("Error fetching car suggestions. Please try again.");
                }
            });
        } else {
            $("#car-suggestions").hide(); 
        }
    });

    $(document).on("click", ".suggestion-item", function () {
        var carId = $(this).data("id");
        
    });
});
$(document).ready(function() {
    $('#driverSelect').change(function() {

        var driverId = $(this).val(); 
        if (driverId) {
            $.ajax({
                url: "/car/car-booking/driver-details/",  
                data: { 'driver_id': driverId },  
                dataType: 'json',
                success: function(data) {
                    // If the driver details are fetched successfully
                    if (data.error) {
                        $('#driver-details').html('<p class="text-danger">Driver not found.</p>');
                    } else {
                        
                        // Display the fetched driver details in the #driver-details div
                        var driverDetails = `
                        <div class="card border-primary shadow-sm" style="max-width: 400px;">
                            <div class="card-header bg-primary text-white text-center">
                                Driver Information
                            </div>
                            <div class="card-body text-center">
                                <img srcatta.image}" alt="Driver Image" class="img-fluid rounded-circle mb-3" style="width: 150px; height: 150px; object-fit: cover;" />
                                <h5 class="card-title">${data.name}</h5>
                                <p class="card-text"><strong>Contact Number:</strong> ${data.number}</p>
                                <p class="card-text"><strong>Gender:</strong> ${data.gender}</p>

                            </div>
                        </div>
                        `;
                        $('#driver-details').html(driverDetails);
                    }
                },
                error: function(xhr, status, error) {
                    // If there's an error with the AJAX request
                    $('#driver-details').html('<p class="text-danger">There was an error fetching driver details.</p>');
                }
            });
        } else {
            // Clear the driver details if no driver is selected
            $('#driver-details').html('');
        }
    });
});
$(document).ready(function() {
   

    // Handle the confirm booking button click
    $(document).on('click', '#confirm-booking-btn', function() {
        // Show the success modal
        $('#successModal').modal('show');
    });
});

    $(document).ready(function () {
        const pricePerHour = parseFloat($("#price-per-hour").val());
        const pricePerDay = parseFloat($("#price-per-day").val());
        const pricePerMonth = parseFloat($("#price-per-month").val());

        // Function to parse date and time into a single Date object
        function parseDateTime(dateStr, timeStr) {
            const dateParts = dateStr.split("-");
            const timeParts = timeStr.split(":");
            return new Date(
                parseInt(dateParts[0]), // Year
                parseInt(dateParts[1]) - 1, // Month (0-based)
                parseInt(dateParts[2]), // Day
                parseInt(timeParts[0]), // Hours
                parseInt(timeParts[1]) // Minutes
            );
        }
        $("#pickupDate").on("change", function () {
            const pickupDate = $(this).val();
            if (pickupDate) {
                $("#dropDate").attr("min", pickupDate); // Set the min attribute
            }
        });

        // When Drop Date or Time changes, calculate the total cost
        $("#pickupDate, #pickupTime, #dropDate, #dropTime").on("change", function () {
            const pickupDate = $("#pickupDate").val();
            const pickupTime = $("#pickupTime").val();
            const dropDate = $("#dropDate").val();
            const dropTime = $("#dropTime").val();
         
            if (pickupDate && pickupTime && dropDate && dropTime) {
                const pickupDateTime = parseDateTime(pickupDate, pickupTime);
                const dropDateTime = parseDateTime(dropDate, dropTime);

                if (dropDateTime > pickupDateTime) {
                    const durationInMilliseconds = dropDateTime - pickupDateTime;
                    const durationInHours = durationInMilliseconds / (1000 * 60 * 60);
                    const durationInDays = durationInHours / 24;

                    let totalCost = 0;
                    let rate = 0;
                    let perUnit = "";
                    let durationText = "";

                    if (durationInHours <= 24) {
                        totalCost = durationInHours * pricePerHour;
                        rate = pricePerHour;
                        perUnit = "Hour";
                        durationText = `${Math.ceil(durationInHours)} Hours`;
                    } else if (durationInDays <= 30) {
                        totalCost = Math.ceil(durationInDays) * pricePerDay;
                        rate = pricePerDay;
                        perUnit = "Day";
                        durationText = `${Math.ceil(durationInDays)} Days`;
                    } else {
                        const durationInMonths = Math.ceil(durationInDays / 30);
                        totalCost = durationInMonths * pricePerMonth;
                        rate = pricePerMonth;
                        perUnit = "Month";
                        durationText = `${durationInMonths} Months`;
                    }

                    // Update Receipt Details
                    $("#rate").text(`₹ ${rate.toFixed(2)}`);
                    $("#total").text(`₹ ${totalCost.toFixed(2)}`);
                    $("input[name='receipt_amount']").val(totalCost.toFixed(2)); 
                    $("#duration").text(durationText); 

                    $(".booking-receipt").show();
                } else {
                }
            } else {
                $(".booking-receipt").hide(); 
            }
        });
        $("#booking-form").submit(function(e) {
            var receiptAmmountValue = $("#receiptAmmount").val();
            $("input[name='receipt_amount']").val(receiptAmmountValue); 
        });

        // Handle form submission
        $("#confirmBooking").on("click", function (e) {
            e.preventDefault(); // Prevent default form submission

            // Hide booking form and show generate invoice button
            $("form").hide();
            $("#generateInvoice").show();
        });
    });

   