# Generic Views
from django.views.generic import TemplateView, View, CreateView, UpdateView
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.db.models import Count

from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView
from .forms import BookingForm
from .models import Booking, Car, User ,UserFeedback
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.contrib import messages
from collections import defaultdict
from django.dispatch import Signal

from customer.signals import password_updated  # Import the correct signal

# Forms
from .forms import UserRegistrationForm, LoginForm ,BookingForm ,GetUserFeedbackForm
from django.template.loader import render_to_string

# Models
from django_countries import countries
from django.views.generic.edit import FormView  
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.db.models.functions import Lower

from django.contrib.auth import authenticate, login, get_user_model
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views import View
from .forms import LoginForm
from django.http import HttpResponseRedirect
from .tasks import display_registered_user_info ,login_user ,logout_user ,booking_success_notification ,feedback_submission_notification ,password_update_notification

class UserRegistrationView(CreateView):
    template_name = 'register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        # Save the form to get the user instance
        user = form.save()

        print('User object:', user)
        print('Username:', user.username)

        # Call Celery task
        display_registered_user_info.delay(
            user.username,
            user.first_name,
            user.last_name, 
            user.email, 
            user.phone_number, 
            user.role,
        )

        messages.success(
            self.request, f"Your account '{user.username}' has been created successfully. You can now log in."
        )

        # Ensure redirection to login page
        return HttpResponseRedirect(self.success_url)


User = get_user_model()  # Get the user model dynamically

class CustomLoginView(View):
    template_name = 'login.html'

    def get(self, request):
        form = LoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user_exists = User.objects.filter(username=username).exists()

            if not user_exists:
                form.add_error('username', "Username not found.")  
            else:
                user = authenticate(request, username=username, password=password)
                
                if user is None:
                    form.add_error('password', "inorrect password.")  
                else:
                    login(request, user)
                    login_user.delay(username)
                    return redirect('home')

        return render(request, self.template_name, {'form': form})  
class UserLogout(TemplateView):
    def get(self, request, *args, **kwargs):
        user = request.user  # Get the user object
        username = user.username  # Extract the username as a string
        print('user: ', username)  # Debugging
        
        logout(request)  # Logout the user
        logout_user.delay(username)  # Pass only the username string

        return redirect('home')

class ShowProfile(LoginRequiredMixin, TemplateView):
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        bookings = Booking.objects.filter(user=user)

        pending_feedbacks = [booking for booking in bookings if not UserFeedback.objects.filter(car=booking).exists()]

        context["booking"] = bookings
        if pending_feedbacks:
            context["feedback_form"] = GetUserFeedbackForm()
            context["pending_feedbacks"] = pending_feedbacks

        return context

    def post(self, request, *args, **kwargs):
        if request.method == "POST":
            booking_id = request.POST.get("booking_id")  
            if not booking_id:
                messages.error(request, "Car is required!")  
                return redirect("profile")  

            try:
                booking = Booking.objects.get(id=booking_id)  
            except Booking.DoesNotExist:
                messages.error(request, "Selected booking does not exist!")  
                return redirect("profile")

            # Create feedback
            rating = request.POST.get("rating")
            comments = request.POST.get("comments")
            feedback = UserFeedback.objects.create(
                car=booking,
                rating=rating,
                comments=comments
            )

            # ✅ Call Celery Task
            feedback_submission_notification.apply_async(
                args=[request.user.username, booking.car.model, rating, comments]
            )

            messages.success(request, "Feedback submitted successfully!")  
            return redirect("profile")  

        messages.error(request, "Invalid request method!")  
        return redirect("profile")

    

User = get_user_model()
@method_decorator(login_required, name='dispatch')
class UserProfileUpdateView(UpdateView):
    def post(self, request, *args, **kwargs):
        user = request.user
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        phone_number = request.POST.get("phone_number")
        email = request.POST.get("email")
        gender = request.POST.get("gender")

        # Validate data
        if not username or not first_name or not last_name or not email:
            return JsonResponse({"status": "error", "message": "All fields are required."}, status=400)

        # Update user details
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.phone_number = phone_number
        user.email = email
        user.gender = gender
        user.save()

        return JsonResponse({"status": "success", "message": "Profile updated successfully."})
class UpdateUserProfileImage(TemplateView):

    def post(self, request, *args, **kwargs):
        if request.FILES.get('image'):
            image = request.FILES['image']
            user = request.user  

            user.image = image  
            user.save()

            return JsonResponse({'status': 'success', 'new_image_url': user.image.url})
        else:
            return JsonResponse({'status': 'error', 'message': 'No image selected'})
