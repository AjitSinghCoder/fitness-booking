from rest_framework import generics
from django.utils import timezone
from booking.models import FitnessClass
from booking.serializers import FitnessClassSerializer
from utils.response import  CustomResponse

class FitnessClassListCreateView(generics.ListCreateAPIView):
    serializer_class = FitnessClassSerializer

    def get_queryset(self):
        return FitnessClass.objects.filter(datetime__gt=timezone.now()).order_by("datetime")

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse.list_response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return CustomResponse.create_response(serializer.data)
        return CustomResponse.error_occurred_response(errors=serializer.errors)