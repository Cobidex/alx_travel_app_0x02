from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_booking_confirmation_email(booking_id, user_email):
    subject = "Booking Confirmation"
    message = f"Your booking with ID {booking_id} has been confirmed."
    sender = "no-reply@alxtravel.com"
    
    send_mail(subject, message, sender, [user_email])
    
    return f"Email sent to {user_email}"

@shared_task
def send_payment_confirmation_email(user_email):
    subject = "Payment Confirmation"
    message = "Your payment has been received and confirmed."
    sender = "no-reply@alxtravel.com"