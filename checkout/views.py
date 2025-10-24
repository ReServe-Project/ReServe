# checkout/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from product_details.models import ClassDetails
from .models import Booking

# This decorator ensures that only logged-in users can access this page
@login_required
def checkout_view(request, class_id):
    # Get the specific class the user wants to book, or show a 404 error if it doesn't exist
    class_to_book = get_object_or_404(ClassDetails, pk=class_id)
    
    # This is where you would handle the form submission with POST
    if request.method == 'POST':
        # (We will add the booking logic here in the next step)
        # For now, let's just imagine it's successful
        # After booking, redirect to the history page
        return redirect('checkout:booking_history')

    # For a GET request, just display the checkout page with the class details
    context = {
        'class': class_to_book,
    }
    return render(request, 'checkout.html', context)


@login_required
def booking_history_view(request):
    # Get all the bookings made by the current user and order them by date
    user_bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
    
    context = {
        'bookings': user_bookings,
    }
    return render(request, 'booking_history.html', context)

