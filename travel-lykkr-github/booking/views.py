from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.db import transaction
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import TravelOption, Booking, UserProfile
from .forms import CustomUserCreationForm, UserProfileForm, UserUpdateForm, TravelSearchForm, BookingForm


def travel_list(request):
    """Display list of available travel options with search and filter functionality"""
    form = TravelSearchForm(request.GET)
    travels = TravelOption.objects.filter(departure_date__gte=timezone.now().date())
    
    if form.is_valid():
        source = form.cleaned_data.get('source')
        destination = form.cleaned_data.get('destination')
        travel_type = form.cleaned_data.get('travel_type')
        departure_date = form.cleaned_data.get('departure_date')
        
        if source:
            travels = travels.filter(source__icontains=source)
        if destination:
            travels = travels.filter(destination__icontains=destination)
        if travel_type:
            travels = travels.filter(type=travel_type)
        if departure_date:
            travels = travels.filter(departure_date=departure_date)
    
    # Pagination
    paginator = Paginator(travels, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'page_obj': page_obj,
        'travels': page_obj,
    }
    return render(request, 'booking/travel_list.html', context)


def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(user=user)
            messages.success(request, 'Registration successful! You can now log in.')
            login(request, user)
            return redirect('travel_list')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})


@login_required
def profile(request):
    """User profile view"""
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, instance=user_profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=user_profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'booking/profile.html', context)


@login_required
def book_travel(request, travel_id):
    """Book a travel option"""
    travel = get_object_or_404(TravelOption, id=travel_id)
    
    if not travel.is_available:
        messages.error(request, 'This travel option is no longer available.')
        return redirect('travel_list')
    
    if request.method == 'POST':
        form = BookingForm(request.POST, travel_option=travel)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Check availability again within transaction
                    travel.refresh_from_db()
                    seats_requested = form.cleaned_data['number_of_seats']
                    
                    if travel.available_seats < seats_requested:
                        messages.error(request, 'Not enough seats available.')
                        return redirect('book_travel', travel_id=travel_id)
                    
                    # Create booking
                    booking = form.save(commit=False)
                    booking.user = request.user
                    booking.travel_option = travel
                    booking.total_price = travel.price * seats_requested
                    booking.save()
                    
                    # Update available seats
                    travel.available_seats -= seats_requested
                    travel.save()
                    
                    messages.success(request, f'Booking confirmed! Your booking ID is {booking.booking_id}')
                    return redirect('my_bookings')
                    
            except Exception as e:
                messages.error(request, 'An error occurred while processing your booking. Please try again.')
                return redirect('book_travel', travel_id=travel_id)
    else:
        # Pre-fill contact information from user profile
        initial_data = {
            'contact_email': request.user.email,
        }
        try:
            profile = request.user.userprofile
            if profile.phone:
                initial_data['contact_phone'] = profile.phone
        except UserProfile.DoesNotExist:
            pass
        
        form = BookingForm(travel_option=travel, initial=initial_data)
    
    context = {
        'form': form,
        'travel': travel,
    }
    return render(request, 'booking/book_travel.html', context)


@login_required
def my_bookings(request):
    """Display user's bookings"""
    bookings = Booking.objects.filter(user=request.user)
    
    # Pagination
    paginator = Paginator(bookings, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'bookings': page_obj,
    }
    return render(request, 'booking/my_bookings.html', context)


@login_required
def cancel_booking(request, booking_id):
    """Cancel a booking"""
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)
    
    if not booking.can_cancel():
        messages.error(request, 'This booking cannot be cancelled.')
        return redirect('my_bookings')
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Update booking status
                booking.status = 'cancelled'
                booking.save()
                
                # Restore available seats
                travel = booking.travel_option
                travel.available_seats += booking.number_of_seats
                travel.save()
                
                messages.success(request, 'Booking cancelled successfully!')
        except Exception as e:
            messages.error(request, 'An error occurred while cancelling your booking. Please try again.')
        
        return redirect('my_bookings')
    
    context = {
        'booking': booking,
    }
    return render(request, 'booking/cancel_booking.html', context)


def travel_detail(request, travel_id):
    """Display travel option details"""
    travel = get_object_or_404(TravelOption, id=travel_id)
    context = {
        'travel': travel,
    }
    return render(request, 'booking/travel_detail.html', context)
