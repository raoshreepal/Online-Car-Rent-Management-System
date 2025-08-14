from django.urls import path
from .views  import *

urlpatterns = [
#if employee 

    path('', HomePageView.as_view(),name="home"),
    path('about/',AboutView.as_view(),name="about"),
  

    path('Services/', ServicesView.as_view(),name="services"),
    path('cars/', CarsView.as_view(),name="cars"),
    path('user/user-save-cars', UserSaveCarsRecordView.as_view(),name="user_save_cars"),
    path("car/car-single/<int:id>", CarSingle.as_view(), name="car-single"),
    path('blog/', CarBlog.as_view(),name="blog"),
    path('contact/', UserContact.as_view(),name="contact"),
    path('register/', UserRegistrationView.as_view(),name="register"),
    path('login/', CustomLoginView.as_view(),name="login"),
    path("pricing/", ShowPricing.as_view(),name="pricing"),
    path("profile/update-password/", UpdatePasswordView.as_view(),name="profile_update_password"),

    path("image-update",UpdateUserProfileImage.as_view(),name="update_user_rofile"),
    path('profile/', ShowProfile.as_view(),name="profile"),
    path("blog/blog-single",ShowBlog.as_view(),name="blog-single"),    
    path("user-logout",UserLogout.as_view(),name="user_logout"),
    path('update-profile/', UserProfileUpdateView.as_view(), name='update_user_profile'),
    path('update-password/', UserPasswordPage.as_view(), name="update_password"),
    path('404notfound',Error404View.as_view(), name='404notfound'),
    path('page_Redirect',ErrorPageRedirect.as_view(), name='error_page_redirect'),
    path('user-booing-record',UserBookingRecord.as_view(), name='user_booking_record'),

    # ------------ ajax -----------
    path('available-car/', AvailableCar.as_view(), name='availablecar'),
    path('car/car-booking/<int:id>/book', CarBookingView.as_view(), name='car_booking'),
    path('car/car-booking/driver-details/',DriverDetails.as_view(), name='driver_Details'),
    path('generate_invoice/', GenerateInvoiceView.as_view(), name='generate_invoice'),
    path('cancel-booking/<int:booking_id>/', CancelBookingView.as_view(), name='cancel_booking'),
    
    path('get-booking-details/<int:booking_id>/', GetBookingDetailsView.as_view(), name='get_booking_details'),
    path('user/save_car/<int:car_id>/', SaveCarView.as_view(), name='save_car'),
    path('user/saved_cars/count/', SavedCarCountView.as_view(), name='saved_cars_count'),







]
