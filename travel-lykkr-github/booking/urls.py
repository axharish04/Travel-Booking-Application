from django.urls import path
from . import views

urlpatterns = [
    path('', views.travel_list, name='travel_list'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('travel/<int:travel_id>/', views.travel_detail, name='travel_detail'),
    path('book/<int:travel_id>/', views.book_travel, name='book_travel'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('cancel-booking/<str:booking_id>/', views.cancel_booking, name='cancel_booking'),
]
