from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
import requests
import uuid
from django.conf import settings
from .models import Listing, Booking, Payment
from .serializers import ListingSerializer, BookingSerializer, PaymentSerializer
from listings.tasks import send_booking_confirmation_email, send_payment_confirmation_email

class ListingViewSet(viewsets.ModelViewSet):
    """
    A viewset for performing CRUD operations on Property model.
    """
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer

class BookingViewSet(viewsets.ModelViewSet):
    """
    A viewset for performing CRUD operations on Booking model.
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def perform_create(self, serializer):
        booking = serializer.save()
        send_booking_confirmation_email.delay(booking.id, booking.user.email)

CHAPA_URL = "https://api.chapa.co/v1/transaction/initialize"

class PaymentViewSet(viewsets.ModelViewSet):
    """
    A viewset to handle payments using Chapa API.
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def perform_create(self, serializer):
        payment = serializer.save()
        # Send payment confirmation email asynchronously
        send_payment_confirmation_email.delay(payment.booking.user.email)

    @action(detail=True, methods=['post'])
    def initiate_payment(self, request, pk=None):
        """
        Initiates a payment transaction with Chapa.
        """
        try:
            booking = Booking.objects.get(id=pk)
            if hasattr(booking, 'payment'):
                return Response({'error': 'Payment already initiated for this booking.'}, status=status.HTTP_400_BAD_REQUEST)

            transaction_id = str(uuid.uuid4())

            headers = {
                "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
                "Content-Type": "application/json",
            }
            payload = {
                "amount": str(booking.total_price),
                "currency": "ETB",
                "email": booking.user.email,
                "first_name": booking.user.first_name,
                "last_name": booking.user.last_name,
                "tx_ref": transaction_id,
                "callback_url": "https://dummy.com/payment/callback/",
            }

            response = requests.post(CHAPA_URL, json=payload, headers=headers)
            response_data = response.json()

            if response.status_code == 200 and response_data.get("status") == "success":
                payment = Payment.objects.create(
                    booking=booking,
                    amount=booking.total_price,
                    transaction_id=transaction_id,
                    status="pending"
                )
                return Response({"payment_url": response_data["data"]["checkout_url"], "transaction_id": transaction_id})

            return Response({"error": "Payment initiation failed"}, status=status.HTTP_400_BAD_REQUEST)
        
        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'])
    def verify_payment(self, request, pk=None):
        """
        Verifies the payment status with Chapa.
        """
        try:
            payment = Payment.objects.get(booking_id=pk)

            url = f"https://api.chapa.co/v1/transaction/verify/{payment.transaction_id}"
            headers = {"Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"}

            response = requests.get(url, headers=headers)
            response_data = response.json()

            if response.status_code == 200 and response_data.get("status") == "success":
                payment.status = "completed"
            else:
                payment.status = "failed"

            payment.save()
            return Response({"status": payment.status})

        except Payment.DoesNotExist:
            return Response({'error': 'Payment record not found.'}, status=status.HTTP_404_NOT_FOUND)