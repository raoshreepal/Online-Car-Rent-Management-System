from django.contrib.auth import logout
from django.shortcuts import redirect ,render
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.views.generic import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
from django.views.generic.edit import UpdateView
from django.http import HttpResponseForbidden
from customer.models import Car , Booking ,ServicesCars ,User ,UserFeedback
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime ,date
from django.db.models import Q

from customer.forms import UserRegistrationForm ,BookingForm ,CarRegistrationForm ,ServicesCarForm
# Employee Pages
class LoginRequiredTemplateView(LoginRequiredMixin, TemplateView):
    login_url = '/login/'  # Redirect URL for unauthenticated users
    def dispatch(self, request, *args, **kwargs):
        # Check if user is authenticated and has the 'employee' role
      if not request.user.is_authenticated:
                      return redirect('login')

        
      if request.user.role != 'employee':
            return redirect("404notfound")
      return super().dispatch(request, *args, **kwargs)
    

class EmployeeIndexView(LoginRequiredTemplateView):
    template_name = 'employee/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee=self.request.user
        total_car=Car.objects.filter(status="available").count()
        car_not_available=Car.objects.filter(status='not_available').count()
        car_services=Car.objects.filter(status='services').count()
        
        employee_booking = Booking.objects.filter(
            driver=employee,
            booking_status="confirm"
            )
        current_datetime = timezone.now()
        matching_bookings = employee_booking.filter(drop_date=current_datetime.date())

        employee_total_booking_receipt_today_ammount = 0
        for booking in matching_bookings:
            dropoff_datetime = datetime.combine(booking.drop_date, booking.drop_time)
            
            dropoff_datetime = timezone.make_aware(dropoff_datetime, timezone.get_current_timezone())

            if dropoff_datetime <= current_datetime:
                employee_total_booking_receipt_today_ammount += booking.receipt_amount

        if not matching_bookings.exists():
            employee_total_booking_receipt_today_ammount = 0

        total_users=Booking.objects.filter(driver=employee).count()
        employee_total_booking_receipt = sum(booking.receipt_amount for booking in employee_booking)
        car_available=Car.objects.filter(status='available')
        booking_pending=Booking.objects.filter(booking_status="pending")
        context['total_users']=total_users
        context['total_car'] = total_car
        context['car_not_available']=car_not_available
        context['car_services']=car_services
        context['employee_total_booking_receipt']=employee_total_booking_receipt
        context['employee_total_booking_receipt_today_ammount']=employee_total_booking_receipt_today_ammount
        context['car_available']=car_available
        context['booking_pending']=booking_pending
        context['current_datetime']=current_datetime
        return context  

class EmployeeNotificationView(LoginRequiredTemplateView):
    template_name = 'employee/notifications.html'

# Employee Profile Pages
class EmployeeProfileView(LoginRequiredTemplateView):
    template_name = 'employee/employee-profile/employee-profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_profile'] = self.request.user
        return context  

class MyBalanceView(LoginRequiredTemplateView):
    template_name = 'employee/employee-profile/mybalence.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
       
        employee=self.request.user
        services=ServicesCars.objects.filter(
        employee=employee,    
        )
        employee_booking = Booking.objects.filter(
            driver=employee,
            booking_status="confirm"
            )
        employee_total_booking_receipt = sum(booking.receipt_amount for booking in employee_booking)
        context['employee_total_booking_receipt']=employee_total_booking_receipt
        context['services']=services
        return context

@method_decorator(login_required, name='dispatch')
class UpdateEmployeeProfileView(View):
    def post(self, request, *args, **kwargs):
        # Get the logged-in user
        user = request.user

        # Update user profile fields
        user.username = request.POST.get('username')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.phone_number = request.POST.get('phone_number')
        user.gender = request.POST.get('gender')

        # Save the updated user
        user.save()

        # Return success response
        return JsonResponse({'message': 'Profile updated successfully'})



User = get_user_model()
class EmployeeImageUpdateView(UpdateView):
    model = User
    fields = ['image']  # Only update the image field
    template_name = 'employee/employee-profile/update-employee-profile.html'

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        user = form.save()
        # Return the updated image URL in the response
        data = {
            'message': 'Profile image updated successfully!',
            'updated_image_url': user.image.url if user.image else None  # Assuming 'image' is the field name
        }
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context
    
