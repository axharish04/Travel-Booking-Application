from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import date, time, timedelta
from decimal import Decimal
from .models import UserProfile, TravelOption, Booking


class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_profile_creation(self):
        profile = UserProfile.objects.create(
            user=self.user,
            phone='1234567890',
            address='123 Test St'
        )
        self.assertEqual(str(profile), "testuser's Profile")
        self.assertEqual(profile.phone, '1234567890')


class TravelOptionModelTest(TestCase):
    def setUp(self):
        self.travel = TravelOption.objects.create(
            travel_id='FL001',
            type='flight',
            source='New York',
            destination='Los Angeles',
            departure_date=date.today() + timedelta(days=7),
            departure_time=time(10, 0),
            arrival_date=date.today() + timedelta(days=7),
            arrival_time=time(13, 0),
            price=Decimal('299.99'),
            available_seats=50,
            total_seats=50
        )
    
    def test_travel_option_creation(self):
        self.assertEqual(str(self.travel), 'FL001 - New York to Los Angeles')
        self.assertTrue(self.travel.is_available)
    
    def test_travel_option_not_available(self):
        # Set departure date to yesterday
        self.travel.departure_date = date.today() - timedelta(days=1)
        self.travel.save()
        self.assertFalse(self.travel.is_available)
    
    def test_no_seats_available(self):
        self.travel.available_seats = 0
        self.travel.save()
        self.assertFalse(self.travel.is_available)


class BookingModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.travel = TravelOption.objects.create(
            travel_id='FL001',
            type='flight',
            source='New York',
            destination='Los Angeles',
            departure_date=date.today() + timedelta(days=7),
            departure_time=time(10, 0),
            arrival_date=date.today() + timedelta(days=7),
            arrival_time=time(13, 0),
            price=Decimal('299.99'),
            available_seats=50,
            total_seats=50
        )
    
    def test_booking_creation(self):
        booking = Booking.objects.create(
            user=self.user,
            travel_option=self.travel,
            number_of_seats=2,
            passenger_names='John Doe, Jane Doe',
            contact_email='test@example.com',
            contact_phone='1234567890'
        )
        
        self.assertTrue(booking.booking_id.startswith('BK'))
        self.assertEqual(booking.total_price, Decimal('599.98'))
        self.assertEqual(booking.status, 'confirmed')
        self.assertTrue(booking.can_cancel())
    
    def test_booking_cannot_cancel_near_departure(self):
        # Set departure to tomorrow
        self.travel.departure_date = date.today() + timedelta(days=1)
        self.travel.departure_time = time(10, 0)
        self.travel.save()
        
        booking = Booking.objects.create(
            user=self.user,
            travel_option=self.travel,
            number_of_seats=1,
            passenger_names='John Doe',
            contact_email='test@example.com',
            contact_phone='1234567890'
        )
        
        self.assertFalse(booking.can_cancel())


class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        UserProfile.objects.create(user=self.user)
        
        self.travel = TravelOption.objects.create(
            travel_id='FL001',
            type='flight',
            source='New York',
            destination='Los Angeles',
            departure_date=date.today() + timedelta(days=7),
            departure_time=time(10, 0),
            arrival_date=date.today() + timedelta(days=7),
            arrival_time=time(13, 0),
            price=Decimal('299.99'),
            available_seats=50,
            total_seats=50
        )
    
    def test_travel_list_view(self):
        response = self.client.get(reverse('travel_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'New York')
        self.assertContains(response, 'Los Angeles')
    
    def test_travel_detail_view(self):
        response = self.client.get(reverse('travel_detail', args=[self.travel.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'FL001')
    
    def test_register_view(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        
        # Test registration
        data = {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@example.com',
            'password1': 'testpass123!',
            'password2': 'testpass123!'
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_login_required_for_booking(self):
        response = self.client.get(reverse('book_travel', args=[self.travel.id]))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_booking_view_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('book_travel', args=[self.travel.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Book Your Travel')
    
    def test_my_bookings_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('my_bookings'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Bookings')
    
    def test_profile_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Update Profile')


class BookingProcessTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        UserProfile.objects.create(user=self.user)
        
        self.travel = TravelOption.objects.create(
            travel_id='FL001',
            type='flight',
            source='New York',
            destination='Los Angeles',
            departure_date=date.today() + timedelta(days=7),
            departure_time=time(10, 0),
            arrival_date=date.today() + timedelta(days=7),
            arrival_time=time(13, 0),
            price=Decimal('299.99'),
            available_seats=50,
            total_seats=50
        )
    
    def test_full_booking_process(self):
        self.client.login(username='testuser', password='testpass123')
        
        # Create booking
        booking_data = {
            'number_of_seats': 2,
            'passenger_names': 'John Doe, Jane Doe',
            'contact_email': 'test@example.com',
            'contact_phone': '1234567890'
        }
        
        response = self.client.post(
            reverse('book_travel', args=[self.travel.id]),
            booking_data
        )
        
        # Should redirect to my_bookings after successful booking
        self.assertEqual(response.status_code, 302)
        
        # Check if booking was created
        booking = Booking.objects.filter(user=self.user).first()
        self.assertIsNotNone(booking)
        self.assertEqual(booking.number_of_seats, 2)
        self.assertEqual(booking.total_price, Decimal('599.98'))
        
        # Check if available seats were updated
        self.travel.refresh_from_db()
        self.assertEqual(self.travel.available_seats, 48)
    
    def test_booking_validation_insufficient_seats(self):
        self.client.login(username='testuser', password='testpass123')
        
        # Set available seats to 1
        self.travel.available_seats = 1
        self.travel.save()
        
        booking_data = {
            'number_of_seats': 2,  # Requesting more than available
            'passenger_names': 'John Doe, Jane Doe',
            'contact_email': 'test@example.com',
            'contact_phone': '1234567890'
        }
        
        response = self.client.post(
            reverse('book_travel', args=[self.travel.id]),
            booking_data
        )
        
        # Should not create booking
        self.assertEqual(Booking.objects.filter(user=self.user).count(), 0)


class SearchFilterTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create multiple travel options
        TravelOption.objects.create(
            travel_id='FL001',
            type='flight',
            source='New York',
            destination='Los Angeles',
            departure_date=date.today() + timedelta(days=7),
            departure_time=time(10, 0),
            arrival_date=date.today() + timedelta(days=7),
            arrival_time=time(13, 0),
            price=Decimal('299.99'),
            available_seats=50,
            total_seats=50
        )
        
        TravelOption.objects.create(
            travel_id='TR001',
            type='train',
            source='Chicago',
            destination='Detroit',
            departure_date=date.today() + timedelta(days=5),
            departure_time=time(14, 0),
            arrival_date=date.today() + timedelta(days=5),
            arrival_time=time(18, 0),
            price=Decimal('89.99'),
            available_seats=100,
            total_seats=100
        )
    
    def test_search_by_source(self):
        response = self.client.get(reverse('travel_list'), {'source': 'New York'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'FL001')
        self.assertNotContains(response, 'TR001')
    
    def test_search_by_type(self):
        response = self.client.get(reverse('travel_list'), {'travel_type': 'train'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TR001')
        self.assertNotContains(response, 'FL001')
    
    def test_search_by_destination(self):
        response = self.client.get(reverse('travel_list'), {'destination': 'Detroit'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TR001')
        self.assertNotContains(response, 'FL001')
