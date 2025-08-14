from django.urls import path
from .views import *

urlpatterns = [
    # Employee Pages
    path('', EmployeeIndexView.as_view(), name='employee_dashboard'),
    path('employee/notification/', EmployeeNotificationView.as_view(), name='employee_notification'),

    # Employee Profile Pages
    path('employee/profile/', EmployeeProfileView.as_view(), name='employee_profile'),
    path('employee/profile/image-update/',EmployeeImageUpdateView.as_view(),name="update_employee_profile_image"),
    path('employee/profile/mybalance/', MyBalanceView.as_view(), name='my_balance'),
    path('employee/profile/update/', UpdateEmployeeProfileView.as_view(), name='update_employee_profile'),
    path('employee/profile/add-user-car-booking/', AddUserView.as_view(), name='add_user'),

    # Car Record Pages
    path('employee/car-record/add-update/', AddUpdateCarView.as_view(), name='addUpdateCar'),
    path('employee/car-record/available/', AvailableCarsView.as_view(), name='available_cars'),
    path('employee/car-record/status/', EmployeeCarStatusView.as_view(), name='carstatus'),

    # Car Services Record Pages
    path('employee/car-services/add/', AddServicesCarsView.as_view(), name='addServicesCars'),
    path('employee/car-services/payment/', CarServicesPaymentView.as_view(), name='carServicesPayment'),
    path('employee/car-services/record/', CarServicesRecordView.as_view(), name='carServicesRrecord'),
    path('employee/car-services/confirm/', ConfirmServicesView.as_view(), name='confirmServices'),

    # Location Pages
    path('employee/location/googlemaps/', GoogleMapsView.as_view(), name='googleMaps'),
    path('employee/location/jsvectormap/', JSVectorMapView.as_view(), name='jsvectorMap'),

    # Booking Pages
    path('employee/booking/record/', BookingRecordView.as_view(), name='booking_record'),
    # notification
    path('employee/dashboard/notifications/', NotificationView.as_view(), name='get_pending_bookings'),
    path('employee/booking-record/confirm-booking/', ConfirmBookingView.as_view(), name='confirm_booking'),
    path('employee/employee-booking-record/generatepdf/', EmployeeBookingPdfView.as_view(), name='generate_employee_pdf'),
    #chart
    path("emplloyee-deshboard/get-car-statistics/", CarStatisticsView.as_view(), name="car_statistics"),
    path("emplloyee/employee-dashboard/accept-pending-car-requests/", ConfirmBookingsView.as_view(),name="accept_pending_car_request"),
    path("employee/employee-dashboard/calendar",PickupLocationView.as_view(),name="displaycalendar"),
    path("employee/employee-user-booking/user-details/", UserBookingsView.as_view(), name='user_bookings'),
    path("employee/employee/user-car-booking/get-car-details",CarDetailsView.as_view(),name="get_car_details"),
    path("employee/car-record/update-car-image/",UpdateCarImageView.as_view(),name="update_car_image"),
    path("employee/dashboard/calendar/",DisplayCalendarView.as_view(),name="get_calendar"),
    path("employee/dashboard/calendar/get-all-date",EmployeeEventDataView.as_view(),name="get_employee_all_date"),
    path("employee/dashbiard/userfeedback/",UserFeedbackView.as_view(),name="user_feedback"),
    path("employee-dashboard/dashboard/feedback/",MyUserFeedback.as_view(),name="user_feedback_page"),
        path("employee-dashboard/dashboard/feedback/send_replay",ReplyFeedbackView.as_view(),name="send_replay")


    
]