from django.db.models import Count
class AddUserView(LoginRequiredMixin, TemplateView):
    template_name = 'employee/employee-profile/add-user-car-booking.html'

    def get_context_data(self, **kwargs):
        # Get the context data from the superclass
        context = super().get_context_data(**kwargs)
        # Get the current user
        current_driver = self.request.user  

        # Get the number of bookings for each user
        user_booking_counts = (
            Booking.objects.filter(driver=current_driver)
            .values('user__username', 'user__email')
            .annotate(total_bookings=Count('car', distinct=True))
        )

       
        # Add the booking form and user booking counts to the context
        context['booking_form'] = BookingForm()
        context['user_booking_counts'] = user_booking_counts
        # Return the context
        return context

    def post(self, request, *args, **kwargs):
        current_driver = request.user  
        form = BookingForm(request.POST)

        if form.is_valid():
            booking = form.save(commit=False)
            booking.driver = current_driver 
            
           
            booking.receipt_amount = form.cleaned_data.get('receipt_amount', 0)
            booking.booking_status = "confirm"
            booking.save()
            
            return redirect('add_user')  
        else:
            print("Form errors:", form.errors)
            context = self.get_context_data()
            context['booking_form'] = form
            return self.render_to_response(context)


# add new car  
class AddUpdateCarView(LoginRequiredMixin, TemplateView):
    template_name = 'employee/car-record/add-update-car.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        available=Car.objects.filter(status="available")
        context['available']=available
        context['car_form'] = CarRegistrationForm()
        
        return context

    def post(self, request, *args, **kwargs):
        form = CarRegistrationForm(request.POST, request.FILES)  
        
        if form.is_valid():
            form.save()
            return redirect('available_cars')  
        else:
            print(form.errors)


        context = self.get_context_data()
        context['car_form'] = form
        return self.render_to_response(context)



class AvailableCarsView(LoginRequiredTemplateView):
    template_name = 'employee/car-record/available-cars.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['car_record'] = Car.objects.all().order_by("-id")
        return context
class EmployeeCarStatusView(LoginRequiredTemplateView):
    template_name = 'employee/car-record/car-status.html'
    def get_context_data(self, **kwargs):
        employee=self.request.user
        context= super().get_context_data(**kwargs)
        confirm_booking=Booking.objects.filter(driver=employee,booking_status='complete',payment_status="complete")
        total_car=Booking.objects.filter(driver=employee).count()
        peding_car=Booking.objects.filter(driver=employee,booking_status='confirm').count()
        cancle_car=Booking.objects.filter(booking_status='canceled').count()
        services=ServicesCars.objects.filter(employee=employee,status="pending").count()
        confirm=Booking.objects.filter(driver=employee,booking_status="confirm")

        context['complete_booking']=confirm_booking
        context['total_car']=total_car
        context['peding_car']=peding_car
        context['cancle_car']=cancle_car
        context['services']=services
        context['confirm']=confirm
        return context
    

# Car Services services form Pages
class AddServicesCarsView(TemplateView):
    template_name = 'employee/car-services-record/add-services-cars.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ServicesCarForm()
        return context

    def post(self, request, *args, **kwargs):
        form = ServicesCarForm(request.POST)
        if form.is_valid():
            form.save()  # Save the service record
            messages.success(request, "Service record added successfully!")
            return redirect('carServicesRrecord')  # Prevents resubmission on refresh
        
        else:
            print("Form Errors:", form.errors)  # Debugging purpose
            messages.error(request, "There was an error submitting the form. Please check your inputs.")

        return render(request, self.template_name, {'form': form})  # Keep the form with errors
class CarServicesPaymentView(LoginRequiredTemplateView):
    template_name = 'employee/car-services-record/car-services-payment.html'
    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        pending_payment = ServicesCars.objects.filter(status="pending").aggregate(total_pending=Sum('cost'))['total_pending'] or 0
        total_services_payment = ServicesCars.objects.aggregate(total_payment=Sum('cost'))['total_payment'] or 0
        all_services_car_record = ServicesCars.objects.all().order_by('-id')
        context['pending_payment']=pending_payment
        context['total_services_payment']=total_services_payment
        context['all_cars']=all_services_car_record
        return context

class CarServicesRecordView(LoginRequiredTemplateView):
    template_name = 'employee/car-services-record/car-services-record.html'
    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        services_car=ServicesCars.objects.all().order_by('-id')
        context['services_car']=services_car
        return context
class ConfirmServicesView(LoginRequiredTemplateView):
    template_name = 'employee/car-services-record/confirm-services.html'
    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        completed_services=ServicesCars.objects.filter(status="completed")
        completed_services_count=ServicesCars.objects.filter(status="completed").count()
        payment = ServicesCars.objects.filter(status="completed").aggregate(total_pending=Sum('cost'))['total_pending'] or 0
        context['payment']=payment
        context['count']=completed_services_count

        context['completed']=completed_services
        return context
