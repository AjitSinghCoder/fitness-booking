from rest_framework import generics, status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import transaction, IntegrityError
from booking.models import Booking
from booking.serializers import BookingRequestSerializer, BookingSerializer
from utils.response import CustomResponse  # import your custom response class

class BookClassView(generics.CreateAPIView):
    serializer_class = BookingRequestSerializer

    @swagger_auto_schema(
        request_body=BookingRequestSerializer,
        responses={
            201: "Booking successful",
            400: "Invalid booking data or duplicate booking"
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                booking = serializer.save()
                booking_data = BookingSerializer(booking).data
                return CustomResponse.create_response(
                    data=booking_data,
                    message="Booking successful!"
                )
            except IntegrityError:
                return CustomResponse.error_occurred_response(
                    message="You have already booked this class.",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            except serializer.ValidationError as e:
                # To handle ValidationError raised inside create()
                return CustomResponse.error_occurred_response(
                    message=str(e),
                    status_code=status.HTTP_400_BAD_REQUEST
                )
        return CustomResponse.error_occurred_response(
            message="Invalid booking data.",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )

class GetBookingsView(generics.ListAPIView):
    serializer_class = BookingSerializer

    email_param = openapi.Parameter(
        'email',
        openapi.IN_QUERY,
        description="Email address to filter bookings",
        type=openapi.TYPE_STRING,
        required=True
    )

    @swagger_auto_schema(manual_parameters=[email_param])
    def get(self, request, *args, **kwargs):
        email = request.query_params.get('email', '').strip()
        if not email:
            return CustomResponse.error_occurred_response(
                message="Email query parameter is required.",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        bookings = Booking.objects.filter(client_email__iexact=email)
        serializer = self.get_serializer(bookings, many=True)
        return CustomResponse.list_response(serializer.data, message=f"Bookings for {email}")
