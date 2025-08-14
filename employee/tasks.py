from celery import shared_task

@shared_task
def booking_confirmed_notification(username, car_model, car_number, driver_name, driver_contact, pickup_date):
    print("========================================")
    print(f"✅ Booking Confirmed!")
    print(f"👤 Username: {username}")
    print(f"🚗 Car Model: {car_model}")
    print(f"🚗 Car Number: {car_number}")
    print(f"🧑‍✈️ Driver Name: {driver_name}")
    print(f"📞 Driver Contact: {driver_contact}")
    print(f"🕒 Pickup Date: {pickup_date}")
    print("========================================")
