# customer/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from decimal import Decimal
from django_countries.fields import CountryField
from datetime import datetime

from django.utils import timezone
class TimestampedModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now, editable=False)  # Set default instead of auto_now_add
    updated_at = models.DateTimeField(auto_now=True)  # Keeps auto_now for updates

    class Meta:
        abstract = True  
 
class Car(TimestampedModel):
    CAR_TYPES = [
        ('EV', 'Electric Vehicle'),
        ('CNG', 'Compressed Natural Gas'),
        ('Petrol', 'Petrol'),
        ('Diesel', 'Diesel'),
    ]

    STATUS_CHOICES = [
        ('available', 'Available'),
        ('pending', 'Pending'),
        ('not_available', 'Not Available'),
        ('services','Services')
    ]

    model = models.CharField(max_length=255)
    make = models.CharField(max_length=255)
    year = models.PositiveIntegerField()
    number = models.CharField(max_length=255, unique=True)
    image = models.ImageField(upload_to='image/')
    type = models.CharField(max_length=10, choices=CAR_TYPES)
    seats = models.PositiveIntegerField(default=4)  # Default to 4 seats
    mileage = models.FloatField()  # Mileage in km/l or miles/gallon
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='available')
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2, default=10.99)  # Price per hour
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2, default=60.99)   # Price per day
    price_per_month = models.DecimalField(max_digits=10, decimal_places=2, default=995.99)  # Price per month
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  # New discount column
   


    def __str__(self):
        return f"{self.id}{self.make} {self.model} ({self.year}){self.status}"


class User(AbstractUser,TimestampedModel):

    phone_number = models.CharField(max_length=15, blank=True, null=True)
    image = models.ImageField(upload_to='media/', blank=True, null=True)
    saved_cars = models.ManyToManyField(Car, related_name='saved_by', blank=True)

    role = models.CharField(
        max_length=50,
        choices=[('admin', 'Admin'), ('employee', 'Employee'), ('customer', 'Customer')],
        default='admin'
    )
    gender = models.CharField(
        max_length=10,
        choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
        default='male',
        blank=True,
        null=True
    )
    

    def __str__(self):
        return f"{self.username}"



class ServicesCars(TimestampedModel):
    SERVICE_STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('pending', 'Pending'),
    ]

    car = models.ForeignKey(Car, on_delete=models.CASCADE, limit_choices_to={'status': 'available'},related_name='services')
    employee = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'employee'}, related_name='service_records')
    service_type = models.CharField(max_length=255)
    service_date = models.DateTimeField()
    complete_date = models.DateTimeField(null=True, blank=True)  # New field added
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    description = models.TextField()
    status = models.CharField(max_length=10, choices=SERVICE_STATUS_CHOICES, default='pending')


    def __str__(self):
        return f"Service Record for Car ID {self.car.id} - {self.service_type}"

class Booking(TimestampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="bookings")
    country = CountryField(default="unknown")
    state = models.CharField(max_length=200, default="unknown")
    city = models.CharField(max_length=200, default="unknown")
    pickup_location = models.CharField(max_length=50, default="Unknown")
    pickup_date = models.DateField()
    pickup_time = models.TimeField()   
    drop_date = models.DateField()
    drop_time = models.TimeField()
    pickup_latitude = models.FloatField(null=True, blank=True)  # Add this
    pickup_longitude = models.FloatField(null=True, blank=True)  # Add this
    
    # Automatically store the logged-in user for driver and customer in the same model
    driver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="driver_bookings")
    payment_status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('complete', 'Complete'),('cancle','Cancle')], default="pending")
    receipt_amount = models.DecimalField(max_digits=100, decimal_places=2, default=00.00)
    BOOKING_STATUS_CHOICES = [
        ("pending", 'Pending'),
        ("complete", 'Complete'),
        ("canceled", 'Canceled'),
        ("confirm", 'Confirm'),
    ]
    booking_status = models.CharField(
            max_length=20,
            choices=BOOKING_STATUS_CHOICES,
            default="pending"  # Default status is "pending"
        )
    

    def __str__(self):
        return f"Booking by {self.user.username} for {self.car.model} on {self.pickup_date}"

   

class UserFeedback(TimestampedModel):
    car = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='feedbacks')
    rating = models.PositiveIntegerField(choices=[(i, str(i)) for i in range(1, 6)], default=5)  # Rating (1-5)
    comments = models.TextField(blank=True, null=True)  
    replay=models.TextField(blank=True,null=True)
    def __str__(self):
        return f"Feedback by {self.car.id} on {self.rating}"