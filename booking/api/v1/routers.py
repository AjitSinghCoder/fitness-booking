from django.urls import path
from .booking_views import (
    BookClassView,
    GetBookingsView,
)
from .class_views import (
    FitnessClassListCreateView,
)


urlpatterns = [
    path("classes/", FitnessClassListCreateView.as_view(), name="fitness-classes"),
    path("book/", BookClassView.as_view(), name="book-class"),
    path("bookings/", GetBookingsView.as_view(), name="get-bookings"),
]
