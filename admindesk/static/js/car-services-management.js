$(document).ready(function () {
    // Show Clear Filter button

    function showClearButton() {
      $('#clearFilter').show();
    }

    // Hide Clear Filter button
    function hideClearButton() {
      $('#clearFilter').hide();
    }

    // Filter by Pending status
    $('#filterPending').click(function () {
      $('#serviceTableBody tr').each(function () {
        if ($(this).hasClass('pending')) {
          $(this).show();
        } else {
          $(this).hide();
        }
      });
      showClearButton();
    });

    // Filter by Complete status
    $('#filterComplete').click(function () {
      $('#serviceTableBody tr').each(function () {
        if ($(this).hasClass('completed')) {
          $(this).show();
        } else {
          $(this).hide();
        }
      });
      showClearButton();
    });

    $('#clearFilter').click(function () {
      $('#serviceTableBody tr').show();
      hideClearButton();
    });

    hideClearButton();
    $('.service-status').click(function() {
      var recordId = $(this).data('id');
      $('#serviceRecordId').val(recordId);
      $('#statusModal').modal('show');
    });
    
    $('#statusForm').submit(function(e) {
      e.preventDefault();
      var recordId = $('#serviceRecordId').val();
      var newStatus = $('#newStatus').val();
      var completeDate = newStatus === 'complete' ? new Date().toISOString() : null;
    
      var services_status_url = car_services_status_url.replace("0", recordId);
    
      $.ajax({
        type: 'POST',
        url: services_status_url,
        data: {
          'new_status': newStatus,
          'complete_date': completeDate,
          'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
        },
        success: function(response) {
          if (response.success) {
            $('#statusModal').modal('hide');
            $('[data-id="' + recordId + '"]').text(newStatus);
            $('[data-id="' + recordId + '"]').data('status', newStatus);
            
            if (newStatus === 'complete') {
              $('[data-id="' + recordId + '"]').closest('tr').find('.complete-date').text(response.complete_date);
            }
          } else {
            alert('Failed to update status');
          }
        },
        error: function() {
          alert('Error updating status');
        }
      });
    });
    
    $('#setNow').click(function() {
      var now = new Date().toISOString().split('T')[0];
      $('#statusDate').val(now);
    });
    /* add service car */
      // Open modal when 'Add Service' button is clicked
      $('#addServiceButton').click(function() {
        $('#addServiceModal').modal('show');
        
    });

    // Load available cars dynamically
   

   

    // Form submission via AJAX
    $('#addServiceForm').submit(function(e) {
        e.preventDefault(); // Prevent default form submission

        var formData = {
            'car': $('#car').val(),
            'employee': $('#employee').val(),
            'service_type': $('#service_type').val(),
            'service_date': $('#service_date').val(),
            'cost': $('#cost').val(),
            'description': $('#description').val(),
            'status': $('#status').val(),
            'complete_date': $('#complete_date').val(),
            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
        };

        $.ajax({
            type: 'POST',
            url: '{% url "services_car_create" %}', // Replace with your actual URL
            data: formData,
            success: function(response) {
                if (response.success) {
                  alert("submitt")
                    $('#addServiceModal').modal('hide');
                    alert('Service added successfully!');
                } else {
                    alert('Failed to add service');
                }
            },
            error: function() {
                alert('Error while adding service');
            }
        });
    });


   /* delete services car */
   $('.delete-btn').on('click', function(e) {
        e.preventDefault();
        var carId = $(this).data('id');
        alert(carId)
        $('#confirmDeleteModal').modal('show');
        $('#confirmDeleteBtn').on('click', function() {
            $.ajax({
                url: delete_car_url.replace("0",carId),// URL for delete view
                method: 'POST',
                data: {
                    'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()  // CSRF token
                },
                success: function(response) {
                    if (response.success) {
                        $('#confirmDeleteModal').modal('hide');
                        $('a[data-id="'+ carId +'"]').closest('tr').remove();
                    } else {
                        alert('Error deleting the car record');
                    }
                },
                error: function() {
                    alert('Error deleting the car record');
                }
            });
        });
    });
});