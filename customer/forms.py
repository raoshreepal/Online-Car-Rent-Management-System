from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from .models import User ,Car  ,ServicesCars ,Booking  ,UserFeedback
from django_countries.fields import CountryField 
User = get_user_model()

class UserRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'password1', 'placeholder': 'Enter Password'}),
        min_length=8,
        required=True
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'password2', 'placeholder': 'Confirm Password'}),
        min_length=8,
        required=True
    )
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'first_name', 'placeholder': 'Enter First Name'}),
        required=True
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'last_name', 'placeholder': 'Enter Last Name'}),
        required=True
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'username', 'placeholder': 'Enter Username'}),
        required=True
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'id': 'email', 'placeholder': 'Enter Email'}),
        required=True
    )
    phone_number = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'phone_number', 'placeholder': 'Enter Phone Number'}),
        required=True
    )
    role = forms.ChoiceField(
        choices=User._meta.get_field('role').choices,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'role'}),
        required=True
    )
    gender = forms.ChoiceField(
        choices=User._meta.get_field('gender').choices,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'gender'}),
        required=False  # Make gender optional (you can set it to True if you want it to be required)
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone_number','image', 'role', 'gender', 'password1', 'password2']

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match.")
        return password2

    # def save(self, commit=True):
    #     user = super().save(commit=False)
    #     user.set_password(self.cleaned_data['password1'])  # Set hashed password
    #     if commit:
    #         user.save()
    #     return user

class LoginForm(forms.Form):
    username = forms.CharField(label="Username", widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Add any custom validation for username if necessary
        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        # Add any custom validation for password if necessary
        return password


class CarRegistrationForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['number', 'make', 'model', 'year', 'mileage', 'type', 'seats','status', 'image','price_per_hour', 'discount','price_per_day', 'price_per_month']

    number = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'addCarNumber', 'placeholder': 'Enter car number'}),
        required=True
    )
    
    make = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'addCarMake', 'placeholder': 'Enter car make'}),
        required=True
    )

    model = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'addCarModel', 'placeholder': 'Enter car model'}),
        required=True
    )

    year = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'id': 'addCarYear', 'placeholder': 'Enter car year'}),
        required=True
    )

    mileage = forms.FloatField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'addCarMileage', 'placeholder': 'Enter car mileage'}),
        required=True
    )

    type = forms.ChoiceField(
        choices=Car.CAR_TYPES,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'addCarType'}),
        required=True
    )

    status = forms.ChoiceField(
        choices=Car.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'addCarStatus'}),
        required=True
    )

    image = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'id': 'addCarImage'}),
        required=True
    )
    seats=forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'id': 'addCarSeats'}),
        required=True
    )
    price_per_hour = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control','id': 'price_per_hour'}),
        required=True
    )

    price_per_day = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control','id':'price_per_day'}),
        required=True
    )

    discount = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control','id': 'discount'}),
        required=True
    )
    price_per_month = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control','id': 'price_per_month'}),
        required=True
    )

class ServicesCarForm(forms.ModelForm):
    class Meta:
        model = ServicesCars
        fields = ['car', 'employee', 'service_type', 'service_date', 'cost', 'description', 'status', 'complete_date']
        widgets = {
            'service_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control', 'id': 'service_date'}),
            'complete_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control', 'id': 'complete_date'}),
        }

    car = forms.ModelChoiceField(
        queryset=Car.objects.filter(status='available'),  # Only show cars that are available
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'car', 'placeholder': 'Select a Car'}),
        required=True
    )

    employee = forms.ModelChoiceField(
        queryset=User.objects.filter(role='employee'), 
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'employee', 'placeholder': 'Select an Employee'}), 
        required=True
    )

    service_type = forms.CharField(
        max_length=255, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'service_type', 'placeholder': 'Enter service type'}), 
        required=True
    )

    service_date = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={
                'class': 'form-control',
                'id': 'service_date',
                'type': 'datetime-local',  # Ensure this is set to datetime-local
                'placeholder': 'Select service date'
            }
        ), 
        required=True
    )   

    cost = forms.DecimalField(
        max_digits=10, 
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'id': 'cost', 'placeholder': 'Enter service cost'}), 
        required=True
    )

    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'id': 'description', 'placeholder': 'Enter service description'}), 
        required=True
    )

    status = forms.ChoiceField(
        choices=ServicesCars.SERVICE_STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'status', 'placeholder': 'Select status'}), 
        required=True
    )

    complete_date = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={
                'class': 'form-control',
                'id': 'service_date',
                'type': 'datetime-local',  # Ensure this is set to datetime-local
                'placeholder': 'Select service date'
            }
        ),     
        required=False
    )

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['user', 'car', 'pickup_location','country','pickup_date', 'pickup_time', 'drop_date', 
                  'drop_time', 'state', 'city']

    user = forms.ModelChoiceField(
        queryset=User.objects.filter(role="customer"),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'userSelect'}),
        required=True
    )

    car = forms.ModelChoiceField(
        queryset=Car.objects.filter(status="available"),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'carSelect'}),
        required=True
    )

    driver= forms.ModelChoiceField(
        queryset=User.objects.filter(role="employee"),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'setDriver'}),
        required=False
    )
    
    pickup_location=forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id':'pickupLocation'}),
        required=True
    )

    pickup_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'pickupDate'}),
        required=True
    )

    pickup_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time', 'id': 'pickupTime'}),
        required=True
    )

    drop_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'dropDate'}),
        required=True
    )

    drop_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time', 'id': 'dropTime'}),
        required=True
    )

    country = CountryField().formfield(
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'countrySelect'}),
        required=True
    )

    state = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'stateSelect'}),
        required=True
    )

    city = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'citySelect'}),
        required=True
    )

    receipt_amount = forms.DecimalField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'receiptAmmount', 'readonly': 'readonly'}),
        required=True  
    )
    def __init__(self, *args, **kwargs):
        self.current_driver = kwargs.pop('current_driver', None)  
        super().__init__(*args, **kwargs)
    def save(self, commit=True):
        instance = super().save(commit=False) 
        if not instance.user:
            instance.user = self.user  

        if instance.pickup_date and instance.drop_date:
            duration = (instance.drop_date - instance.pickup_date).days
            if duration > 0:
                if instance.car.type == 'hourly':
                    instance.receipt_amount = duration * instance.car.price_per_hour
                elif instance.car.type == 'daily':
                    instance.receipt_amount = duration * instance.car.price_per_day
                elif instance.car.type == 'monthly':
                    instance.receipt_amount = duration * instance.car.price_per_month

        if commit:
            instance.save()

        return instance

class GetUserFeedbackForm(forms.ModelForm):
    class Meta:
        model = UserFeedback
        fields = ['car', 'rating', 'comments']
    car = forms.ModelChoiceField(
        queryset=Booking.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'bookingSelect'}),
        required=True,
        label="Select Booking"
    )

    rating = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'ratingSelect'}),
        required=True,
        label="Rating (1-5)"
    )

    comments = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'id': 'comments', 'rows': 3,'placeholder': 'Write your feedback...'}),
        required=False,
        label="Comments"
    )

    