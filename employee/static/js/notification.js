$(document).ready(function() {

  function fetchPendingBookings() {
    $.ajax({
      url: notificationUrl,  
      method: 'GET',
      success: function(response) {
          $('#notif-count').text(response.pending_bookings_count);
          $('#notif-text').text(response.pending_bookings_count);

          $('#notif-details').empty();

          if (response.pending_bookings_count > 0) {
            response.bookings_data.forEach(function(booking) {
              var bookingHtml = '<a href="#">' +
                                  '<div class="notif-icon notif-warning">' +
                                    '<i class="fa fa-car"></i>' +
                                  '</div>' +
                                  '<div class="notif-content">' +
                                    '<span class="block">Booking for car: ' + booking.car_name + ' is pending</span>' +
                                    '<span class="time">' + booking.booking_at +" "+ booking.bookking_at_time+'</span>' +
                                  '</div>' +
                                '</a>';
              $('#notif-details').append(bookingHtml);
            });
          } else {
            // Show a message if there are no pending bookings
            $('#notif-details').append('<div class="notif-content"><span class="block">No pending bookings</span></div>');
          }
        },
      error: function(xhr, errmsg, err) {
        console.log("Error fetching pending bookings:", errmsg);
      }
    });
  }

  // Trigger the function on page load
  fetchPendingBookings();

  // Optional: Set up periodic updates (e.g., every 30 seconds)
  setInterval(fetchPendingBookings, 30000); // Refresh every 30 seconds
});
$(document).ready(function () {
  function toggleAcceptAllRequest() {
      if ($(".form-check-input:checked").length > 0) {
          $('#acceptallrequest').show();
      } else {
          $('#acceptallrequest').hide();
      }
  }

  // Toggle checkbox when an individual booking is clicked
  $('.checked_booking').on('click', function() {
      var checkbox = $(this).closest('.item-list').find('.form-check-input');
      checkbox.prop('checked', !checkbox.prop('checked'));
      toggleAcceptAllRequest();
  });

  // Handle "Select All" Click
  $("#selectAll").on("click", function () {
      $(".form-check-input").prop("checked", true);
      toggleAcceptAllRequest();
  });

  // Handle "Cancel Selection" Click
  $("#cancelSelection").on("click", function () {
      $(".form-check-input").prop("checked", false);
      toggleAcceptAllRequest();
  });

  // Handle "Accept All Requests" Click
  $("#acceptallrequest").on("click", function () {
      var selectedBookings = $(".form-check-input:checked").map(function () {
          return $(this).val();
      }).get();

      if (selectedBookings.length === 0) {
          alert("No bookings selected!");
          return;
      }

      $.ajax({
          url: accept_url,  
          type: "POST",
          headers: { 
              "X-CSRFToken": getCookie('csrftoken')  
          },  
          data: {
              booking_ids: selectedBookings,
          },
          success: function (response) {
              if (response.success) {
                  $('#successModal').show('show');
                                              location.reload(); 

                  selectedBookings.forEach(function(booking_id) {
                      $('.checked_booking[data-booking-id="' + booking_id + '"]').remove();
                  });

                  selectedBookings.forEach(function(booking_id) {
                      $('#checkbox-' + booking_id).prop('disabled', true); 
                  });
                  location.reload();  


              } else {
                  alert("Failed to confirm bookings!");
              }
          },
          error: function () {
              alert("Error processing request!");
          }
      });
  });

  // Function to get CSRF token from cookies
  function getCookie(name) {
      var cookieValue = null;
      if (document.cookie && document.cookie !== '') {
          var cookies = document.cookie.split(';');
          for (var i = 0; i < cookies.length; i++) {
              var cookie = cookies[i].trim();
              if (cookie.substring(0, name.length + 1) === (name + '=')) {
                  cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                  break;
              }
          }
      }
      return cookieValue;
  }
  function loadFeedbacks() {
    $.ajax({
        url: feedbackUrl,  // Django URL
        dataType: "json",
        success: function (response) {
            let feedbackList = response.feedbacks;
            let notifCenter = $(".feedback-notif-center");
            let notifCount = $("#notifs-count");

            notifCenter.empty();  // Purana data clear karo
            notifCount.text(feedbackList.length);  // Notification count update karo

            if (feedbackList.length > 0) {
                feedbackList.forEach(function (feedback) {
                    let feedbackHTML = `
                             <a href="#" class="notif-item d-flex align-items-center p-2 border-bottom">
    <div class="notif-img">
        <img style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover;" 
             src="${feedback.image}" alt="Profile Img">
    </div>
    <div class="notif-content ms-3">
        <span class="subject fw-bold d-block">${feedback.name}</span>
        <span class="block text-muted small">${feedback.description}</span>
        <span class="time text-secondary d-block small">${feedback.created_at}</span>
    </div>
</a>

                      `;
                    notifCenter.append(feedbackHTML);
                });
            } else {
                notifCenter.append('<p class="text-center text-muted">No feedback available</p>');
            }
        },
        error: function (xhr, status, error) {
            console.error("Error fetching feedbacks:", error);
        }
    });
}

// Call the function every 30 seconds
setInterval(loadFeedbacks, 30000);
loadFeedbacks();  // Initial call

});


