from django.contrib import admin
from .models import User, Car ,ServicesCars ,Booking ,UserFeedback
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'first_name', 'last_name', 'email', 'phone_number', 'gender', 'role' ,'is_active', 'is_staff']
    search_fields = ['saved_cars','id', 'username', 'email', 'gender']
    list_filter = ['gender', 'role', 'is_active', 'is_staff','saved_cars']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'image', 'gender','saved_cars')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Role', {'fields': ('role',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'role'),
            
        }),
        ('Timestamps', {  # Move timestamps to a separate section
            'fields': ('created_at', 'updated_at')
        }),
    )

class CarAdmin(admin.ModelAdmin):
    list_display = ['model', 'make', 'year', 'number', 'type', 'seats', 'mileage', 'status']
    search_fields = ['model', 'make', 'number', 'type','status','discount']
    list_filter = ['type', 'status', 'year']
    readonly_fields = ('created_at', 'updated_at')
     

    fieldsets = (
        (None, {'fields': ('model', 'make', 'year', 'number', 'image' ,'discount','price_per_hour','price_per_day','price_per_month')}),
        ('Details', {'fields': ('type', 'seats', 'mileage')}),
        ('Availability', {'fields': ('status',)}),
        ('Timestamps', {  # Move timestamps to a separate section
            'fields': ('created_at', 'updated_at')
        }),
    )
class ServiceRecordAdmin(admin.ModelAdmin):
    list_display = ['car', 'employee', 'service_type', 'service_date', 'cost', 'status']
    search_fields = ['car__model', 'car__number', 'employee__username', 'service_type']
    list_filter = ['service_type', 'status', 'service_date', 'complete_date']
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {'fields': ('car', 'employee', 'service_type', 'service_date', 'complete_date', 'cost')}),
        ('Details', {'fields': ('description', 'status')}),
        ('Timestamps', {  # Move timestamps to a separate section
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    ordering = ['service_date']
    list_per_page = 20
   

admin.site.register(ServicesCars, ServiceRecordAdmin)


admin.site.register(User, UserAdmin)
admin.site.register(Car, CarAdmin)

class BookingAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'car', 'booking_status', 'pickup_date', 'pickup_location', 'pickup_time', 'drop_date', 
        'drop_time', 'get_country', 'state', 'city', 'driver', 'payment_status', 'receipt_amount'  # Fixed typo
    ]
    
    # Add filters to make it easier to narrow down bookings based on attributes
    list_filter = [
        'user', 'car', 'pickup_date', 'drop_date', 'state', 'city', 'driver', 'payment_status', 'receipt_amount'  # Fixed typo
    ]
    
    # Add search functionality for user, car, and location fields
    search_fields = ['user__username', 'booking_status', 'car__model', 'car__make', 'state', 'city', 'receipt_amount', 'payment_status']  # Fixed car__name

    # Mark non-editable fields as read-only
    readonly_fields = ('created_at', 'updated_at')

    # Organize fields in the admin panel
    fieldsets = (
        ('Booking Details', {
            'fields': ('user', 'car', 'pickup_date', 'pickup_time', 'drop_date', 'drop_time')
        }),
        ('Location', {
            'fields': ('country', 'state', 'city', 'pickup_location')
        }),
        ('Driver & Payment Details', {
            'fields': ('driver', 'booking_status', 'payment_status', 'receipt_amount')
        }),
        ('Timestamps', {  # Move timestamps to a separate section
            'fields': ('created_at', 'updated_at')
        }),
    )

    # Add ordering to the admin list view
    ordering = ['pickup_date', 'pickup_time']

    # Use a method to display the country in the list view
    def get_country(self, obj):
        return obj.country.name  # Or obj.country.code depending on how you want to display it
    get_country.short_description = 'Country' 
    def get_car(self, obj):
        return f"{obj.car.make} {obj.car.model}"  # Assuming your car has make and model fields
    get_car.short_description = 'Car'  # Label for the column in the admin list

admin.site.register(Booking, BookingAdmin)

@admin.register(UserFeedback)
class UserFeedbackAdmin(admin.ModelAdmin):
    list_display = ('car', 'rating', 'comments','created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'booking_car__id')
