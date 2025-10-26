# checkout/urls.py

from django.urls import path
from . import views

app_name = 'checkout'

urlpatterns = [
    path('book/<int:class_id>/', views.checkout_view, name='checkout'),
    path('history/', views.booking_history_view, name='booking_history'),
    # Add this new path for deleting a booking
    path('delete/<int:booking_id>/', views.delete_booking, name='delete_booking'),
]