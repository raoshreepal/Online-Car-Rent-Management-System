import os
import datetime
from io import BytesIO
from dateutil import parser  
import openpyxl
from django.http import HttpResponse

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required 
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import default_storage
from django.db.models import Q, Sum  
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, DetailView
from django.views.generic.edit import FormView

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from customer.models import User, Car, ServicesCars, Booking
from customer.forms import (
    UserRegistrationForm, 
    CarRegistrationForm, 
    ServicesCarForm, 
    BookingForm
)

    

class AdminLoginRequiredMixin(LoginRequiredMixin, TemplateView):
    login_url = '/login/' 

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(self.login_url)
        if request.user.role != 'admin':
            return redirect('404notfound')  
        return super().dispatch(request, *args, **kwargs)
# Admin Pages
class AdminIndexView(AdminLoginRequiredMixin, TemplateView):
    template_name = 'admindesk/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        avl_cars=Car.objects.filter(status='available')
        total_available_cars = Car.objects.filter(status='available').count()
        total_services_cars = ServicesCars.objects.filter(status="pending").count()
        total_user=User.objects.filter(role="customer").count()
        total_employee=User.objects.filter(role="employee").count()

        total_pending_cars = Booking.objects.filter(booking_status='confirm').count()
        total_confirm_car =Booking.objects.filter(booking_status="confirm")        
        booking_pending=Booking.objects.filter(booking_status="pending")
        total_pending_payment = Booking.objects.aggregate(
                            total_pending=Sum('receipt_amount')
        )['total_pending'] or 0
        today = timezone.now().date()

        # Calculate total amount for pending payments where drop_date = today
        total_pending_amount = Booking.objects.filter(
            drop_date=today, 
            payment_status="pending"
        ).aggregate(total_amount=Sum("receipt_amount"))["total_amount"] or 0

        payment_confirm=Booking.objects.filter(payment_status='complete')
        context['payment_confirm']=payment_confirm
        context['total_employee']=total_employee
        context['today']=today
        context["total_pending_amount"] = total_pending_amount
        context['total_available_cars'] = total_available_cars
        context['total_pending_cars'] = total_pending_cars
        context['total_services_cars'] = total_services_cars
        context['avl_cars']=avl_cars
        context['booking_pending']=booking_pending
        context['total_confirm']=total_confirm_car
        context['total_user']=total_user
        context['total_pending_payment']=total_pending_payment

        
        return context
class AdminLoginView(AdminLoginRequiredMixin,TemplateView):
    template_name = 'admindesk/adminlogin.html'

class AdminNotificationView(AdminLoginRequiredMixin):
    template_name = 'admindesk/notifications.html'

# Admin Profile Pages
@method_decorator(login_required, name='dispatch')
class  UpdateAdminImage(AdminLoginRequiredMixin,TemplateView):
    def post(self, request, *args, **kwargs):
            user = request.user
            image = request.FILES.get('image')

            if image:
                user.image = image
                user.save()
                return JsonResponse({'success': True, 'message': 'Image updated successfully'})
            else:
                return JsonResponse({'success': False, 'message': 'No image provided'})
@method_decorator(login_required, name='dispatch')
class AdminProfileView(AdminLoginRequiredMixin):
    template_name = 'admindesk/admin-profile/admin-profile.html'
@method_decorator(login_required, name='dispatch')
class UpdateAdminProfileView(AdminLoginRequiredMixin):
    def post(self, request, *args, **kwargs):
        # Get the logged-in admin user
        user = request.user

        # Update admin profile fields
        user.username = request.POST.get('username')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.phone_number = request.POST.get('phone_number')
        user.gender = request.POST.get('gender')

        # Save the updated user profile
        user.save()

        # Return success response
        return JsonResponse({'success': True, 'message': 'Profile updated successfully'})

class AddUserView(AdminLoginRequiredMixin):
    template_name = 'admindesk/user-management.html'

    def get(self, request, *args, **kwargs):
        users = User.objects.all()
        context = {
            'users': users
        }
        return render(request, self.template_name, context)
# Car Record Pages
class AddUpdateCarView(AdminLoginRequiredMixin):
    template_name = 'admindesk/car-record/add-update-car.html'
    

