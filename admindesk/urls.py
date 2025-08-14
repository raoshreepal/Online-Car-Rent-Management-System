from django.urls import path
from .views import *
from django.views.generic import RedirectView

urlpatterns = [
    # Admin Pages
    path('', AdminIndexView.as_view(), name='admin_index'),
    path('admin-dashboard/login/', AdminLoginView.as_view(), name='admin_login'),
    # path('admin-dashboard/logout/',AdminLogoutView.as_view(), name='admin_logout'),
    path('admin-dashboard/notification/', AdminNotificationView.as_view(), name='admin_notification'),

    # Admin Profile Pages
    path('admin-dashboard/admin-profile/', AdminProfileView.as_view(), name='admin_profile'),
    path('admin-deshboard/profile/update-image',UpdateAdminImage.as_view(), name='update_admin_image'),
    
    path('admin-dashboard/profile/update/', UpdateAdminProfileView.as_view(), name='update_admin_profile'),
    path('admin-dashboard/user-management/', AddUserView.as_view(), name='user_management'),

    # Car Record Pages
    path('admin-dashboard/car-record/add-update/', AddUpdateCarView.as_view(), name='add_update_car'),
    path('admin-dashboard/car', AvailableCarsView.as_view(), name='car_management'),
    # path('admin-dashboard/car-record/status/', CarStatusView.as_view(), name='car_status'),

    # Car Services Record Pages
    path('admin-dashboard/car-services/add/', AddServicesCarsView.as_view(), name='add_services_cars'),
    path('admin-dashboard/car-services/payment/', CarServicesPaymentView.as_view(), name='car_services_payment'),
    path('admin-dashboard/car-services-management', CarServicesRecordView.as_view(), name='car_services_management'),
    # path('admin-dashboard/car-services/confirm/', ConfirmServicesView.as_view(), name='confirm_services'),


    # Booking Pages
    path('admin-dashboard/report/', BookingRecordView.as_view(), name='report'),
    path('admin-dashboad/maintenance',CarMaintenance.as_view(),name="maintenance"),
    path('admin-dashboad/maintenance/get-services/<int:car_id>',GetServicesView.as_view(),name="maintenance-get-car-details"),
    

    path('admin-dashboard/Employee-Management',EmployeeManagement.as_view(),name="employee_management"),
    path("admin-desk/booking-management/",BookingManagement.as_view(),name="booking_management"),


    #__________ajax  fiels______________________
    path("admin-dashboard/user-management/<int:id>/", GetUserDetails.as_view(), name="get_user_details"),
        path('admin-dashboard/user-management/filter/', FilterUsersView.as_view(), name='filter_users'),
        path('admin-dashboard/update-user/<int:id>/', UpdateUserDetails.as_view(), name='update_user_details'),
        path("admin-dashboard/user-management/adduser/",AdminAddUser.as_view(),name="admin_Add_user"),
        path("admin-dashboard/user-management/user-search/", UserSearchView.as_view(), name='user_search'),
        path("admin-dashboard/user-management/user-pdf-records/",UserPdfRecord.as_view(), name='user_pdf_records'),
    path("admin-dashboard/user-management/user-delete/",DeleteUserView.as_view(), name="admin_user_Delete"),
    # --------------- add update delete car ajax ----------
    path('admin-dashboard/admin-desk/car-management/car-details/<int:car_id>/', CarDetailsView.as_view(), name='car_details'),
    path('admin-dashboard/admin-desk/car-management/car-image-update/<int:car_id>/', CarImageUpdate.as_view(), name='car_image_update'),
    path('admin-dashboard/admin-desk/car-management/car-status-update/<int:car_id>/', CarStatusUpdate.as_view(), name='car_status_update'),

    # ----------- car services ajax --------
    path("admin-dashboard/car-services-management/services-status/<int:record_id>/", ServicesCarStatusUpdate.as_view(), name='services_status_url'),    
    path("admin-dashboard/car-services-management/services-status/delete-services-car/<int:record_id>/",DeleteServicesCar.as_view(), name='delete_services_car_url'),
    #-------- redirect -------

    path('admin-desk/car-management/update-car-ret-price/<int:car_id>',UpdateCarRentPrice.as_view(), name='update_car_ret_price'),
    path('admin-desk/employee-manageemt/employee-details/',EmployeeAllDetailsView.as_view(),name="eployee_all_details"),
    path("adminidesk/base/notification",NotificationView.as_view(),name="get_notification_count"),
    path("admin-desk/index/display-chart/",DailyReportView.as_view(),name="admin_index_chart"),
    
    
    path("admin-desk/get-employee-car-boking/select-emplyee/",EmployeeListView.as_view(),name="get_employee"),
    path("admin-desk/get-employee-car-boking/confirm-pending-booking/",ConfirmBookingView.as_view(),name="confirm_employee_booking"),
    path("admin-desk/cancle-pending-booking/",CancelBookingView.as_view(),name="cancled_booking"),
    
    
    path("admin-desk/booking-managementget/booking-details/", GetBookingDetailsView.as_view(), name="get_booking_details"),
    path("admin-desk/booking-management/booking-form/get-car-price/<int:car_id>/", CarPriceView.as_view(), name="get_car_price"),
    path("admin-desk/car-management/get-car-update-details/<int:car_id>/edit", CarUpdateView.as_view(),name="car_update_details" ),
    path("admin-desk/car-management/car-update-details/<int:car_id>", UpdateCarView.as_view(),name="update_car_record" ),
    path('admin-desk/dashboard/calendar',CalendarView.as_view(),name="calendar"),
    path("admin-desk/dashboard/calendar/events/", EventDataView.as_view(), name="get_events"),
     path("admin-desk/dashboard/employee-management/get-employee-details/", GetEmployeeDetailsView.as_view(), name="get_employee_details"),
    path("admin-desk/dashboard/employee-management/update-employee/", UpdateEmployeeView.as_view(), name="update_employee"),
    path('admin-desk/dashboard/employee-management/report/booking-report/export-booking-report/', ExportBookingReportView.as_view(), name='export_booking_report'),
        path('admin-desk/dashboard/employee-management/report/service-report/export-services-report/', ExportServicesReportView.as_view(), name='export_services_report'),


]
