from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, time, timedelta
from decimal import Decimal
import random
from booking.models import TravelOption


class Command(BaseCommand):
    help = 'Populate the database with sample travel options'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=20,
            help='Number of travel options to create',
        )

    def handle(self, *args, **options):
        count = options['count']
        
        # Sample Indian cities
        cities = [
            'Mumbai', 'Delhi', 'Bengaluru', 'Hyderabad', 'Chennai', 'Kolkata',
            'Pune', 'Ahmedabad', 'Jaipur', 'Lucknow', 'Kanpur', 'Nagpur',
            'Indore', 'Bhopal', 'Visakhapatnam', 'Vadodara', 'Ludhiana', 'Agra',
            'Nashik', 'Faridabad', 'Meerut', 'Varanasi', 'Srinagar', 'Amritsar'
        ]
        
        travel_types = ['flight', 'train', 'bus']
        
        # Clear existing sample data
        TravelOption.objects.filter(travel_id__startswith='SAMPLE').delete()
        
        created_count = 0
        
        for i in range(count):
            # Random source and destination (make sure they're different)
            source = random.choice(cities)
            destination = random.choice([city for city in cities if city != source])
            
            # Random travel type
            travel_type = random.choice(travel_types)
            
            # Generate travel ID
            prefix = {
                'flight': 'FL',
                'train': 'TR',
                'bus': 'BS'
            }[travel_type]
            travel_id = f"SAMPLE{prefix}{str(i+1).zfill(3)}"
            
            # Random departure date (next 30 days)
            departure_date = date.today() + timedelta(days=random.randint(1, 30))
            
            # Random departure time
            departure_hour = random.randint(6, 22)
            departure_minute = random.choice([0, 15, 30, 45])
            departure_time = time(departure_hour, departure_minute)
            
            # Calculate arrival (add random travel time based on type)
            if travel_type == 'flight':
                travel_duration = timedelta(hours=random.randint(1, 6))
                price_range = (3000, 15000)  # ₹3,000 to ₹15,000
                seat_range = (50, 300)
            elif travel_type == 'train':
                travel_duration = timedelta(hours=random.randint(3, 12))
                price_range = (500, 3000)   # ₹500 to ₹3,000
                seat_range = (100, 500)
            else:  # bus
                travel_duration = timedelta(hours=random.randint(4, 15))
                price_range = (300, 2000)   # ₹300 to ₹2,000
                seat_range = (30, 60)
            
            arrival_datetime = timezone.datetime.combine(departure_date, departure_time) + travel_duration
            arrival_date = arrival_datetime.date()
            arrival_time = arrival_datetime.time()
            
            # Random price
            price = Decimal(str(random.randint(*price_range) + random.random())).quantize(Decimal('0.01'))
            
            # Random seat configuration
            total_seats = random.randint(*seat_range)
            available_seats = random.randint(0, total_seats)
            
            try:
                travel_option = TravelOption.objects.create(
                    travel_id=travel_id,
                    type=travel_type,
                    source=source,
                    destination=destination,
                    departure_date=departure_date,
                    departure_time=departure_time,
                    arrival_date=arrival_date,
                    arrival_time=arrival_time,
                    price=price,
                    available_seats=available_seats,
                    total_seats=total_seats
                )
                created_count += 1
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created: {travel_option.travel_id} - {source} to {destination}'
                    )
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating travel option: {e}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} travel options')
        )
