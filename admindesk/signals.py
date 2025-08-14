from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from customer.models import ServicesCars, Car  # Import your models
from django.db.models.signals import post_delete

@receiver(post_save, sender=ServicesCars)
def update_car_status(sender, instance, **kwargs):
    """
    When a service record is marked as 'complete', set the car's status to 'available'.
    """
    if instance.status == "complete":
        car = instance.car  # Assuming 'car' is a ForeignKey in ServicesCars model
        if car:
            car.status = "available"
            car.save()
            print(f"Car {car.id} status updated to available on {now()}.")
@receiver(post_delete, sender=ServicesCars)
def update_car_status_on_delete(sender, instance, **kwargs):
    """
    When a service record is deleted, update the car's status to 'available'.
    """
    if instance.car:  # Ensure the car exists
        instance.car.status = "available"
        instance.car.save()