class UserPasswordPage(TemplateView):
    template_name = 'update-password.html'

    def post(self, request, *args, **kwargs):
        username_or_email = request.POST.get('username_or_email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            return JsonResponse({'message': 'Passwords do not match.'}, status=400)

        user = None
        if '@' in username_or_email:
            try:
                user = User.objects.get(email=username_or_email)
            except User.DoesNotExist:
                return JsonResponse({'message': 'Email does not exist.'}, status=400)
        else:
            try:
                user = User.objects.get(username=username_or_email)
            except User.DoesNotExist:
                return JsonResponse({'message': 'Username does not exist.'}, status=400)

        if user:
            user.set_password(password)
            user.save()
            password_updated.send(sender=UserPasswordPage, request=request, user=user, new_password=password)
            return JsonResponse({'message': 'Password updated successfully.'}, status=200)

        return JsonResponse({'message': 'User not found.'}, status=400)
# Home Page View
class HomePageView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        total_cars=Car.objects.all().count()
        
        total_users=User.objects.filter(role="customer").count()
        car_counts = Car.objects.values('make').annotate(total=Count('id')).count()
        top_rating = UserFeedback.objects.filter(rating__gte=4)[:6]
       
        available_cars = Car.objects.filter(status='available')
        feedbacks=UserFeedback.objects.all()
        if user.is_authenticated:
            saved_cars = user.saved_cars.all()
            car_records = [
                {
                    'id': car.id,
                    'model': car.model,
                    'make': car.make,
                    'price_per_hour': car.price_per_hour,
                    'image': car.image.url if car.image else None,
                    'is_saved': car in saved_cars
                }
                for car in available_cars
            ]
        else:
            car_records = [
                {
                    'id': car.id,
                    'model': car.model,
                    'make': car.make,
                    'price_per_hour': car.price_per_hour,
                    'image': car.image.url if car.image else None,
                    'is_saved': False
                }
                for car in available_cars
            ]
        context['top_rating']=top_rating
        context['car_counts']=car_counts
        context['total_users']=total_users
        context['feedbacks']=feedbacks
        context['car_records'] = car_records
        context['messages'] = messages.get_messages(self.request)  # Add messages to context
        context['total_cars']=total_cars
        return context

# About Page View
class AboutView(TemplateView):
    template_name = 'about.html'


# Services Page View
class ServicesView(TemplateView):
    template_name = 'services.html'


# Cars Page View
class CarsView(TemplateView):
    template_name = 'car.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Fetch all available cars
        available_cars = Car.objects.all().order_by("-id")

        # If user is authenticated, check saved cars
        if user.is_authenticated:
            saved_cars = user.saved_cars.all()
            car_records = [
                {
                    'id': car.id,
                    'model': car.model,
                    'make': car.make,
                    'price_per_hour': car.price_per_hour,
                    'image': car.image.url if car.image else None,
                    'is_saved': car in saved_cars,
                    'status':car.status
                }
                for car in available_cars
            ]
        else:
            # If user is not authenticated, no car can be saved
            car_records = [
                {
                    'id': car.id,
                    'model': car.model,
                    'make': car.make,
                    'price_per_hour': car.price_per_hour,
                    'image': car.image.url if car.image else None,
                    'is_saved': False
                }
                for car in available_cars
            ]

        context['car_records'] = car_records
        return context

# Car Blog Page View
class CarBlog(TemplateView):
    template_name = 'blog.html'


# Contact Page View
class UserContact(TemplateView):
    template_name = 'contact.html'


# Pricing Page View

class ShowPricing(TemplateView):
    template_name = 'pricing.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Fetch all available cars
        available_cars = Car.objects.all()

        # If user is authenticated, check saved cars
        if user.is_authenticated:
            saved_cars = user.saved_cars.all()
            car_records = [
                {
                    'id': car.id,
                    'model': car.model,
                    'make': car.make,
                    'price_per_hour': car.price_per_hour,
                    'price_per_day': car.price_per_day,
                    'price_per_month': car.price_per_month,
                    'discount':car.discount,
                    'image': car.image.url if car.image else None,
                    'is_saved': car in saved_cars
                }
                for car in available_cars
            ]
        else:
            # If user is not authenticated, no car can be saved
            car_records = [
                {
                    'id': car.id,
                    'model': car.model,
                    'make': car.make,
                    'price_per_hour': car.price_per_hour,
                    'image': car.image.url if car.image else None,
                    'is_saved': False
                }
                for car in available_cars
            ]

        context['car_records'] = car_records
        return context

# Single Blog Post View
class ShowBlog(TemplateView):
    template_name = 'blog-single.html'

        # Fetch all available cars
# Single Car View
class CarSingle(TemplateView):
    template_name = 'car-single.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        car_id = self.kwargs.get('id')
        car = get_object_or_404(Car, id=car_id)
        car_records=Car.objects.all()
        all_cars=Car.objects.filter(status="available")
        feedbacks = UserFeedback.objects.filter(car__car=car)
        feedbackscount = UserFeedback.objects.filter(car__car=car).count()
        
        if feedbackscount<0:
            feedbackscount=0
        
        rating_counts = feedbacks.values("rating").annotate(count=Count("rating")).order_by("-rating")

        # Prepare data for template
        ratings = {i: 0 for i in range(1, 6)}  # Initialize all ratings to 0
        total_reviews = feedbacks.count()

        for item in rating_counts:
            ratings[item["rating"]] = item["count"]

        # Calculate percentage
        rating_percentages = {i: round((ratings[i] / total_reviews) * 100) if total_reviews > 0 else 0 for i in ratings}


        # Count reviews for each rating (1 to 5)
        rating_counts = {i: feedbacks.filter(rating=i).count() for i in range(1, 6)}
        total_reviews = sum(rating_counts.values())

        # Calculate percentages
        rating_percentages = {
            i: round((count / total_reviews) * 100) if total_reviews > 0 else 0
            for i, count in rating_counts.items()
        }
        context["rating_data"] = [
                {"rating": i, "count": rating_counts[i], "percentage": rating_percentages[i]}
                for i in range(5, 0, -1)  # Iterate from 5-star to 1-star
                ]

        context['feedbackcount']=feedbackscount
        context['car_details'] = car
        context["rating_counts"] = ratings  # {1: 5, 2: 10, 3: 20, ...}
        context["rating_percentages"] = rating_percentages  # {1: 10%, 2: 20%, ...}
        context['feedbacks'] = feedbacks
        context['rating_counts'] = rating_counts  # Pass rating counts
        context['rating_percentages'] = rating_percentages  # Pass percentages
        context['reversed_range'] = reversed(range(1, 6))  # To display 5-star first
        context['car_records']=car_records
        context['all_cars']=all_cars
        return context


class Error404View(TemplateView):
    template_name = 'Error404.html'
class ErrorPageRedirect(TemplateView):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')  # Redirect to login page if not authenticated

        if request.user.role=="customer":
            return redirect('home') # Red
        if request.user.role=="employee":
            return redirect('employee_dashboard') # Red
        if request.user.role=="admin":
            return redirect('admin_index') # Red
        else:
            return redirect('home')
        

# ajax for  user booking available car display
class AvailableCarsView(View):
    def get(self, request, *args, **kwargs):
        pickup_location = request.GET.get('pickup_location')
        dropoff_location = request.GET.get('dropoff_location')
        pickup_date = request.GET.get('pickup_date')
        dropoff_date = request.GET.get('dropoff_date')
        pickup_time = request.GET.get('pickup_time')

        # Filter cars based on the provided data (adjust this as needed)
        cars = Car.objects.filter(seats__gte=4)  # Example: filter cars with at least 4 seats
        available_cars = []

        for car in cars:
            available_cars.append({
                'id': car.id,
                'model': car.model,
                'description': car.description,
                'price_per_day': car.price_per_day,
            })

        return JsonResponse({'success': True, 'cars': available_cars})
class AvailableCar(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('query', '')
        
        # Fetch cars that match the query (case-insensitive search)
        cars = Car.objects.filter(make__icontains=query)[:10]  # Limit to top 10 results
        
        car_data = [
            {
                "id": car.id,
                "model": car.model,
                "type": car.type,
                "seats": car.seats,
                "price": f"{car.price_per_hour}",
                "discount": f"{car.discount}",
                "image": car.image.url if car.image else "",  # Assuming Car has an 'image' field
            }
            for car in cars
        ]
        
        return JsonResponse({"cars": car_data})

@method_decorator(login_required, name='dispatch')
class CarBookingView(TemplateView):
    template_name = 'booking.html'  

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        carid = self.kwargs.get('id')
        car = get_object_or_404(Car, id=carid)

        existing_booking = Booking.objects.filter(user=self.request.user, car=car, booking_status="pending").first()

        if existing_booking:
            context['booking'] = existing_booking
            context['show_confirmation'] = True
        else:
            # Pre-fill car in the form
            context['form'] = BookingForm(initial={'car': car, 'user': self.request.user})
            context['show_confirmation'] = False

        context['car'] = car
        return context

    def post(self, request, *args, **kwargs):
        carid = self.kwargs.get('id')
        car = get_object_or_404(Car, id=carid)
        form = BookingForm(request.POST)

        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.car = car  # Ensure the car is set correctly
            receipt_amount = form.cleaned_data.get('receipt_amount', 0)
            booking.receipt_amount = receipt_amount
            booking.save()
            user=self.request.user
            status=booking.booking_status
            print('status: ', status)
            booking_success_notification.delay(
                user.username,
                car.model,
                booking.receipt_amount,
                booking.pickup_date.strftime("%Y-%m-%d %H:%M:%S")
            )
            messages.success(request, f"Your booking for {car.model} has been successfully submitted!")
            context = self.get_context_data(*args, **kwargs)
            context['booking'] = booking
            context['show_confirmation'] = True
            return self.render_to_response(context)

        else:
            for field, errors in form.errors.items():
                print(f"Error in {field}: {errors}")
            messages.error(request, "Some error occurred while booking the car.")

            context = self.get_context_data(*args, **kwargs)
            context['form'] = form 
            return self.render_to_response(context)

class DriverDetails(View):
    def get(self, request, *args, **kwargs):
        driver_id = request.GET.get('driver_id') 
        try:
            driver =User.objects.get(id=driver_id)  
            driver_details = {
                'name': f"{driver.first_name} {driver.last_name}",
                'image': driver.image.url if driver.image else None,
                'number': driver.phone_number,
                'gender': driver.gender,
                'email': driver.email
                # Add other details you want to display
            }
            return JsonResponse(driver_details)
        except User.DoesNotExist:
            return JsonResponse({'error': 'Driver not found'}, status=404)
class GenerateInvoiceView(View):
    def post(self, request, *args, **kwargs):
        # Get POST data from the request
        car_model = request.POST.get('car_model')
        user_name = request.POST.get('user_name')
        user_email = request.POST.get('user_email')
        driver_name = request.POST.get('driver_name')
        booking_date = request.POST.get('booking_date')
        booking_duration = request.POST.get('booking_duration')

        # Prepare the context for the invoice
        context = {
            'car_model': car_model,
            'user_name': user_name,
            'user_email': user_email,
            'driver_name': driver_name,
            'booking_date': booking_date,
            'booking_duration': booking_duration,
            'total_price': float(booking_duration) * 50  # Example price calculation (adjust as needed)
        }

        # Generate the HTML for the invoice using a Django template
        invoice_html = render_to_string('invoice_template.html', context)

        # Return the generated HTML in the JSON response
        return JsonResponse({'invoice_html': invoice_html})

    def get(self, request, *args, **kwargs):
        # If the user tries to access the view using GET, return an error response
        return JsonResponse({'error': 'Invalid request method. Use POST.'}, status=400)
def ajax_booking_create(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=True)
            return JsonResponse({'success': True, 'message': 'Booking successful!'})
        else:
            print(form.errors)  # Log errors for debugging
            return JsonResponse({'success': False, 'error_message': 'Form is invalid.', 'form_errors': form.errors})
    return JsonResponse({'success': False, 'error_message': 'Invalid request method'})
class UserBookingRecord(LoginRequiredMixin, TemplateView):
    template_name = 'user_booking_record.html' 
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        your_booking = Booking.objects.filter(user=user)
        context['bookings'] = your_booking

        available_cars = Car.objects.filter(status='available')

        if user.is_authenticated:
            saved_cars = user.saved_cars.all()  
            car_records = [
                {
                    'id': car.id,
                    'model': car.model,
                    'make': car.make,
                    'price_per_hour': car.price_per_hour,
                    'price_per_day': car.price_per_day,
                    'price_per_month': car.price_per_month,
                    'discount': car.discount,
                    'image': car.image.url if car.image else None,
                    'is_saved': car in saved_cars  # Check if the car is saved by the user
                }
                for car in available_cars
            ]
        else:
            # If the user is not authenticated, no car can be saved
            car_records = [
                {
                    'id': car.id,
                    'model': car.model,
                    'make': car.make,
                    'price_per_hour': car.price_per_hour,
                    'image': car.image.url if car.image else None,
                    'is_saved': False  # Mark all cars as unsaved
                }
                for car in available_cars
            ]

        # Add car records to context
        context['car_records'] = car_records

        return context

class CancelBookingView(View):
    def post(self, request, *args, **kwargs):
        booking_id = request.POST.get('booking_id')
        booking = get_object_or_404(Booking, id=booking_id)

        if booking.user == request.user:
            # Update booking status to "canceled"
            booking.booking_status = 'canceled'
            booking.save()
            return JsonResponse({'success': True})
        
        return JsonResponse({'success': False}, status=403)
class GetBookingDetailsView(LoginRequiredMixin,View):
    def get(self, request, booking_id):
        try:
            booking = Booking.objects.get(id=booking_id)
            car = booking.car
            user = booking.user
            driver=booking.driver
            data = {
                'car_make': car.make,
                'car_model': car.model,
                'car_year': car.year,  # Adjust as per your model
                'car_registration_number': car.number,  # Adjust as per your model
                'driver_name': driver.username, 
                'driver_email': driver.email,
                'driver_number': driver.phone_number,
                'user_name': user.first_name + " " + user.last_name,
                'user_email': user.email,
                'user_phone': user.phone_number,  # Adjust as per your model
                
                'pickup_location': f"{booking.pickup_location},{booking.city}-{booking.state},{booking.country}",

                'pickup_date': booking.pickup_date,
                'drop_date': booking.drop_date,
                'booking_status': booking.booking_status,
                'receipt_amount': booking.receipt_amount,
                'booking_status': booking.booking_status,
                'payment_status': booking.payment_status,  # Adju # Adjust field names as per your model
            }
            # Return the data as JSON response
            return JsonResponse(data)
        
        except Booking.DoesNotExist:
            # Return an error if the booking does not exist
            return JsonResponse({'error': 'Booking not found'}, status=404)
class CancelBookingView(View):
    def post(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id)

        booking.booking_status = 'canceled'
        booking.save()

        
        return JsonResponse({'success': True, 'car_model': booking.car.model})
@method_decorator(login_required, name='dispatch')
class SaveCarView(View):
    def post(self, request, *args, **kwargs):
        car_id = request.POST.get('car_id')
        if not car_id:
            return JsonResponse({'error': 'Car ID not provided'}, status=400)

        try:
            car = Car.objects.get(id=car_id)
            user = request.user
            if car in user.saved_cars.all():
                user.saved_cars.remove(car)
                action = 'removed'
            else:
                user.saved_cars.add(car)
                action = 'added'
            
            # Get the updated count of saved cars
            saved_cars_count = user.saved_cars.count()

            return JsonResponse({'success': True, 'action': action, 'saved_cars_count': saved_cars_count})

        except Car.DoesNotExist:
            return JsonResponse({'error': 'Car not found'}, status=404)
class SavedCarsView(LoginRequiredMixin, TemplateView):
    template_name = 'saved_cars.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['saved_cars'] = self.request.user.saved_cars.all()
        return context
@method_decorator(login_required, name='dispatch')
class SavedCarCountView(View):
    def get(self, request, *args, **kwargs):
        saved_cars_count = request.user.saved_cars.count()
        return JsonResponse({'count': saved_cars_count})
class UserSaveCarsRecordView(LoginRequiredMixin,TemplateView):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            # Get saved cars for the authenticated user
            saved_cars = request.user.saved_cars.all()
            car_details = [
                {
                     'id': car.id,
                    'model': car.model,
                    'make': car.make,
                    'price_per_hour': car.price_per_hour,
                    'price_per_day': car.price_per_day,
                    'price_per_month': car.price_per_month,
                    'discount':car.discount,
                    'image': car.image.url if car.image else None,
                    'is_saved': car in saved_cars,
                    'status':car.status
                }
                for car in saved_cars
            ]
            return JsonResponse({'success': True, 'saved_cars': car_details})
        else:
            return JsonResponse({'success': False, 'message': 'User not authenticated'})
        
        
@method_decorator(login_required, name="dispatch")
class UpdatePasswordView(View):
    def post(self, request, *args, **kwargs):
        user = request.user
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        # Check if the current password is correct
        if not user.check_password(current_password):
            return JsonResponse({"status": "error", "message": "Invalid current password."}, status=400)

        # Check if new passwords match
        if new_password != confirm_password:
            return JsonResponse({"status": "error", "message": "New password and confirm password do not match."}, status=400)

        # Update password
        user.set_password(new_password)
        user.save()
        update_session_auth_hash(request, user)  # Keep the user logged in

        return JsonResponse({"status": "success", "message": "Password updated successfully."})