class AvailableCarsView(AdminLoginRequiredMixin, TemplateView):
    template_name = 'admindesk/car-management.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['car_records'] = Car.objects.all().order_by('-id')
        context['available_count'] = Car.objects.filter(status='available').count()
        context['pending_count'] = Car.objects.filter(status='pending').count()
        context['not_available_count'] = Car.objects.filter(status='not_available').count()
        context['services_count'] = Car.objects.filter(status='services').count()
        context['add_new_car'] = CarRegistrationForm()  # Empty form for GET request
        return context

    def post(self, request, *args, **kwargs):
        form = CarRegistrationForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()

            messages.success(request, "Car added successfully!")
            return redirect('car_management')  # Redirect to prevent resubmission

        else:
            print(form.errors)
        context = self.get_context_data()
        context['add_new_car'] = form  # Pass the invalid form to show errors
        return self.render_to_response(context)


# Car Services Record Pages
class AddServicesCarsView(AdminLoginRequiredMixin):
    template_name = 'admindesk/car-services-record/add-services-cars.html'

class CarServicesPaymentView(AdminLoginRequiredMixin):
    template_name = 'admindesk/car-services-record/car-services-payment.html'
class CarServicesRecordView(AdminLoginRequiredMixin, View):
    template_name = 'admindesk/car-services-management.html'

    def get(self, request, *args, **kwargs):
        form = ServicesCarForm()  # Initialize the form
        cars = Car.objects.filter(status='available')  # Fetch available cars
        employees = User.objects.filter(role='employee')  # Fetch employees
        servicescar = ServicesCars.objects.all()  # Fetch service records
        context = {
            'form': form,
            'cars': cars,
            'employees': employees,
            'service_records': servicescar
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = ServicesCarForm(request.POST)  # Initialize the form with POST data
        
        if form.is_valid():
            try:
                service_record = form.save(commit=False)  

                car = service_record.car  
                
                car.status = 'services'
                car.save()  # Save the updated car status

                # Now commit the service record to the database
                form.save()

                # Success message
                messages.success(request, 'Service record added and car status updated successfully!')
                return redirect('car_services_management')  # Redirect back to the same page

            except Exception as e:
                messages.error(request, f'Error while adding service record: {str(e)}')
                return redirect('car_services_management')  # Redirect back on error
        else:
            # If form is not valid, show error messages
            messages.error(request, 'Form submission is invalid.')
            return redirect('car_services_management')


@method_decorator(csrf_exempt, name='dispatch')
class DeleteServicesCar(View):
    def post(self, request, *args, **kwargs):
        record_id = kwargs.get('record_id')  # Get the record ID from the URL
        try:
            service_car = get_object_or_404(ServicesCars, id=record_id)
            service_car.delete()  # Delete the service car record
            return JsonResponse({'success': True})
        except ServicesCars.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Service car not found'})
# Location Pages
class GoogleMapsView(AdminLoginRequiredMixin):
    template_name = 'admindesk/location/googlemaps.html'

class JSVectorMapView(AdminLoginRequiredMixin):
    template_name = 'admindesk/location/jsvectormap.html'

# Booking Pages
class UserConfirmBookingView(AdminLoginRequiredMixin):
    template_name = 'admindesk/booking/user-confirm-booking.html'




class EmployeeManagement(AdminLoginRequiredMixin):
    template_name = 'admindesk/employee-management.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employe=User.objects.filter(role="employee")
        context["employee"] =employe
        add_employee=UserRegistrationForm()
        context['add_employee']=add_employee
        return context
    def post(self, request, *args, **kwargs):
        add_employee_form = UserRegistrationForm(request.POST)
        
        if add_employee_form.is_valid():
            # Save the new employee data
            add_employee_form.save()
            # Redirect to the same page after successfully adding the employee
            return redirect(reverse('employee-management'))  # Redirect using the view's URL name
        
        # If the form is not valid, re-render the template with form errors
        context = self.get_context_data()
        context['add_employee'] = add_employee_form  # Reassign the form with errors
        return self.render_to_response(context)
    
    

# class AdminLogoutView(AdminLoginRequiredMixin):
#     def get(self, request, *args, **kwargs):
#         logout(request)
#         return redirect('home')

# ___________ ajax _____
class GetUserDetails(AdminLoginRequiredMixin):
    def get(self, request, id, *args, **kwargs): 
        try:
            user = User.objects.get(id=id)
            bookings = Booking.objects.filter(user=user).count()
            user_payment = Booking.objects.filter(user=user).aggregate(
                            total_pending=Sum('receipt_amount')
            )['total_pending'] or 0

            response_data = {
                'name': f"{user.first_name} {user.last_name}",
                'email': user.email,
                'contact': user.phone_number,
                'gender': user.gender,
                'role': user.role,
                'bookings': bookings,
                'user_payment':user_payment
                 
            }

          

            return JsonResponse(response_data)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
class FilterUsersView(View):
    def get(self, request, *args, **kwargs):
        role = request.GET.get('role')
        gender = request.GET.get('gender')

        # Filter by role and gender
        users = User.objects.all().order_by('-date_joined')
        if role and role != 'all':
            users = users.filter(role=role)
        if gender and gender != 'all':
            users = users.filter(gender=gender)

        users_data = [{
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'phone_number': user.phone_number,
            'role': user.role,
            'gender': user.gender,
            'date_joined': user.date_joined.strftime('%B %d, %Y'),  # Format the date as "Month Day, Year"
            'image': user.image.url if user.image else None
        } for user in users]

        return JsonResponse({'users': users_data})

class UpdateUserDetails(AdminLoginRequiredMixin,View):
    def post(self, request, *args, **kwargs):
        user_id = kwargs.get('id')
        user = User.objects.get(id=user_id)

        # Now you can safely access request.POST
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.phone_number = request.POST.get('phone_number')
        user.role = request.POST.get('role')
        user.gender = request.POST.get('gender')  # Fix here to get 'gender'
        
        user.save()

        return JsonResponse({'message': 'User details updated successfully!'})
class AdminAddUser(AdminLoginRequiredMixin, FormView):
    form_class = UserRegistrationForm  # The form to be used for user registration
    template_name = 'user-management.html'  # Template where the form will be displayed

    def form_valid(self, form):
        # This method is called when the form is valid (no validation errors)
        form.save()  # Save the form data to the database
        return JsonResponse({'success': True, 'message': 'User added successfully!'})

    def form_invalid(self, form):
            errors = {}
            for field, error_list in form.errors.items():
                errors[field] = error_list[0]
            print(f"Form errors: {errors}")  # Log all form errors for debugging
            return JsonResponse({'success': False, 'message': 'Form is not valid.', 'errors': errors})

    def post(self, request, *args, **kwargs):
        # This is the method that handles POST requests
        return super().post(request, *args, **kwargs)

class UserSearchView(AdminLoginRequiredMixin):
    def get(self, request):
        search_query = request.GET.get('username', '')  # Get the search query from the request

    # Filter users by username, first name, or last name using icontains for case-insensitive search
        users = User.objects.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
         )
        user_data = [
            {
                'id':user.id,
                'username':user.username,
                'image': user.image.url if user.image else '',  # Profile image
                'name': f'{user.first_name} {user.last_name}',  # Combine first and last name
                'email': user.email,
                'contact': user.phone_number,
                'gender': user.gender,
                'role': user.role,
            'date_joined': user.date_joined.strftime('%B %d, %Y'),  # Format the date as "Month Day, Year"
            }
            for user in users
        ]

        return JsonResponse({'users': user_data})

