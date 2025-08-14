$(document).ready(function() {
    function fetchPendingBookings() {
      $.ajax({
        url: notification_url,  // Ensure notification_url is defined
        method: 'GET',
        success: function(response) {
        
            // Update the count of pending bookings
            $('#notif-count').text(response.pending_bookings_count);
            $('#notif-text').text(response.pending_bookings_count);
        
            $('#notif-details').empty();  // Clear existing notifications
        
            if (response.pending_bookings_count > 0) {
                // Check if bookings_data exists and is an array
                if (response.bookings_data && Array.isArray(response.bookings_data)) {
                    // Loop through bookings data and build the notification HTML
                    let notificationsHtml = response.bookings_data.map(function(booking) {
                        return `
                            <a href="#">
                                <div class="notif-icon notif-warning">
                                    <i class="fa fa-car"></i>
                                </div>
                                <div class="notif-content">
                                    <span class="block">Booking for car: ${booking.car_name} is pending</span>
                                    <span class="time">${booking.booking_at} ${booking.bookking_at_time}</span>
                                </div>
                            </a>
                        `;
                    }).join('');  // Join the array of HTML into a single string
        
                    $('#notif-details').append(notificationsHtml);  // Append all notifications at once
                } else {
                    console.error("bookings_data is missing or not an array:", response.bookings_data);
                }
            } else {
                // If no bookings, show a default message
                $('#notif-details').append('<div class="notif-content"><span class="block">No pending bookings</span></div>');
            }
        },
        error: function(xhr, errmsg, err) {
          console.log("Error fetching pending bookings:", errmsg);
        }
      });
    }
  
    fetchPendingBookings();
  
    setInterval(fetchPendingBookings, 30000); // Refresh every 30 seconds
});
$(document).ready(function () {
    fetchChartData();  // Fetch chart data when page loads

    function fetchChartData() {
        $.ajax({
            url: "admin-desk/index/display-chart/",  // Django class-based view URL
            method: "GET",
            dataType: "json",
            success: function (response) {
                // Pass the received data to the chart rendering function
                renderStackedBarChart(response);
            },
            error: function (xhr, errmsg, err) {
                console.log("Error fetching data for chart:", errmsg);
            }
        });
    }

    function renderStackedBarChart(data) {
        var canvas = document.getElementById("statisticsChart").getContext("2d");
    
        // Ensure the canvas width is large enough
    
    
    
        var stackedBarChart = new Chart(canvas, {
            type: "bar",
            data: {
                labels: ["Total Cars", "Available Cars", "Pending Cars", "Rented Cars", "Services"],
                datasets: [
                    {
                        label: "Total Cars",
                        backgroundColor: "#88E788",
                        data: [data.total_cars, 0, 0, 0, 0],
                        borderColor: "#1e7e34",
                        borderWidth: 1,
                        borderRadius: 5,  // Rounded corners for bars

                        hoverBackgroundColor: "#218838",
                        hoverBorderColor: "#155d27",
                    },
                    {
                        label: "Available Cars",
                        backgroundColor: "#28a745",
                        data: [0, data.available_cars, 0, 0, 0],
                        borderColor: "#1e7e34",
                        borderWidth: 1,
                        borderRadius: 5,  // Rounded corners for bars

                        hoverBackgroundColor: "#218838",
                        hoverBorderColor: "#155d27",
                    },
                    {
                        label: "Pending Cars",
                        backgroundColor: "#E67E22",
                        data: [0, 0, data.pendings, 0, 0],
                        borderColor: "#c79b00",
                        borderWidth: 1,
                        borderRadius: 5,

                        hoverBackgroundColor: "#e69a00",
                        hoverBorderColor: "#bf8500",
                    },
                    {
                        label: "Rented Cars",
                        backgroundColor: "#007bff",
                        data: [0, 0, 0, data.rented_cars, 0],
                        borderColor: "#0056b3",
                        borderWidth: 1,
                        borderRadius: 5,

                        hoverBackgroundColor: "#0056b3",
                        hoverBorderColor: "#004085",
                    },
                    {
                        label: "Services",
                        backgroundColor: "#ffc107",
                        data: [0, 0, 0, 0, data.services],
                        borderColor: "#e0a800",
                        borderWidth: 1,
                        borderRadius: 5,

                        hoverBackgroundColor: "#e0a800",
                        hoverBorderColor: "#d39e00",
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false, // Allow flexible sizing
                scales: {
                    x: {
                        beginAtZero: true,
                        stacked: true,
                        grid: {
                             display: true, 
                             color: "#ddd",
                              borderColor: "#ccc", 
                              borderWidth: 1 
                            },
                        ticks: { 
                            font: { 
                                size: 14, family: "'Arial', sans-serif" 
                            }, 
                            color: "#333" },
                        // Increase bar width
                       
                        

                    },
                    y: {
                        beginAtZero: true,
                        stacked: true,
                        grid: { 
                            display: true, 
                            color: "#ddd" 
                        },
                        ticks: { 
                            font: { 
                                size: 14, family: "'Arial', sans-serif"
                             }, 
                             color: "#333" },
                    },
                },
                plugins: {
                    legend: {
                        display: true,
                        position: "top",
                        labels: { font: { size: 14, family: "'Arial', sans-serif" }, color: "#333" },
                    },
                    tooltip: {
                        enabled: true,
                        backgroundColor: "#fff",
                        titleColor: "#333",
                        bodyColor: "#333",
                        borderColor: "#ccc",
                        borderWidth: 1,
                        titleFont: { size: 14, family: "'Arial', sans-serif" },
                        bodyFont: { size: 12, family: "'Arial', sans-serif" },
                    },
                },
            },
        });
    }
   
    
    

    // Auto-refresh chart every 30 seconds
});

$(document).ready(function () {
    var selectedBookingId = null;

    // Open modal on button click
    $(".openModal").click(function () {
        selectedBookingId = $(this).data("id"); 
        var urls = window.location.origin + "/admindesk/admin-desk/get-employee-car-boking/select-emplyee/";

        // Fetch employee list via AJAX
        $.ajax({
            url: urls, // Django URL to fetch employee data
            type: "GET",
            success: function (data) {
                var employeeDropdown = $("#employeeSelect");
                employeeDropdown.empty(); // Clear existing options
                
                // Append new employee options
                $.each(data.employees, function (index, employee) {
                    employeeDropdown.append(
                        `<option value="${employee.id}"> ${employee.username}</option>`
                    );

                });

                $("#employeeModal").modal("show"); // Open the modal
            },
            error: function () {
                alert("Error fetching employees");
            }
        });
    });


    // Handle confirm booking
    $("#confirmBooking").click(function () {
        var selectedEmployeeId = $("#employeeSelect").val();

            console.log("idddddd"+selectedBookingId)
        if (!selectedEmployeeId || !selectedBookingId) {
            alert("Please select an employee.");
            return;
        }


        $.ajax({
            url:"/admindesk/admin-desk/get-employee-car-boking/confirm-pending-booking/" , // Django view URL to confirm booking
            type: "POST",
            data: {
                booking_id: selectedBookingId,
                employee_id: selectedEmployeeId,
                csrfmiddlewaretoken: "{{ csrf_token }}" // CSRF token for security
            },
            success: function (response) {
                alert(response.message);
                $("#employeeModal").modal("hide"); // Close modal
                location.reload(); // Reload to update the UI
            },
            error: function () {
                alert("Error confirming booking.");
            }
        });
    });
});



// cancle booking
$(document).ready(function () {
    var selectedBookingId = null;

    // Open modal on cancel button click
    $(".openCancelModal").click(function () {
        selectedBookingId = $(this).data("id"); // Get the booking ID from button
        $("#cancelModal").modal("show"); // Open the modal
    });

    // Handle cancel booking
    $("#cancelBooking").click(function () {
        if (!selectedBookingId) {
            alert("Invalid booking.");
            return;
        }
        var urls = window.location.origin + "/admindesk/admin-desk/cancle-pending-booking/";
        var csrfToken = $("#csrfForm input[name='csrfmiddlewaretoken']").val();

        $.ajax({
            url: urls, 
            type: "POST",
            data: {
                booking_id: selectedBookingId,
                csrfmiddlewaretoken: csrfToken  
            },
            success: function (response) {
                alert(response.message); 
                $("#cancelModal").modal("hide"); 
                location.reload(); 
            },
            error: function () {
                alert("Error canceling the booking.");
            }
        });
    });
});

// print the chart
