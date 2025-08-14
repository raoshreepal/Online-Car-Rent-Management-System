from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from django.contrib import messages
from django.db.models.signals import pre_save
from .models import Booking
from django.dispatch import Signal, receiver
from .tasks import display_registered_user_info  ,login_user ,logout_user ,password_update_notification

User = get_user_model()

@receiver(post_save, sender=User)
def register_user(sender, instance, created, **kwargs):
    if created:  # Ensure the signal runs only when a new user is created
        print("User registered successfully..")
        print(f"User: {instance.username}")  # Print username for debugging
        print("----------------------------------------------------------------------")
        display_registered_user_info.apply_async((instance.username,instance.first_name,instance.last_name,instance.email,instance.phone_number,instance.role),countdown=10)
@receiver(user_logged_in)
def user_login_success(sender, request, user, **kwargs):
    messages.success(request, "You are logged in successfully.")  #
@receiver(post_save, sender=Booking)
def process_booking(sender, instance, created, **kwargs):
    if created:
        # ✅ Update car status
        instance.car.status = 'pending'
        instance.car.save()

        # ✅ Extract and Log Arguments
        username = instance.user.username
        car_model = instance.car.model
        number = instance.car.number
        receipt_amount = instance.receipt_amount
        pickup_date = instance.pickup_date.strftime("%Y-%m-%d %H:%M:%S")  # Convert to string

        print("=== Debugging Celery Task Arguments ===")
        print(f"Username: {username}")
        print(f"Car Model: {car_model}")
        print(f"Car Number: {number}")
        print(f"Receipt Amount: {receipt_amount}")
        print(f"Booking Time: {pickup_date}")  # Now it's a string
        print("=======================================")

        booking_success_notification.apply_async(
                 args=[username, car_model, number, receipt_amount, pickup_date]
        )


@receiver(pre_save, sender=Booking)
def update_car_status_on_cancellation(sender, instance, **kwargs):
    # Check if the booking status is being updated to 'canceled'
    if instance.booking_status == 'canceled' and instance.pk:
        print("---------------------available car after cancle the bokoing from user side -----")
        previous_booking = Booking.objects.get(pk=instance.pk)
        if previous_booking.booking_status != 'canceled':
            # When booking is canceled, update car status to available
            car = instance.car
            car.status = 'available'
            car.save()
password_updated = Signal()  # Define the signal only once

@receiver(password_updated)
def handle_password_updated(sender, request, user, new_password, **kwargs):
    print("-------------------- Password Updated ----------------------------------------")
    print(f"✅ Password successfully updated for user: {user.username}")

    # ✅ Call Celery Task
    password_update_notification.apply_async(args=[user.username, new_password])