class UserPdfRecord(AdminLoginRequiredMixin):
    def get(self, request, *args, **kwargs):
        # Retrieve all users from the database
        users = User.objects.all()

        # Create a buffer to store the PDF in memory
        buffer = BytesIO()

        # Create a canvas for the PDF generation
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # Write title or header
        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, height - 100, " Car Rent- User Records")

        # Set the font for table header and content
        p.setFont("Helvetica", 20)

        # Set starting Y position for the table and create a header row
        y_position = height - 150

        # Set background color for table header (light gray color)
        p.setFillColorRGB(0.8, 0.8, 0.8)  # Light gray color
        p.rect(10, y_position, 580, 20, fill=1)  # Draw background for the header

        # Set font for table headers
        p.setFont("Helvetica-Bold", 10)
        p.setFillColor(colors.black)

        p.drawString(5, y_position + 5, "Id")  # Added "Join Date" column

        p.drawString(15, y_position + 5, "Username")
        p.drawString(100, y_position + 5, "Full Name")
        p.drawString(200, y_position + 5, "Email")
        p.drawString(350, y_position + 5, "Phone")
        p.drawString(450, y_position + 5, "Gender")
        p.drawString(500, y_position + 5, "Role")
        p.drawString(550, y_position + 5, "Join Date")  # Added "Join Date" column


        # Draw vertical lines for the columns
        p.setStrokeColor(colors.black)
        p.setLineWidth(-1)
        p.line(10, y_position, 10, y_position - 20)  # Vertical line after Username
        p.line(95, y_position, 95, y_position - 20)  # Vertical line after Username
        p.line(200, y_position, 200, y_position - 20)  # Vertical line after Full Name
        p.line(350, y_position,350, y_position - 20)  # Vertical line after Email
        p.line(445, y_position, 445, y_position - 20)  # Vertical line after Phone
        p.line(495, y_position, 495, y_position - 20)  # Vertical line after Gender
        p.line(545, y_position, 545, y_position - 20)  # Vertical line after Role

        # Reset font for normal content text
        p.setFont("Helvetica", 10)

        # Set the Y position for the content below the header
        y_position -= 20  # Move down to below the header row

        # Loop through users and write their data
        for user in users:
            # Safely handle None values for fields
            username = user.username or 'Not available'
            full_name = f"{user.first_name or 'Not available'} {user.last_name or 'Not available'}"
            email = user.email or 'Not available'
            phone_number = user.phone_number or 'Not available'
            gender = user.gender or 'Not available'
            role = user.role or 'Not available'
            join_date = user.date_joined.strftime("%Y-%m-%d") if user.date_joined else '-'  # Format join date
            # Draw user data in the table with appropriate column spacing
            p.drawString(15, y_position, username)
            p.drawString(100, y_position, full_name)
            p.drawString(210, y_position, email)
            p.drawString(360, y_position, phone_number)
            p.drawString(450, y_position, gender)
            p.drawString(500, y_position, role)
            p.drawString(550, y_position, join_date)

            # Draw vertical lines for the columns
            p.line(1,y_position, 1,y_position-15)
            p.line(95, y_position, 95, y_position - 15)  # Vertical line after Username
            p.line(200, y_position, 200, y_position - 15)  # Vertical line after Full Name
            p.line(350, y_position, 350, y_position - 15)  # Vertical line after Email
            p.line(445, y_position, 445, y_position - 15)  # Vertical line after Phone
            p.line(495, y_position, 495, y_position - 15)  # Vertical line after Gender
            p.line(545, y_position, 545, y_position - 15)  # Vertical line after Role

            p.line(10, y_position - 2, 590, y_position - 2) 

            y_position -= 15

            if y_position < 100:
                p.showPage()
                y_position = height - 100  

        p.showPage()
        p.save()

        # Get the PDF data from the buffer
        pdf_data = buffer.getvalue()

        pdf_filename = "user_records.pdf"
        pdf_path = os.path.join(settings.MEDIA_ROOT, pdf_filename)

        with open(pdf_path, 'wb') as f:
            f.write(pdf_data)

        pdf_url = os.path.join(settings.MEDIA_URL, pdf_filename)

        return JsonResponse({'pdf_url': pdf_url})
