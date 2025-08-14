from celery import shared_task
from datetime import datetime


@shared_task
def display_registered_user_info(username, first_name,last_name,email, phone, role):
    print("========================================")
    print(f"✅  Registered!")
    print(f"👤 Username: {username}")
    print(f" First Name:{first_name}")
    print(f"last Name:{last_name}")
    print(f"📧 Email: {email}")
    print(f"📞 Phone: {phone}")
    print(f"🎭 Role: {role}")
    print("========================================")



@shared_task
def login_user(username):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("========================================")
    print(f"✅  User Logged In!")
    print(f"👤 Username: {username}")
    print(f"🕒 Login Time: {current_time}")
    print("========================================")
@shared_task
def logout_user(username):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("========================================")
    print(f"✅  User Logged Out!")
    print(f"👤 Username: {username}")
    print(f"🕒 Logout Time: {current_time}")
    print("========================================")

@shared_task
def booking_success_notification(username, car_model, number, receipt_amount, pickup_date):
    print("========================================")
    print(f"✅  Car Booking Successful!")
    print(f"👤 Username: {username}")
    print(f"🚗 Car Model: {car_model}")
    print(f"🚗 Car Number: {number}")
    print(f"💰 Receipt Amount: {receipt_amount}")
    print(f"🕒 Booking Time: {pickup_date}")
    print("========================================")

@shared_task
def feedback_submission_notification(username, car_model, rating, comments):
    print("========================================")
    print(f"✅ Feedback Submitted!")
    print(f"👤 Username: {username}")
    print(f"🚗 Car Model: {car_model}")
    print(f"⭐ Rating: {rating}")
    print(f"💬 Comments: {comments}")
    print("========================================")

@shared_task
def password_update_notification(username, new_password):
    print("========================================")
    print(f"🔐 Password Update Notification")
    print(f"👤 Username: {username}")
    print(f"🔑 New Password: {new_password}")  # ⚠️ (For security reasons, avoid displaying plaintext passwords)
    print("========================================")