# Location Pages
class GoogleMapsView(LoginRequiredTemplateView):
    template_name = 'employee/location/googlemaps.html'

class JSVectorMapView(LoginRequiredTemplateView):
    template_name = 'employee/location/jsvectormap.html'

# Booking Pages

class BookingRecordView(LoginRequiredTemplateView):
    template_name = 'employee/booking/booking-record.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        driver_name=self.request.user.id
        
        employee_booking = Booking.objects.filter(
            driver=driver_name,
            booking_status="confirm"
            )
        employee_total_booking_receipt = sum(booking.receipt_amount for booking in employee_booking)


        pending_bookings = Booking.objects.filter(booking_status='pending').order_by('-id')
        pending_bookings_count = Booking.objects.filter(booking_status='pending').count()
        context['pending_bookings'] = pending_bookings
        context['pending_bookings_count'] = pending_bookings_count
        context['employee_booking']=employee_booking
        context['employee_total_booking_receipt']=employee_total_booking_receipt

        return context
# class EmployeeLogoutView(LoginRequiredTemplateView):
#     template_name = 'employee/logout.html'

#     def get(self, request, *args, **kwargs):
#         logout(request)
#         return redirect('home')
class NotificationView(View):

    def get(self, request, *args, **kwargs):
        # Query for pending bookings
        pending_bookings_count = Booking.objects.filter(booking_status='pending').count()
        pending_bookings = Booking.objects.filter(booking_status='pending').order_by('-id')

        # Prepare the response data
        bookings_data = []
        for booking in pending_bookings:
            bookings_data.append({
                'car_name': booking.car.model,
                'car_image': booking.car.image.url,
                'booking_at': booking.pickup_date.strftime('%Y-%m-%d'),  # Optional: Format datetime
                'bookking_at_time':booking.pickup_time.strftime('%H:%M:%S')

            })
        
        # Return the data as JSON
        return JsonResponse({
            'pending_bookings_count': pending_bookings_count,
            'bookings_data': bookings_data
        })
class ConfirmBookingView(View):
    def post(self, request):
        booking_id = request.POST.get('booking_id')
        car_id = request.POST.get('car_id')

        # Get the booking and car objects
        booking = get_object_or_404(Booking, id=booking_id)
        car = get_object_or_404(Car, id=car_id)

        # Ensure the booking is in 'pending' status
        if booking.booking_status == 'pending':
            # Update the booking status to 'confirmed'
            booking.booking_status = 'confirm'
            booking.driver = request.user  # Assign the current logged-in user as the driver
            booking.save()

            # Update the car status to 'not_available'
            car.status = 'not_available'
            car.save()

            return JsonResponse({'status': 'success'})

        return JsonResponse({'status': 'error'}, status=400)
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from django.conf import settings
import os