# delete user
class DeleteUserView(AdminLoginRequiredMixin):
    def post(self, request, *args, **kwargs):
        user_id = request.POST.get('user_id')

        # Try to get the user by ID and delete
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return JsonResponse({'success': True})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User not found.'})
# ------------- car views --------------------------------
class CarDetailsView(DetailView):
    model = Car
    
    def get_object(self, queryset=None):
        car_id = self.kwargs.get('car_id')  
        try:
            return Car.objects.get(id=car_id)
        except Car.DoesNotExist:
            return None

    def get(self, request, *args, **kwargs):
        car = self.get_object()  
        if car:
            car_data = {
                'id': car.id,
                'make': car.make,
                'model': car.model,
                'year': car.year,
                'number': car.number,
                'mileage': car.mileage,
                'type': car.type,
                'status':car.status,
                'seats': car.seats,
                'discount': car.discount,
               'par_hour_rent':car.price_per_hour,
                'par_day_rent':car.price_per_day,
                'par_month_rent':car.price_per_month,

            }
            return JsonResponse(car_data)
        else:
            return JsonResponse({'error': 'Car not found'}, status=404)

class CarImageUpdate(AdminLoginRequiredMixin):
    def post(self, request, car_id):
        try:
            print(car_id)
            car = Car.objects.get(id=car_id)
            
            image = request.FILES.get('image')
            
            if image:
                car.image = image
                car.save()

                new_image_url = car.image.url
                return JsonResponse({
                    'success': True,
                    'new_image_url': new_image_url
                })
            else:
                return JsonResponse({'success': False, 'error': 'No image provided'})

        except ObjectDoesNotExist:
            return JsonResponse({'success': False, 'error': 'Car not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


class CarStatusUpdate(View):
    def post(self, request, car_id, *args, **kwargs):
        try:
            new_status = request.POST.get('new_status')
            car = Car.objects.get(id=car_id)
            car.status = new_status
            car.save()
            return JsonResponse({'success': True})
        except Car.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Car not found'})
from django.utils.dateparse import parse_datetime  # For date parsing
class ServicesCarStatusUpdate(AdminLoginRequiredMixin, View):
    def post(self, request, record_id):
        try:
            service_record = ServicesCars.objects.get(id=record_id)
            new_status = request.POST.get('new_status')
            complete_date = request.POST.get('complete_date')

            service_record.status = new_status

            if new_status == 'complete' and complete_date:
                complete_date_obj = parse_datetime(complete_date)  # Parse date
                
                if complete_date_obj is not None:
                    if complete_date_obj.tzinfo is None:
                        complete_date_obj = timezone.make_aware(complete_date_obj)
                    
                    service_record.complete_date = complete_date_obj

            service_record.save()

            return JsonResponse({
                'success': True,
                'complete_date': service_record.complete_date.strftime('%Y-%m-%d %H:%M:%S') if service_record.complete_date else None
            })

        except ServicesCars.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Record not found'})
# update car 
class UpdateCarRentPrice(View):
    def get(self, request, car_id):
        try:
            car = Car.objects.get(id=car_id)
            return JsonResponse({
                'price_per_hour': car.price_per_hour,
                'price_per_day': car.price_per_day,
                'price_per_month': car.price_per_month,
                'discount': car.discount,
                'id':car.id,
            })
        except Car.DoesNotExist:
            return JsonResponse({'error': 'Car not found'}, status=404)
    def post(self, request, car_id):
            try:
                car = Car.objects.get(id=car_id)
                # Get the updated values from the POST request
                updated_hour_rate = request.POST.get('price_per_hour')
                updated_day_rate = request.POST.get('price_per_day')
                updated_month_rate = request.POST.get('price_per_month')
                update_discount=request.POST.get('discount')

                # Ensure they are in the correct format (decimal or float)
                updated_hour_rate = float(updated_hour_rate) if updated_hour_rate else car.price_per_hour
                updated_day_rate = float(updated_day_rate) if updated_day_rate else car.price_per_day
                updated_month_rate = float(updated_month_rate) if updated_month_rate else car.price_per_month
                update_discount=float(update_discount) if update_discount else car.discount

                # Update the car's rental rates
                car.price_per_hour = updated_hour_rate
                car.price_per_day = updated_day_rate
                car.price_per_month = updated_month_rate
                car.discount=update_discount

                # Save the updated car details in the database
                car.save()
                
                return JsonResponse({'success': 'Car rent details updated successfully'})

            except Car.DoesNotExist:
                return JsonResponse({'error': 'Car not found'}, status=404)
            except ValueError:
                return JsonResponse({'error': 'Invalid input for rates'}, status=400)


class EmployeeAllDetailsView(View):
    def get(self, request, *args, **kwargs):
        emp_id = request.GET.get('id')  # Get employee ID from query parameter

        try:
            # Get employee details from the database
            employee = User.objects.get(id=emp_id)

            # Fetch related bookings and services
            booking = Booking.objects.filter(driver=employee)
            services = ServicesCars.objects.filter(employee=employee)

            # Prepare the response data
            response_data = {
                'name': employee.username,
                'email': employee.email,
                'phone': employee.phone_number,
                'booking': booking.count(),  # Total number of bookings
                'services': services.count(),  # Total number of services
                
            }

            return JsonResponse(response_data)

        except User.DoesNotExist:
            # Handle case when employee is not found
            return JsonResponse({'error': 'Employee not found'}, status=404)
class NotificationView(View):
    def get(self, request, *args, **kwargs):
        pending_bookings_count = Booking.objects.filter(booking_status='pending').count()
        pending_bookings = Booking.objects.filter(booking_status='pending').order_by('-id')
        bookings_data = []
        for booking in pending_bookings:
            bookings_data.append({
                'car_name': booking.car.model,
                'car_image': booking.car.image.url,
                'booking_at': booking.pickup_date.strftime('%Y-%m-%d'),  # Format date
                'bookking_at_time': booking.pickup_time.strftime('%H:%M:%S')  # Format time
            })
        
        # Include bookings_data in the JsonResponse
        return JsonResponse({
            'pending_bookings_count': pending_bookings_count,
            'bookings_data': bookings_data  # Add this line
        })
class DailyReportView(View):
    def get(self, request, *args, **kwargs):
        total_cars = Car.objects.count()
        available_cars = Car.objects.filter(status="available").count()
        pending_cars = Booking.objects.filter(booking_status="pending").count()
        rented_cars = Booking.objects.filter(booking_status="confirm").count()
        services_pending = ServicesCars.objects.filter(status="pending").count()

        data = {
            "total_cars": total_cars,
            "available_cars": available_cars,
            "pendings": pending_cars,
            "rented_cars": rented_cars,
            "services": services_pending,
        }
        
        return JsonResponse(data)
class EmployeeListView(View):
    def get(self, request, *args, **kwargs):
        # Filter users with role='employee'
        employees = User.objects.filter(role="employee")
        
        # You can specify the fields you want to return. For example, id and username
        employee_data = employees.values("id", "username")  # Adjust fields as needed
        
        return JsonResponse({"employees": list(employee_data)})
@method_decorator(csrf_exempt, name='dispatch')
class ConfirmBookingView(View):
    def post(self, request, *args, **kwargs):
        booking_id = request.POST.get("booking_id")
        employee_id = request.POST.get("employee_id")
    
        try:
            booking = Booking.objects.get(id=booking_id)
            employee = User.objects.get(id=employee_id)

            # Assign the booking to the employee
            booking.driver = employee
            booking.booking_status = "confirm"
            booking.save()
            car = booking.car  # Assuming the booking has a foreign key to Car
            car.status = "not_available"
            car.save()

            return JsonResponse({"message": "Booking confirmed successfully!"})
        except Booking.DoesNotExist:
            return JsonResponse({"error": "Booking not found."}, status=400)
        except User.DoesNotExist:
            return JsonResponse({"error": "Employee not found."}, status=400)

        return JsonResponse({"error": "Invalid request."}, status=400)
class CancelBookingView(View):
    def post(self, request, *args, **kwargs):
        booking_id = request.POST.get("booking_id")
        print('booking_id: ', booking_id)

        try:
            # Get the booking and update its status to "cancel"
            booking = Booking.objects.get(id=booking_id)
            booking.booking_status = "canceled"
            booking.payment_status="cancle"
            booking.save()
            return JsonResponse({"message": "Booking cancelled successfully!"})

        except Booking.DoesNotExist:
            return JsonResponse({"error": "Booking not found."}, status=400)

        return JsonResponse({"error": "Invalid request."}, status=400)
class BookingManagement(AdminLoginRequiredMixin,TemplateView):
    template_name ="admindesk/booking-management.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["all_booking"] =Booking.objects.all() 
        context['booking_form']=BookingForm()
        return context
    def post(self, request, *args, **kwargs):
        form = BookingForm(request.POST)

        if form.is_valid():
            booking = form.save(commit=False)
            booking.driver = form.cleaned_data.get('driver')  # Ensure 'driver' is captured
            booking.receipt_amount = form.cleaned_data.get('receipt_amount', 0)
            booking.booking_status = "confirm"
            
            booking.save()  # This triggers the `post_save` signal

            return redirect('booking_management')
        else:
            print("Form errors:", form.errors)
            context = self.get_context_data()
            context['booking_form'] = form
            return self.render_to_response(context)
class GetBookingDetailsView(View):
    def get(self, request, *args, **kwargs):
        car_id = request.GET.get('car_id')

        try:
            # Get the booking record based on the car_id
            booking = Booking.objects.get(id=car_id)
            user = booking.user
            driver = booking.driver  
            car = booking.car

            # Prepare the data to return in the required format
            booking_details = {
                "booking_id": booking.id,
                "user": user.username,
                "driver": driver.username if driver else "No driver assigned",  # Handle if no driver
                "car_number": car.number,
                "car_model": car.model,
                "pickup_date": booking.pickup_date.strftime('%Y-%m-%d %H:%M'),
                "drop_date": booking.drop_date.strftime('%Y-%m-%d %H:%M'),
                "booking_status": booking.booking_status,
                "payment_status":booking.payment_status
            }

            return JsonResponse({"success": True, "data": booking_details})

        except Booking.DoesNotExist:
            return JsonResponse({"success": False, "message": "Booking not found."})

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
class CarPriceView(View):
    def get(self, request, car_id):
        try:
            car = Car.objects.get(id=car_id)
            return JsonResponse({
                "price_per_hour": car.price_per_hour,
                "price_per_day": car.price_per_day,
                "price_per_month": car.price_per_month,
                "discount": car.discount,
            })
        except Car.DoesNotExist:
            return JsonResponse({"error": "Car not found"}, status=404)


class CarUpdateView(View):
    def get(self, request, *args, **kwargs):
        car_id = kwargs.get('car_id')  # Get the car ID from the URL
        try:
            car = Car.objects.get(id=car_id)
            car_data = {
                'id': car.id,  # Ensure the car ID is also included
                'number': car.number,
                'make': car.make,
                'model': car.model,
                'year': car.year,
                'mileage': car.mileage,
                'type': car.type,
                'status': car.status,
                'seats': car.seats,
                'price_per_hour': car.price_per_hour,
                'price_per_day': car.price_per_day,
                'price_per_month': car.price_per_month,
                'discount': car.discount
            }
            return JsonResponse({'car': car_data})
        except Car.DoesNotExist:
            return JsonResponse({'error': 'Car not found'}, status=404)



class UpdateCarView(View):
    def post(self, request, car_id):  
        if not car_id:
            return JsonResponse({'success': False, 'error': 'Car ID is missing.'}, status=400)

        try:
            car = Car.objects.get(id=car_id) 
        except Car.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Car not found.'}, status=404)

        car.number = request.POST.get('number')
        car.make = request.POST.get('make')
        car.model = request.POST.get('model')
        car.year = request.POST.get('year')
        car.mileage = request.POST.get('mileage')
        car.type = request.POST.get('type')
        car.seats = request.POST.get('seats')
        car.save()

        # Return success response
        return JsonResponse({'success': True, 'message': 'Car details updated successfully'})
class CalendarView(TemplateView):
    template_name = "admindesk/calendar.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)        
        return context

class EventDataView(View):
    def get(self, request, *args, **kwargs):
        # Fetch bookings
        bookings = Booking.objects.values("pickup_date", "drop_date")
        booking_events = []
        for b in bookings:
            if b["pickup_date"]:
                booking_events.append({
                    "title": "Pickup",
                    "start": str(b["pickup_date"]),
                    "backgroundColor": "#007bff",
                    "borderColor": "#007bff"
                })
            if b["drop_date"]:
                booking_events.append({
                    "title": "Drop",
                    "start": str(b["drop_date"]),
                    "backgroundColor": "#239B56",
                    "borderColor": "#239B56"
                })

        # Fetch services
        services = ServicesCars.objects.values("service_date", "complete_date")
        service_events = []
        for s in services:
            if s["service_date"]:
                service_events.append({
                    "title": "Start",
                    "start": str(s["service_date"]),
                    "backgroundColor": "#b45f06",
                    "borderColor": "#28a745"
                })
            if s["complete_date"]:
                service_events.append({
                    "title": "Complete",
                    "start": str(s["complete_date"]),
                    "backgroundColor": "#b45f06",
                    "borderColor": "#17a2b8"
                })

        return JsonResponse(booking_events + service_events, safe=False)






class GetEmployeeDetailsView(View):
    def get(self, request):
        emp_id = request.GET.get("emp_id")
        employee = get_object_or_404(User, id=emp_id)

        data = {
            "id": employee.id,
            "fname": employee.first_name,
            "lname": employee.last_name,
            "username": employee.username,
            "email": employee.email,
            "contact": employee.phone_number,
            "role": employee.role,
            "gender": employee.gender,
        }
        print("data:",data)
        return JsonResponse({"success": True, "data": data})

class UpdateEmployeeView(View):
    def post(self, request):
        emp_id = request.POST.get("emp_id")
        employee = get_object_or_404(User, id=emp_id)

        # Updating employee details
        employee.first_name = request.POST.get("fname")
        employee.last_name = request.POST.get("lname")
        employee.username = request.POST.get("username")
        employee.email = request.POST.get("email")
        employee.phone_number = request.POST.get("contact")
        employee.role = request.POST.get("role")
        employee.gender = request.POST.get("gender")

        # Handling image upload
        if "image" in request.FILES:
            if employee.image:
                default_storage.delete(employee.image.path)  # Delete old image
            employee.image = request.FILES["image"]

        employee.save()

        return JsonResponse({"success": True, "data": {"id": employee.id}})
    
    
    
from django.db.models import Count
class BookingRecordView(AdminLoginRequiredMixin, TemplateView):
    template_name = 'admindesk/report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        completed_services = ServicesCars.objects.all()
        booking_revenue = Booking.objects.aggregate(total=Sum('receipt_amount'))['total'] or 0
        
        service_revenue = ServicesCars.objects.aggregate(total=Sum('cost'))['total'] or 0
        booking=Booking.objects.all()
        booking_employees = User.objects.filter(role='employee').annotate(
        total_bookings=Count('driver_bookings', distinct=True),
        total_services=Count('service_records', distinct=True)  
        )   
        total_confirm_cost = booking.aggregate(total_amount=Sum('receipt_amount'))['total_amount'] or 0
        profit=booking_revenue - service_revenue
        total_cost = completed_services.aggregate(Sum('cost'))['cost__sum'] or 0
        context['completed_services'] = completed_services
        context['booking']=booking
        context['total_cost'] = total_cost
        context['booking_employees']=booking_employees
        context['booking_revenue']=booking_revenue
        context['service_revenue']=service_revenue
        context['total_confirm_cost']=total_confirm_cost
        context['profit']=profit
        return context
class CarMaintenance(AdminLoginRequiredMixin, TemplateView):
    template_name = "admindesk/maintenance.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Fetch all cars with their maintenance history
        cars = Car.objects.all()
        
        car_maintenance_data = []
        for car in cars:
            total_cost = ServicesCars.objects.filter(car=car).aggregate(Sum('cost'))['cost__sum'] or 0
            service_count = ServicesCars.objects.filter(car=car).count()
            
            car_maintenance_data.append({
                'car_id':car.id,
                'car': car,
                'total_cost': total_cost,
                'service_count': service_count,
            })

        context['car_maintenance_data'] = car_maintenance_data
        return context
class ExportBookingReportView(View):
    def get(self, request, *args, **kwargs):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Booking Report"

        # Define column headers
        headers = ["Booking ID", "Customer", "Driver", "Car", "Date", "Status", "Amount"]
        ws.append(headers)

        # Fetch booking data
        bookings = Booking.objects.all()

        for booking in bookings:
            ws.append([
                booking.id,
                booking.user.username if booking.user else "N/A",
                booking.driver.username if booking.driver else "N/A",  # Handle None case
                booking.car.model if booking.car else "N/A",
                booking.drop_date.strftime("%Y-%m-%d") if booking.drop_date else "N/A",
                booking.booking_status if booking.booking_status else "N/A",
                booking.receipt_amount if booking.receipt_amount else "0.00",
            ])

        # Create HTTP response with Excel content
        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = 'attachment; filename="booking_report.xlsx"'

        # Save workbook to response
        wb.save(response)
        return response
class ExportServicesReportView(View):
    def get(self, request, *args, **kwargs):
        # Create a new Excel workbook and sheet
        print("enter")
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Services Report"

        # Define headers
        headers = ["Service ID", "Car", "Category","Description", "Price", "Status", "Created At" ,"Complete services"]
        ws.append(headers)

        # Fetch all services from the database
        services = ServicesCars.objects.all()

        # Add service data to the worksheet
        for service in services:
            ws.append([
                service.id,
                service.car.number,
                service.service_type if service.service_type else "N/A",  # Handle missing category
                service.description,
                service.cost if service.cost else "0.00",
                service.status if service.status else "N/A",
                service.service_date.strftime("%Y-%m-%d") if service.service_date else "N/A",
                service.complete_date.strftime("%Y-%m-%d") if service.complete_date else "N/A",

            ])

        # Create an HTTP response with Excel content
        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = 'attachment; filename="services_report.xlsx"'

        # Save the workbook to the response
        wb.save(response)
        return response
class GetServicesView(View):
    def get(self, request, car_id, *args, **kwargs):
        # Fetch all services for the given car ID
        services = ServicesCars.objects.filter(car_id=car_id).select_related("employee")

        # Convert queryset to list of dictionaries
        service_data = [
            {
                "id": service.id,
                "name": service.service_type,
                "employee": service.employee.username,  # Fetch employee name
                "service_date": service.service_date.strftime("%Y-%m-%d"),
                "complete_date": service.complete_date.strftime("%Y-%m-%d") if service.complete_date else "N/A",
                "cost": float(service.cost),
                "description": service.description,
                "status": service.status,
            }
            for service in services
        ]

        return JsonResponse({"services": service_data})