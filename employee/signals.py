from django.db.models.signals import post_save
from django.dispatch import receiver
from employee.tasks import booking_confirmed_notification

from customer.models import ServicesCars ,Car ,Booking  # Import your service model
@receiver(post_save, sender=ServicesCars)
def update_car_status(sender, instance, created, **kwargs):
    """Set car status to 'services' when a new service record is added."""
    if created and instance.car:  # Ensure a car instance exists
        instance.car.status = "services"
        instance.car.save()
        print(f"Car {instance.car.id} status updated to 'services'")

@receiver(post_save, sender=Booking)
def update_car_status_on_booking(sender, instance, **kwargs):
    if instance.booking_status == "confirm" and instance.car:
        print(f"Booking {instance.id} confirmed. Updating car {instance.car.id} status...")
        instance.car.status = "not_available"
        instance.car.save()
        print(f"Car {instance.car.id} status updated to 'not available'")

        # ✅ Extract User, Car, and Driver Details
        username = instance.user.username
        car_model = instance.car.model
        car_number = instance.car.number
        driver_name = instance.driver.username if instance.driver else "Not Assigned"
        driver_contact = instance.driver.phone_number if instance.driver else "Not Available"
        pickup_date = instance.pickup_date.strftime("%Y-%m-%d")

        print("=== Debugging Celery Task for Booking Confirmation ===")
        print(f"👤 Username: {username}")
        print(f"🚗 Car Model: {car_model}")
        print(f"🚗 Car Number: {car_number}")
        print(f"🧑‍✈️ Driver Name: {driver_name}")
        print(f"📞 Driver Contact: {driver_contact}")
        print(f"🕒 Pickup Date: {pickup_date}")
        print("=======================================")

        # ✅ Call Celery Task for User Notification
        booking_confirmed_notification.apply_async(
            args=[username, car_model, car_number, driver_name, driver_contact, pickup_date]
        )
