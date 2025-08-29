from django.contrib import admin
from .models import UserProfile, TravelOption, Booking


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'date_of_birth')
    search_fields = ('user__username', 'user__email', 'phone')
    list_filter = ('date_of_birth',)


@admin.register(TravelOption)
class TravelOptionAdmin(admin.ModelAdmin):
    list_display = ('travel_id', 'type', 'source', 'destination', 'departure_date', 'departure_time', 'price', 'available_seats')
    list_filter = ('type', 'departure_date', 'source', 'destination')
    search_fields = ('travel_id', 'source', 'destination')
    ordering = ('departure_date', 'departure_time')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('travel_id', 'type', 'source', 'destination')
        }),
        ('Schedule', {
            'fields': ('departure_date', 'departure_time', 'arrival_date', 'arrival_time')
        }),
        ('Pricing & Capacity', {
            'fields': ('price', 'total_seats', 'available_seats')
        }),
    )


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'user', 'travel_option', 'number_of_seats', 'total_price', 'status', 'booking_date')
    list_filter = ('status', 'booking_date', 'travel_option__type')
    search_fields = ('booking_id', 'user__username', 'travel_option__travel_id')
    readonly_fields = ('booking_id', 'booking_date', 'total_price')
    ordering = ('-booking_date',)
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('booking_id', 'user', 'travel_option', 'status')
        }),
        ('Travel Details', {
            'fields': ('number_of_seats', 'total_price', 'booking_date')
        }),
        ('Passenger Information', {
            'fields': ('passenger_names', 'contact_email', 'contact_phone')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new booking
            obj.total_price = obj.travel_option.price * obj.number_of_seats
        super().save_model(request, obj, form, change)
