"""
Serializers for the fitness booking API.
"""
from rest_framework import serializers
from django.utils import timezone
from django.db import transaction
from .models import FitnessClass, Booking
import logging

logger = logging.getLogger(__name__)


class FitnessClassSerializer(serializers.ModelSerializer):
    """
    Serializer for FitnessClass model.
    Converts datetime to IST for API responses.
    """
    name_display = serializers.CharField(source='get_name_display', read_only=True)
    datetime_ist = serializers.SerializerMethodField()
    is_fully_booked = serializers.ReadOnlyField()
    booked_slots = serializers.ReadOnlyField()
    
    class Meta:
        model = FitnessClass
        fields = [
            'id', 'name', 'name_display', 'instructor', 
            'datetime', 'datetime_ist', 'total_slots', 
            'available_slots', 'booked_slots', 'is_fully_booked'
        ]
        read_only_fields = ['id', 'available_slots', 'booked_slots', 'is_fully_booked']
    
    def get_datetime_ist(self, obj):
        """
        Convert UTC datetime to IST for display.
        """
        if obj.datetime:
            # Convert to IST (Asia/Kolkata timezone)
            ist_datetime = timezone.localtime(obj.datetime)
            return ist_datetime.strftime('%Y-%m-%d %H:%M:%S %Z')
        return None


class BookingRequestSerializer(serializers.Serializer):
    """
    Serializer for handling booking requests.
    """
    class_id = serializers.IntegerField(help_text="ID of the fitness class to book")
    client_name = serializers.CharField(
        max_length=100,
        help_text="Name of the client making the booking"
    )
    client_email = serializers.EmailField(
        help_text="Email address of the client"
    )
    
    def validate_class_id(self, value):
        """
        Validate that the fitness class exists.
        """
        try:
            fitness_class = FitnessClass.objects.get(id=value)
        except FitnessClass.DoesNotExist:
            raise serializers.ValidationError("Fitness class not found.")
        
        # Check if class is in the future
        if fitness_class.datetime <= timezone.now():
            raise serializers.ValidationError("Cannot book a class that has already started or finished.")
        
        return value
    
    def validate(self, data):
        """
        Cross-field validation for booking request.
        """
        try:
            fitness_class = FitnessClass.objects.get(id=data['class_id'])
            
            # Check if user already booked this class
            existing_booking = Booking.objects.filter(
                fitness_class=fitness_class,
                client_email=data['client_email']
            ).exists()
            
            if existing_booking:
                raise serializers.ValidationError("You have already booked this class.")
            
            # Check available slots
            if fitness_class.available_slots <= 0:
                raise serializers.ValidationError("No available slots for this class.")
                
        except FitnessClass.DoesNotExist:
            raise serializers.ValidationError("Fitness class not found.")
        
        return data
    
    def create(self, validated_data):
        """
        Create a new booking with atomic transaction to prevent race conditions.
        """
        class_id = validated_data['class_id']
        client_name = validated_data['client_name']
        client_email = validated_data['client_email']
        
        with transaction.atomic():
            # Lock the fitness class row to prevent race conditions
            fitness_class = FitnessClass.objects.select_for_update().get(id=class_id)
            
            # Double-check availability (in case of concurrent requests)
            if fitness_class.available_slots <= 0:
                raise serializers.ValidationError("No available slots for this class.")
            
            # Create the booking
            booking = Booking.objects.create(
                fitness_class=fitness_class,
                client_name=client_name,
                client_email=client_email
            )
            
            # Decrease available slots
            fitness_class.available_slots -= 1
            fitness_class.save()
            
            logger.info(f"Booking successful: {booking}")
            return booking


class BookingSerializer(serializers.ModelSerializer):
    """
    Serializer for Booking model with class details.
    """
    fitness_class_details = serializers.SerializerMethodField()
    booked_at_ist = serializers.SerializerMethodField()
    
    class Meta:
        model = Booking
        fields = [
            'id', 'client_name', 'client_email', 
            'booked_at', 'booked_at_ist', 'fitness_class_details'
        ]
        read_only_fields = ['id', 'booked_at']
    
    def get_fitness_class_details(self, obj):
        """
        Get detailed information about the booked fitness class.
        """
        fitness_class = obj.fitness_class
        ist_datetime = timezone.localtime(fitness_class.datetime)
        
        return {
            'id': fitness_class.id,
            'name': fitness_class.get_name_display(),
            'instructor': fitness_class.instructor,
            'datetime': fitness_class.datetime.isoformat(),
            'datetime_ist': ist_datetime.strftime('%Y-%m-%d %H:%M:%S %Z'),
            'total_slots': fitness_class.total_slots,
            'available_slots': fitness_class.available_slots
        }
    
    def get_booked_at_ist(self, obj):
        """
        Convert booking timestamp to IST.
        """
        if obj.booked_at:
            ist_datetime = timezone.localtime(obj.booked_at)
            return ist_datetime.strftime('%Y-%m-%d %H:%M:%S %Z')
        return None
