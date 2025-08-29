from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"


class TravelOption(models.Model):
    TRAVEL_TYPES = [
        ('flight', 'Flight'),
        ('train', 'Train'),
        ('bus', 'Bus'),
    ]
    
    travel_id = models.CharField(max_length=20, unique=True)
    type = models.CharField(max_length=10, choices=TRAVEL_TYPES)
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    departure_date = models.DateField()
    departure_time = models.TimeField()
    arrival_date = models.DateField()
    arrival_time = models.TimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    available_seats = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    total_seats = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['departure_date', 'departure_time']
    
    def __str__(self):
        return f"{self.travel_id} - {self.source} to {self.destination}"
    
    @property
    def is_available(self):
        return self.available_seats > 0 and self.departure_date >= timezone.now().date()


class Booking(models.Model):
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    
    booking_id = models.CharField(max_length=20, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    travel_option = models.ForeignKey(TravelOption, on_delete=models.CASCADE)
    number_of_seats = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='confirmed')
    passenger_names = models.TextField(help_text="Enter passenger names separated by commas")
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=15)
    
    class Meta:
        ordering = ['-booking_date']
    
    def __str__(self):
        return f"Booking {self.booking_id} - {self.user.username}"
    
    def save(self, *args, **kwargs):
        if not self.booking_id:
            # Generate booking ID
            import uuid
            self.booking_id = f"BK{str(uuid.uuid4().hex)[:8].upper()}"
        
        if not self.total_price:
            self.total_price = self.travel_option.price * self.number_of_seats
        
        super().save(*args, **kwargs)
    
    def can_cancel(self):
        """Check if booking can be cancelled (at least 24 hours before departure)"""
        if self.status == 'cancelled':
            return False
        
        departure_datetime = timezone.datetime.combine(
            self.travel_option.departure_date,
            self.travel_option.departure_time
        )
        departure_datetime = timezone.make_aware(departure_datetime)
        
        return departure_datetime > timezone.now() + timezone.timedelta(hours=24)
