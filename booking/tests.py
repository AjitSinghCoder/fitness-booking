from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.utils import timezone
from booking.models import FitnessClass,Booking
from unittest.mock import patch

import pytz
from datetime import timedelta


class FitnessClassTests(APITestCase):

    def setUp(self):
        # Create two fitness classes: one upcoming, one past
        self.ist = pytz.timezone('Asia/Kolkata')
        self.upcoming_class = FitnessClass.objects.create(
            name="YOGA",
            instructor="Instructor A",
            datetime=timezone.now() + timedelta(days=2),
            total_slots=10,
            available_slots=10
        )
        self.past_class = FitnessClass(
            name="HIIT",
            instructor="Instructor B",
            datetime=timezone.now() - timedelta(days=2),
            total_slots=10,
            available_slots=10
        )
        with patch.object(FitnessClass, 'full_clean', return_value=None):
            self.past_class.save()

    def test_list_upcoming_fitness_classes(self):
        url = '/api/v1/classes/' 
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['count'], 1)


class BookingTests(APITestCase):

    def setUp(self):
        self.fitness_class = FitnessClass.objects.create(
            name="ZUMBA",
            instructor="Instructor C",
            datetime=timezone.now() + timedelta(days=1),
            total_slots=5,
            available_slots=5
        )
        self.booking = Booking.objects.create(
            fitness_class=self.fitness_class,
            client_name="Test Client",
            client_email="client@example.com"
        )
        self.list_url = '/api/v1/bookings/'
        self.create_url = '/api/v1/book/'
    def test_list_bookings_by_email_success(self):
        response = self.client.get(self.list_url, {'email': 'client@example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data['data']), 1)
        self.assertEqual(data['data'][0]['client_email'], "client@example.com")

    def test_list_bookings_missing_email_param(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertEqual(data['status'], 'error')
        self.assertIn('Email query parameter is required', data['message'])

    def test_create_booking_success(self):
        payload = {
            "class_id": self.fitness_class.id,
            "client_name": "New Client",
            "client_email": "newclient@example.com"
        }
        response = self.client.post(self.create_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['data']['client_name'], "New Client")

    def test_create_booking_already_booked(self):
        payload = {
            "class_id": self.fitness_class.id,
            "client_name": "Test Client",
            "client_email": "client@example.com"
        }
        response = self.client.post(self.create_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertEqual(data['status'], 'error')

    def test_create_booking_no_slots(self):
        # Set available_slots to 0
        self.fitness_class.available_slots = 0
        self.fitness_class.save()

        payload = {
            "class_id": self.fitness_class.id,
            "client_name": "Another Client",
            "client_email": "another@example.com"
        }
        response = self.client.post(self.create_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertEqual(data['status'], 'error')

    def test_create_booking_past_class(self):
        from unittest.mock import patch

        past_class = FitnessClass(
            name="HIIT",
            instructor="Past Instructor",
            datetime=timezone.now() - timedelta(days=1),
            total_slots=5,
            available_slots=5,
        )
        with patch.object(FitnessClass, 'full_clean', return_value=None):
            past_class.save()

        payload = {
            "class_id": past_class.id,
            "client_name": "Late Client",
            "client_email": "late@example.com"
        }
        response = self.client.post(self.create_url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertEqual(data['status'], 'error')
