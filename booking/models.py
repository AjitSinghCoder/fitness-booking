from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.validators import MinValueValidator
from utils.basemodel import BaseModel
import logging
logger = logging.getLogger(__name__)





class FitnessClass(BaseModel):
    """
    Model representing a fitness class offered by the studio.
    """

    CLASS_TYPES = [
        ("YOGA", "Yoga"),
        ("ZUMBA", "Zumba"),
        ("HIIT", "HIIT"),
    ]
    name = models.CharField(max_length=100, choices=CLASS_TYPES)
    instructor = models.CharField(max_length=100)
    datetime = models.DateTimeField()
    total_slots = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
    )
    available_slots = models.PositiveIntegerField(
        validators=[MinValueValidator(0)],
    )

    class Meta:
        ordering = ["datetime"]
        verbose_name = "Fitness Class"
        verbose_name_plural = "Fitness Classes"


    def clean(self):
        """
        Custom validation for the model.
        """
        super().clean()

        # Ensure available_slots doesn't exceed total_slots
        if self.available_slots > self.total_slots:
            raise ValidationError(
                {"available_slots": "Available slots cannot exceed total slots."}
            )

        # Ensure class is scheduled for future (only for new classes)
        if not self.pk and self.datetime <= timezone.now():
            raise ValidationError(
                {"datetime": "Class must be scheduled for a future date and time."}
            )

    def save(self, *args, **kwargs):
        # Set available_slots to total_slots for new classes
        if not self.pk:
            self.available_slots = self.total_slots

        self.full_clean()  # Run validation
        super().save(*args, **kwargs)
        logger.info(f"Fitness class saved: {self}")

    @property
    def is_fully_booked(self):
        """Check if the class is fully booked."""
        return self.available_slots == 0

    @property
    def booked_slots(self):
        """Calculate number of booked slots."""
        return self.total_slots - self.available_slots


class Booking(BaseModel):
    fitness_class = models.ForeignKey(
        FitnessClass,
        on_delete=models.CASCADE,
        related_name="bookings",
    )
    client_name = models.CharField(max_length=100,)
    client_email = models.EmailField()
    booked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-booked_at"]
        unique_together = [
            "fitness_class",
            "client_email",
        ]  # Prevent duplicate bookings
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        logger.info(f"Booking created: {self}")