class EmployeeBookingPdfView(View):
    def get(self, request, *args, **kwargs):
        # Get the employee's booking data
        employee = request.user
        employee_bookings = Booking.objects.filter(driver=employee, booking_status="confirm")

        
        # Calculate total amount
        total_amount = sum(booking.receipt_amount for booking in employee_bookings)

        # Create a response with PDF content type
        buffer = BytesIO()
        
        # Create a canvas
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # Get the current date and time
        current_datetime = datetime.now().strftime('%B %d, %Y %I:%M %p')  # Format: Month Day, Year Hour:Minute AM/PM
        
        # Add a title to the PDF with current date and time
        c.setFont("Helvetica", 16)
        c.drawString(100, height - 50, f"Employee: {employee.username} - Booking Report")
        c.setFont("Helvetica", 10)
        c.drawString(100, height - 70, f"Report Generated On: {current_datetime}")

        # Adjust starting position for headers
        y_position = height - 100  # Start at this position
        
        # Set up the table headers at y_position
        c.setFont("Helvetica", 10)
        c.drawString(100, y_position, "Car Model, Number, Type, Seats")
        c.drawString(300, y_position, "Pickup date")
        c.drawString(400, y_position, "Drop Date")
        c.drawString(500, y_position, "Pickup Location")
        c.drawString(600, y_position, "Booking Status")
        c.drawString(700, y_position, "Amount")
        c.drawString(800, y_position, "User Username & Email")
        
        # Draw a line under the headers
        y_position -= 10
        c.line(95, y_position, 850, y_position)  # Draw the line between the headers and rows
        
        # Add the rows of the table
        for booking in employee_bookings:
            y_position -= 20
            # Car details in the same column (adjusted to fit them all together)
            car_details = f"{booking.car.model} - {booking.car.number} - {booking.car.type} - {booking.car.seats} seats"
            c.drawString(100, y_position, car_details)

            c.drawString(300, y_position, str(booking.pickup_date))
            c.drawString(400, y_position, str(booking.drop_date))
            c.drawString(500, y_position, booking.pickup_location)
            c.drawString(600, y_position, booking.booking_status)
            c.drawString(700, y_position, f"${booking.receipt_amount}")

            # Display the username and email in a new column
            user_details = f"{booking.user.username} - {booking.user.email}"
            c.drawString(800, y_position, user_details)
            
            # Check if we need to add another page
            if y_position < 100:
                c.showPage()
                y_position = height - 100
                c.setFont("Helvetica", 10)
                c.drawString(100, y_position, "Car Model, Number, Type, Seats")
                c.drawString(300, y_position, "Pickup Date")
                c.drawString(400, y_position, "Drop Date")
                c.drawString(500, y_position, "Pickup Location")
                c.drawString(600, y_position, "Booking Status")
                c.drawString(700, y_position, "Amount")
                c.drawString(800, y_position, "User Username & Email")
                y_position -= 10
                c.line(95, y_position, 850, y_position)  # Draw the line again for new page
        
        # Add the total amount field
        y_position -= 20
        c.setFont("Helvetica-Bold", 12)
        c.drawString(500, y_position, "Total Amount:")
        c.drawString(600, y_position, f"${total_amount}")
        
        # Draw a line under the total field
        y_position -= 10
        c.line(95, y_position, 850, y_position)

        # Save the PDF
        c.showPage()
        c.save()

        # Prepare the file content to be sent back to the client
        pdf_content = buffer.getvalue()
        buffer.close()

        # Save the PDF to a temporary file
        file_path = os.path.join(settings.MEDIA_ROOT, 'pdfs', f'{employee.username}_booking_report.pdf')
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'wb') as f:
            f.write(pdf_content)

        # Send the URL of the generated PDF back to the frontend
        pdf_url = f'{settings.MEDIA_URL}pdfs/{os.path.basename(file_path)}'
        return JsonResponse({'pdf_url': pdf_url})

class CarStatisticsView(View):
    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            available_cars = Car.objects.filter(status="available").count()
            rented_cars = Booking.objects.filter(driver=self.request.user, booking_status="confirm").count()
            rented_cars_pending = Booking.objects.filter(booking_status="pending").count()
            total_cars=Car.objects.all().count()

            services = ServicesCars.objects.filter(employee=self.request.user,status='pending').count()
        else:
            available_cars = Car.objects.filter(status="available").count()
            rented_cars_pending=0
            rented_cars = 0 # No rented cars for unauthenticated users
            services = 0 # No services for unauthenticated users
            total_cars=0
        data = {
            "available_cars": available_cars,
            "rented_cars": rented_cars,
            "services": services,
            "pendings": rented_cars_pending,
            'total_cars': total_cars,
        }
        return JsonResponse(data)
@method_decorator(login_required, name="dispatch")
class ConfirmBookingsView(View):
    def post(self, request, *args, **kwargs):
        booking_ids = request.POST.getlist("booking_ids[]")

        if not booking_ids:
            return JsonResponse({"success": False, "error": "No bookings selected"})

        employee = request.user  

        # Update selected bookings and trigger signal
        bookings = Booking.objects.filter(id__in=booking_ids)
        for booking in bookings:
            booking.booking_status = "confirm"
            booking.driver = employee
            booking.save()  # Triggers the post_save signal

        return JsonResponse({"success": True})
class PickupLocationView(View):
    def get(self, request, *args, **kwargs):
        employee=self.request.user
        pickup_locations = Booking.objects.filter(driver=employee).values('pickup_date').distinct()
        print("----------------------------------------")
        print(pickup_locations)
        dates = [location['pickup_date'] for location in pickup_locations]
        print(dates)
        print("-----------------")
        return JsonResponse({'dates': dates})

class UserBookingsView(View):
    def get(self, request):
        username = request.GET.get("username")  # Get username from AJAX request

        # Fetch bookings and manually serialize each Booking object
        bookings = Booking.objects.filter(user__username=username)
        booking_list = [
            {
                "car_name": booking.car.model,  
                "car_number":booking.car.number,
                "pickup_date": booking.pickup_date.strftime("%Y-%m-%d"),
                "pickup_location":booking.pickup_location,
                "drop_date": booking.drop_date.strftime("%Y-%m-%d"),
                "receipt_amount": booking.receipt_amount
            }
            for booking in bookings
        ]

        return JsonResponse({"bookings": booking_list}, safe=False)
