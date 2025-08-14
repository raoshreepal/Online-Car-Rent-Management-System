$(document).ready(function() {
  
    // Use event delegation for dynamically added .view-user elements
    $('#userTableBody').on('click', '.view-user', function() {
        var userId = $(this).data('user-id');
        
        // Dynamically replace '0' with the actual userId
        var url = getUserDetailsUrl.replace('0', userId);

        // AJAX request to fetch user details
        $.ajax({
            url: url,
            type: 'GET',
            success: function(response) {
                // Populate modal with user details
                $('#viewUserName').text(response.name);
                $('#viewUserEmail').text(response.email);
                $('#viewUserContact').text(response.contact);
                $('#viewUserRole').text(response.role);
                $('#viewUserGender').text(response.gender);
                $('#totalBoking').text(response.bookings);
                $('#totalPayent').text("$"+response.user_payment);
                
                
                // Populate booking & payment details (if applicable)
                $('#bookingDetailsList').empty();
                

                // Show the modal
                $('#viewUserDetailsModal').modal('show');
            },
            error: function(xhr) {
                console.error("An error occurred while fetching user details.");
            }
        });
    });
    
    $('#userTableBody').on('click', '.edit-user', function() {
        var userId = $(this).data('user-id');

        // Dynamically replace '0' with the actual userId
        var url = getUserDetailsUrl.replace('0', userId);

        // AJAX request to fetch user details
        $.ajax({
            url: url,
            type: 'GET',
            success: function(response) {
                // Prepopulate the edit modal with user details (excluding the image)
                $('#editUserFirstName').val(response.name.split(' ')[0]);  // First Name
                $('#editUserLastName').val(response.name.split(' ')[1]);   // Last Name
                $('#editUserEmail').val(response.email);                   // Email
                $('#editUserPhoneNumber').val(response.contact);           // Phone number
                $('#editUserRole').val(response.role);             
                $('#editUserGender').val(response.gender); //        // Role

                // Store userId in the form for later use
                $('#editUserForm').data('user-id', userId);

                // Show the modal
                $('#editUserModal').modal('show');
            },
            error: function(xhr) {
                console.error("An error occurred while fetching user details.");
            }
        });
    });

    // Handle form submission to update user details
   $('#editUserForm').on('submit', function(event) {
    event.preventDefault();  // Prevent the default form submission

    var userId = $(this).data('user-id');
    var updatedData = {
        first_name: $('#editUserFirstName').val(),
        last_name: $('#editUserLastName').val(),
        email: $('#editUserEmail').val(),
        phone_number: $('#editUserPhoneNumber').val(),
        role: $('#editUserRole').val(),
        gender: $('#editUserGender').val()  // Add gender to the updated data
    };
    var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();

    // Dynamically replace '0' with the actual userId
    var url = updateUserDetailsUrl.replace('0', userId);

    // AJAX request to update the user details
    $.ajax({
        url: url,
        type: 'POST',
        data: updatedData,  // Send data in the body
        headers: {
            'X-CSRFToken': csrfToken  // Add CSRF token to the request headers
        },
        success: function(response) {
            // Close the modal
            $('#editUserModal').modal('hide');
    
            // Success notification
            $.notify({
                icon: 'icon-check',
                title: 'Success!',
                message: 'User details updated successfully.',
            }, {
                type: 'success',
                placement: {
                    from: "top",
                    align: "right"
                },
                time: 3000, // Display for 3 seconds
            });
            
            // Find the row of the user that was updated
            var userRow = $('#userTableBody').find(`tr[data-user-id="${userId}"]`);
            
            // Update the table row with the new user data
            userRow.find('.user-name').text(updatedData.first_name + ' ' + updatedData.last_name); // Update Name
            userRow.find('.user-email').text(updatedData.email); // Update Email
            userRow.find('.user-phone').text(updatedData.phone_number); // Update Phone Number
            userRow.find('.user-role').text(updatedData.role); // Update Role
            
            // Optionally, update the user image if it was changed
            if (updatedData.image) {
                userRow.find('img').attr('src', updatedData.image); // Update Image if provided
            }
    
            // Optionally, you can add some highlighting to show the row was updated
            userRow.addClass('updated-row');
            setTimeout(function() {
                userRow.removeClass('updated-row');
            }, 3000);  // Highlight for 3 seconds
        },
        error: function(xhr) {
            // Handle error (optional)
            $.notify({
                icon: 'icon-error',
                title: 'Error!',
                message: 'An error occurred while updating user details.',
            }, {
                type: 'danger',
                placement: {
                    from: "top",
                    align: "right"
                },
                time: 3000,
            });
        }
    });
    
});

  // Variables to store current page and items per page
  let currentPage = 1;
  const itemsPerPage = 5;
  let currentRole = 'all';
  let currentGender = 'all';
  let totalPages = 1;
  
  // Event delegation for filtering by role and gender
     // Click event to filter based on role buttons
     $(".filter-role").click(function () {
        var role = $(this).data("role");
        var gender = $('input[name="gender"]:checked').val() || 'all';  // Get selected gender
        currentPage = 1;  // Reset to first page on filter change
        filterUsers(role, gender);
    });

    // Search button click event
    $('input[name="role"], input[name="gender"]').on('change', function () {
        var role = $('input[name="role"]:checked').val() || 'all';  // Get selected role
        var gender = $('input[name="gender"]:checked').val() || 'all';  // Get selected gender
        currentPage = 1;  // Reset to first page on filter change
        filterUsers(role, gender);
    });

  function filterUsers(role, gender) {
    $.ajax({
        url: filterUsersUrl,
        type: 'GET',
        data: { role: role, gender: gender },
        success: function(response) {
            var userTableBody = $('#userTableBody');
            userTableBody.empty();

            if (response.users.length === 0) {
                userTableBody.append('<tr><td  colspan="8" style="text-align: center;">No records found.</td></tr>');
                $('#previousPage, #nextPage').hide();
                return;
            }

            // Calculate pagination
            totalPages = Math.ceil(response.users.length / itemsPerPage);
            const startIndex = (currentPage - 1) * itemsPerPage;
            const endIndex = startIndex + itemsPerPage;

            response.users.slice(startIndex, endIndex).forEach(function(user) {
                var genderClass = (gender !== 'all' && user.gender === gender) ? `${gender}-column` : '';
                var roleClass = (role !== 'all' && user.role === role) ? `${role}-column` : '';

                var userRow = `
                <tr>
                    <td style="text-align: center;">
                        ${user.image ? `<img class="rounded-circle" src="${user.image}" alt="${user.first_name} ${user.last_name}" style="width: 50px; height: 50px; object-fit: cover;">` : '-'}
                        <br>${user.username || '-'}
                    </td>
                    <td>${user.first_name || '-'} ${user.last_name || '-'}</td>
                    <td>${user.email || '-'}</td>
                    <td style="text-align: center;"> ${user.phone_number || '-'}</td>
                    <td style="text-align: center;"class="${genderClass}">${user.gender || '-'}</td>
                    <td style="text-align: center;" class="${roleClass}">${user.role || '-'}</td>
                    <td>${ user.date_joined }</td>
                    <td>
                        <i class="fas fa-eye text-primary view-user" data-user-id="${user.id}" style="cursor: pointer;" title="View Details"></i>
                        <i class="fas fa-edit text-warning edit-user ms-2" data-user-id="${user.id}" style="cursor: pointer;" title="Edit Details"></i>
                        <i class="fas fa-trash text-danger ms-2 delete-user" data-user-id="${user.id}" style="cursor: pointer;" title="Delete User"></i>  <!-- Delete icon -->

                        </td>
                </tr>
                `;

                userTableBody.append(userRow);
            });

            $('#previousPage').toggle(currentPage > 1);
            $('#nextPage').toggle(currentPage < totalPages);
        },
        error: function(xhr) {
            console.error("An error occurred while filtering users.");
        }
    });
}

  // Function to handle next page click
  $('#nextPage').on('click', function() {
      if (currentPage < totalPages) {
          currentPage++;
          filterUsers(currentRole, currentGender);
      }
  });
  
  // Function to handle previous page click
  $('#previousPage').on('click', function() {
      if (currentPage > 1) {
          currentPage--;
          filterUsers(currentRole, currentGender);
      }
  });
  
  // Initial load with default filters
  filterUsers(currentRole, currentGender);
  // add user  form
  $('#add-user-tab').on('click', function(e) {
    e.preventDefault();
    // Hide "View Users" and slide in "Add User" form
    $('#view-users').hide("slide", { direction: "left" }, 500);
    $(".hidetable").hide("slide", { direction: "left" }, 500);
    $('#add-user').show("slide", { direction: "right" }, 500);
    $(this).tab('show');
  });

  $('#view-users-tab').on('click', function(e) {
    e.preventDefault();
    // Hide "Add User" and slide in "View Users" form
    $('#add-user').hide("slide", { direction: "right" }, 500);
    $(".hidetable").show("slide", { direction: "left" }, 500);

    $('#view-users').show("slide", { direction: "left" }, 500);
    $(this).tab('show');
  });
  $('#add-user-tab').on('click', function(e) {
    e.preventDefault();
    $('#view-users').hide();
    $('#add-user').show();
    $(this).tab('show');
  });

  // Switch back to View Users when clicked
  $('#view-users-tab').on('click', function(e) {
    e.preventDefault();
    $('#add-user').hide();
    $('#view-users').show();
    $(this).tab('show');
  });

  $('#user-form').submit(function(event) {
    event.preventDefault(); // Prevent default form submission
    var formData = new FormData(this); // Collect form data
  
   $.ajax({
    type: 'POST',
    url: admin_add,  // Ensure this URL matches the one in your URLconf
    data: formData,
    processData: false,
    contentType: false,
    success: function(response) {
        if (response.success) {
            // Show success modal and update the user list
            $('#successModal').modal('show');
            fetchUsers();  // Assuming fetchUsers() will refresh the user list
        }else if (response.errors) {
            // Handle form errors and display them in the modal
            let errorMessages = '';
            $.each(response.errors, function(field, error) {
                // Append each error message to a string
                errorMessages += error + '<br>';
            });

            // Show the error messages in the modal
            $('.error-message').html(errorMessages);
            $('#errorModal').modal('show');  // Display the modal
        }
    },
    error: function(xhr, status, error) {
        // In case of an unexpected error, show a default error message
        $('.error-message').text("An unexpected error occurred. Please try again.");
        $('#errorModal').modal('show');
    }
});

});
  

  // Cancel button functionality
   // When the user types in the search box
  // When the user clicks the search icon
$('#searchIconBtn').on('click', function () {
    var query = $('#searchusername').val();  // Get the search query
    if (query.length >0 || query.length === 0) {
        $.ajax({
            url: user_search,  // The URL to send the request to
            method: 'GET',
            data: {
                'username': query  // Pass the search query as a parameter
            },
            success: function (response) {
                
                // Clear the table body
                // $('#userTableBody').empty();
                var userTableBody = $('#userTableBody');
                userTableBody.empty();
                // Loop through  the users and display them
                if (response.users.length === 0) {
                    userTableBody.append('<tr><td  colspan="8" style="text-align: center;">No records found.</td></tr>');
                    $('#previousPage, #nextPage').hide();
                    return;
                } else {
                    $(".usernotsearch").hide();
                    response.users.forEach(function (user) {
                        // Check and set user image, use placeholder if not available
                        var userImage = user.image ? 
                                        `<img class="rounded-circle" src="${user.image}" alt="${user.first_name} ${user.last_name}" style="width: 50px; height: 50px; object-fit: cover;">` : 
                                        'Not atech';

                        // Check for username, first_name, last_name, email, phone_number, gender, role, and date_joined
                        var username = user.username || '-';
                        var fullName =user.name || '-';
                        var email = user.email || '-';
                        var phoneNumber = user.contact  || '-';
                        var gender = user.gender || '-';
                        var role = user.role || '-';
                        var dateJoined = user.date_joined || '-';

                        // Dynamic CSS classes based on gender or role (optional)
                        var genderClass = user.gender ? 'text-' + user.gender.toLowerCase() : '';
                        var roleClass = user.role ? 'text-' + user.role.toLowerCase() : '';

                        // Construct the row HTML using template literals
                        var userRow = `
                        <tr>
                            <td style="text-align: center;">
                                ${userImage}
                                <br>${username}
                            </td>
                            <td>${fullName}</td>
                            <td>${email}</td>
                            <td style="text-align: center;">${phoneNumber}</td>
                            <td style="text-align: center;" class="${genderClass}">${gender}</td>
                            <td style="text-align: center;" class="${roleClass}">${role}</td>
                            <td>${dateJoined}</td>
                            <td>
                                <i class="fas fa-eye text-primary view-user" data-user-id="${user.id}" style="cursor: pointer;" title="View Details"></i>
                                <i class="fas fa-edit text-warning edit-user ms-2" data-user-id="${user.id}" style="cursor: pointer;" title="Edit Details"></i>
                                <i class="fas fa-trash text-danger ms-2 delete-user" data-user-id="${user.id}" style="cursor: pointer;" title="Delete User"></i>  <!-- Delete icon -->

                                </td>
                        </tr>
                        `;
                        // Append the row to the table body
                        $('#userTableBody').append(userRow);
                    });
                }
            },
            error: function () {
                $(".usernotsearch").show();
            }
        });
    }
});
$('#pdfButton').on('click', function () {
    // Trigger the AJAX call to generate the PDF
    $.ajax({
        url: user_pdf_records,  // URL for the PDF generation view
        method: 'GET',
        success: function (response) {
            // Open the PDF in a new tab
            window.open(response.pdf_url, '_blank');
        },
        error: function () {
            alert("There was an error generating the PDF.");
        }
    });
});
/* user delete */
$(document).on('click', '.delete-user', function() {
    var userId = $(this).data('user-id');  // Get the user ID from the data attribute

    // Confirm the deletion with the user
    if (confirm("Are you sure you want to delete this user?")) {
        $.ajax({
            url: admin_user_delete,  // URL of the Django view
            method: 'POST',
            data: {
                'user_id': userId  // Send the user ID to the server
            },
            headers: {
                'X-CSRFToken': getCookie('csrftoken')  // Include the CSRF token in the headers
            },
            success: function(response) {
                if (response.success) {
                    // On success, remove the row from the table
                    $(`tr[data-user-id="${userId}"]`).remove();
                    alert('User deleted successfully.');
                } else {
                    alert('Error deleting user: ' + response.message);
                }
            },
            error: function(xhr, status, error) {
                alert('An error occurred. Please try again.');
            }
        });
    }
});

// Function to get the CSRF token from the cookie
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


});

