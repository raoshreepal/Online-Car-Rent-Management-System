$(document).ready(function () {
    let selectedCarId = null;
  
    // Search Functionality
    $("#searchBar").on("input", function () {
      const query = $(this).val().toLowerCase();
      $("#carTableBody tr").each(function () {
        // const number = $(this).find("td:nth-child(3)").text().toLowerCase();
        const status = $(this).find("td").text().toLowerCase();
        if ( status.includes(query)) {
          $(this).show();
        } else {
          $(this).hide();
        }
      });
    });
  
    // Add Car
    $("#addCarButton").click(function () {
      $("#addCarModal").modal("show",{ direction: "bottom" }, 500);
    });
  
    $("#addCarForm").submit(function (e) {
      e.preventDefault();
      const carNumber = $("#addCarNumber").val();
      const carMake = $("#addCarMake").val();
      const carModel = $("#addCarModel").val();
      const carYear = $("#addCarYear").val();
      const carMileage = $("#addCarMileage").val();
      const carStatus = $("#addCarStatus").val();
      const newCarId = $("#carTableBody tr").length + 1;
  
      $("#carTableBody").append(`
        <tr data-car-id="${newCarId}">
          <td>${newCarId}</td>
          <td><img src="https://via.placeholder.com/100" alt="Car Image" class="img-thumbnail" /></td>
          <td>${carNumber}</td>
          <td>${carMake}</td>
          <td>${carModel}</td>
          <td>${carYear}</td>
          <td>${carMileage}</td>
          <td>${carStatus}</td>
          <td>
            <i class="fas fa-eye text-primary view-car" style="cursor: pointer;" title="View"></i>
            <i class="fas fa-edit text-warning ms-2 edit-car" style="cursor: pointer;" title="Edit"></i>
            <i class="fas fa-trash text-danger ms-2 delete-car" style="cursor: pointer;" title="Delete"></i>
          </td>
        </tr>
      `);
  
      $("#addCarModal").modal("hide");
      $("#addCarForm")[0].reset();
    });
      $('.view-car').on('click', function() {
        var carId = $(this).data('user-id'); 

        var url = viewCarUrl.replace('0', carId);

        $.ajax({
            url: url, 
            type: 'GET',
            dataType: 'json',
            success: function(data) {
                if (data.error) {
                    alert('Car not found');
                } else {
                    $('#car-id').text(data.id);
                    $('#car-make').text(data.make);
                    $('#car-model').text(data.model);
                    $('#car-year').text(data.year);
                    $('#car-number').text(data.number); 
                    $('#car-mileage').text(data.mileage);
                    $('#car-type').text(data.type);
                    $('#car-status').text(data.status.toUpperCase());
                    $('#car-par-hour-rent').text("₹ "+data.par_hour_rent);
                    $('#car-par-day-rent').text("₹ "+data.par_day_rent);
                    $('#car-par-month-rent').text("₹ "+data.par_month_rent);
                    $('#carRentdiscount').text(data.discount+"%");
                    $('#car-seats').text(data.seats);

                    $('#carDetailsModal').modal('show');
                }
            },
            error: function(xhr, status, error) {
                console.error('Error fetching car details: ' + error);
            }
        });
    });


    $('.car-thumbnail').on('click', function() {
        var imageUrl = $(this).attr('src');
        
        var carId = $(this).data('car-id');
        
        $('#fullImage').attr('src', imageUrl);
        
        $('#updateImageBtn').data('car-id', carId);
        
        $('#imageModal').modal('show');
    });
    $('#cancelButton').on('click', function() {
        $('#imageModal').modal('hide');
        $('#fullImage').attr('src', '');
    });

    $('#updateImageBtn').on('click', function() {
        var formData = new FormData();
        var imageFile = $('#imageUpload')[0].files[0]; 
        var carId = $(this).data('car-id'); 

        var car_image = carImageUpdate.replace('0', carId);

        if (imageFile) {
            formData.append('image', imageFile); 
            formData.append('car_id', carId); 

            var csrfToken = $('input[name="csrfmiddlewaretoken"]').val(); 

            formData.append('csrfmiddlewaretoken', csrfToken);

            $.ajax({
                url: car_image,
                type: 'POST',
                data: formData,
                contentType: false,  
                processData: false, 
                success: function(response) {
                    if (response.success) {
                        $('.car-thumbnail[data-car-id="' + carId + '"]').attr('src', response.new_image_url);

                        $('#imageModal').modal('hide');
                        $('#imageUpload').val('');
                    } else {
                        alert('Error: ' + response.error);
                    }
                },
                error: function(xhr, status, error) {
                    console.error('Error: ' + error);
                    alert('An error occurred while updating the image.');
                }
            });
        } else {
            alert('Please select an image to upload.');
        }
    });
    /*                  car statsu update */ 
 
    // When the Update Status button is clicked
    var scid;
    // Open modal on <td> click
    $('.car-status').on('click', function() {
        scid = $(this).data('car-id');
        $('#statusModal').modal('show');
    });

    // Handle the status update
    $('#updateStatusBtn').on('click', function() {
        var newStatus = $('#statusSelect').val();

        $.ajax({
            type: 'POST',
            url: carStatusUpdate.replace("0",scid),
            data: {
                'new_status': newStatus,
                'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
            },
            success: function(response) {
                if (response.success) {
                    $('#statusModal').modal('hide');
                    $('.car-status[data-car-id="' + scid + '"]').text(newStatus.toUpperCase());
                } else {
                    alert('Failed to update status');
                }
            },
            error: function() {
                alert('Error updating status');
            }
        });
    });

    /* search car  bu status */
    
       function showClearButton() {
            $('#clearFilter').show();
        }

        function hideClearButton() {
            $('#clearFilter').hide();
        }

        $('#showAvailable').click(function() {
            $('.car-record').hide();
            $('.car-record.available').show();
            showClearButton();
        });

        $('#showPending').click(function() {
            $('.car-record').hide();
            $('.car-record.pending').show();
            showClearButton();
        });

        $('#showNotAvailable').click(function() {
            $('.car-record').hide();
            $('.car-record.not_available').show();
            showClearButton();
        });

        $('#showONServices').click(function() {
            $('.car-record').hide();
            $('.car-record.services').show();  
            showClearButton();
        });

        $('#clearFilter').click(function() {
            $('.car-record').show();
            hideClearButton();
        });

        hideClearButton();
     
     function calculateRentPrices() {
        var pricePerHour = parseFloat($('#edit-par-hour-rent').val()); 
        var discount = parseFloat($('#edit-discount').val()); 

        if (!isNaN(pricePerHour) ) {
            var discountedPricePerHour = pricePerHour * (1 - (discount / 100));

            var pricePerDay = discountedPricePerHour * 24;

            var pricePerMonth = pricePerDay * 30;

            $('#edit-par-day-rent').val(pricePerDay.toFixed(2)); 
            $('#edit-par-month-rent').val(pricePerMonth.toFixed(2)); 
        } else {
            $('#edit-par-day-rent').val('');
            $('#edit-par-month-rent').val('');
        }
    }

    $('#edit-par-hour-rent, #edit-discount').on('input', function() {
        calculateRentPrices(); 
    });
    $('.edit-price').on('click', function() {
         carId = $(this).data('car-id');  
        $.ajax({
            url: update_car_ret_price.replace("0",carId),  
            type: 'GET',
            dataType: 'json',
            success: function(data) {
                if (data.error) {
                    alert('Car not found');
                } else {
                    $('#edit-par-hour-rent').val(data.price_per_hour);
                    $('#edit-par-day-rent').val(data.price_per_day);
                    $('#edit-par-month-rent').val(data.price_per_month);
                    $('#edit-discount').val(data.discount);  

                    $('#editCarRentModal').modal('show');
                }
            },
            error: function(xhr, status, error) {
                console.error('Error fetching car details: ' + error);
            }
        });
    });

    $('#editRentForm').on('submit', function(e) {
        e.preventDefault(); 
        var updatedHourRate = $('#edit-par-hour-rent').val();
        var updatedDayRate = $('#edit-par-day-rent').val();
        var updatedMonthRate = $('#edit-par-month-rent').val();
        var udatediscount=$('#edit-discount').val();
       
        $.ajax({
            url: update_car_ret_price.replace("0",carId), 
            type: 'POST',
            data: {
                price_per_hour: updatedHourRate,
                price_per_day: updatedDayRate,
                price_per_month: updatedMonthRate,
                discount: udatediscount,
                csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()  
            },
            success: function(response) {
                if (response.success) {
                        location.reload();
                        var updatedHourRate = response.updatedHourRate;
                        var updatedDayRate = response.updatedDayRate;
                        var updatedMonthRate = response.updatedMonthRate;
                        var updatedDiscount = response.updatedDiscount;
                
                        $('#car-par-hour-rent-' + carId).text(updatedHourRate.toFixed(2));
                        $('#car-par-day-rent-' + carId).text(updatedDayRate.toFixed(2));
                        $('#car-par-month-rent-' + carId).text(updatedMonthRate.toFixed(2));
                        $('#car-discount-' + carId).text(updatedDiscount.toFixed(2));
                
                        $('#editCarRentModal').modal('hide');
                        
                                                
                    
                } else {
                    alert('Failed to update the car rent details');
                }
            },
            error: function(xhr, status, error) {
                alert('There was an error updating the car rent details.');
            }
        });
    });
    $(".edit-car").on("click", function() {
        var carId = $(this).data("car-id");
    
        // AJAX call to fetch car data
        $.ajax({
            url: car_update.replace("0", carId),  // Make sure car_update has the correct URL format
            type: 'GET',
            success: function(response) {
                // Populate the form with the car details from the response
                $('#updateCarId').val(response.car.id);
                $('#updateCarNumber').val(response.car.number);
                $('#updateCarMake').val(response.car.make);
                $('#updateCarModel').val(response.car.model);
                $('#updateCarYear').val(response.car.year);
                $('#updateCarMileage').val(response.car.mileage);
                $('#updateCarType').val(response.car.type);
                $('#updateCarSeats').val(response.car.seats);
                $('#updateCarModal').modal('show');
            },
            error: function(xhr, status, error) {
                alert("An error occurred: " + error);
            }
        });
    });
    
    $('#updateCarForm').submit(function(e) {
        e.preventDefault();
        var carId = $('#updateCarId').val();

        var formData = new FormData(this);
    
        $.ajax({
            url: upate_car.replace("0",carId),  // Ensure 'update_car' is correct, should be the URL for updating
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                if (response.success) {
                    alert('Car details updated successfully!');
                    $('#updateCarModal').modal('hide');  // Close modal
                    location.reload();  // Optionally reload the page to reflect updates
                } else {
                    console.log('There was an error updating the car details: ' + JSON.stringify(response.errors));
                }
            },
            error: function(xhr, status, error) {
                alert("An error occurred during the update: " + error);
            }
        });
    });
    
    
});