class CarDetailsView(View):
    def get(self, request, *args, **kwargs):
        car_id = request.GET.get('car_id')  # Get the car ID from the request
        try:
            car = Car.objects.get(id=car_id)
            data = {
                'rate_per_hour': str(car.price_per_hour),
                'rate_per_day': str(car.price_per_day),
                'rate_per_month': str(car.price_per_month),
                'discount': str(car.discount),
            }
            return JsonResponse(data)
        except Car.DoesNotExist:
            return JsonResponse({'error': 'Car not found'}, status=404)
class UpdateCarImageView(View):
    def post(self, request, *args, **kwargs):
        # Get car ID from the request
        car_id = request.POST.get('car_id')
        
        try:
            # Fetch the car object using the provided ID
            car = Car.objects.get(id=car_id)
            
            # Check if the image is part of the request
            if request.FILES.get('image'):
                # Save the new image
                new_image = request.FILES['image']
                car.image = new_image
                car.save()
                
                # Return the new image URL as a response
                return JsonResponse({'success': True, 'new_image_url': car.image.url})
            else:
                return JsonResponse({'success': False, 'error': 'No image provided'})
        
        except Car.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Car not found'})
class DisplayCalendarView(TemplateView):
    template_name = 'employee/calendar.html'
class EmployeeEventDataView(View):
    def get(self, request, *args, **kwargs):
        current_employee = self.request.user

        # Fetch bookings
        bookings = Booking.objects.filter(driver=current_employee).values("pickup_date", "drop_date")
        booking_events = []
        for b in bookings:
            if b["pickup_date"]:
                booking_events.append({"title": "Booking", "start": str(b["pickup_date"]), "color": "#007bff"})
            if b["drop_date"]:
                booking_events.append({"title": "Drop", "start": str(b["drop_date"]), "color": "#239B56"})

        # Fetch services
        services = ServicesCars.objects.filter(employee=current_employee).values("service_date", "complete_date")
        service_events = []
        for s in services:
            if s["service_date"]:
                service_events.append({"title": "Service Start", "start": str(s["service_date"]), "color": "#28a745"})
            if s["complete_date"]:
                service_events.append({"title": "Service Complete", "start": str(s["complete_date"]), "color": "#17a2b8"})

        # If no services exist, add a default placeholder event
        if not service_events:
            service_events.append({
                "title": "No Services Scheduled",
                "start": str(date.today()),  # Corrected: date.today() instead of datetime.date.today()
                "color": "#d3d3d3"  # Grey color
            })

        return JsonResponse(booking_events + service_events, safe=False)



class UserFeedbackView(View):
    def get(self, request, *args, **kwargs):
        current_driver = self.request.user

        # Get bookings related to the current driver
        bookings = Booking.objects.filter(driver=current_driver)

        # Fetch feedback related to these bookings
        feedbacks = UserFeedback.objects.filter(car__in=bookings).order_by('-created_at')[:5]        

        feedback_list = []
        for feedback in feedbacks:
            feedback_list.append({
                "image": feedback.car.user.image.url,
                "name": feedback.car.driver.username,
                "created_at": feedback.created_at.strftime("%Y-%m-%d %H:%M"),
                "description": (feedback.comments[:20] + "...") if len(feedback.comments) > 6 else feedback.comments
            })

        return JsonResponse({"feedbacks": feedback_list}, safe=False)
class MyUserFeedback(LoginRequiredTemplateView,TemplateView):
    template_name ="employee/myfeedback.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_driver = self.request.user

        # Get bookings related to the current driver
        bookings = Booking.objects.filter(driver=current_driver)

        # Fetch feedback related to these bookings
        feedbacks = UserFeedback.objects.filter(car__in=bookings).order_by('-id')
        context["myfeedback"] = feedbacks
        return context
class ReplyFeedbackView(View):
    def post(self, request, *args, **kwargs):
        feedback_id = request.POST.get("feedback_id")
        reply_text = request.POST.get("reply")

        try:
            feedback = UserFeedback.objects.get(id=feedback_id)
            feedback.replay = reply_text  # Update reply field
            feedback.save()

            return JsonResponse({"status": "success"})
        except UserFeedback.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Feedback not found"}, status=404)