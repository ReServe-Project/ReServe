# checkout/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from home_search.models import Class  # <-- FIX 1: Import from the correct app
from .models import Booking
from .forms import BookingForm
from django.views.decorators.http import require_POST

@login_required
def checkout_view(request, class_id):
    # FIX 2: Use the correct model name 'Class'
    class_to_book = get_object_or_404(Class, pk=class_id)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            
            # --- Simplified Logic ---
            booking.user = request.user
            booking.class_booked = class_to_book
            booking.participants = 1  # Always 1 participant
            booking.total_price = class_to_book.price # Price is just the class price
            
            booking.save()
            
            # Use the correct attribute for the class name (it's .name)
            messages.success(request, f'Successfully booked {class_to_book.name}!')
            
            return redirect('checkout:booking_history')
    else:
        form = BookingForm()

    context = {
        'class': class_to_book,
        'form': form,
    }
    return render(request, 'checkout/checkout.html', context)


@login_required
def booking_history_view(request):
    # Get the status from the URL's query parameters (e.g., ?status=PAID)
    status_filter = request.GET.get('status')
    
    # Start with all bookings for the current user
    user_bookings = Booking.objects.filter(user=request.user)
    
    # If a valid status is provided, filter the bookings
    if status_filter in ['PENDING', 'PAID', 'CANCELLED']:
        user_bookings = user_bookings.filter(payment_status=status_filter)
        
    # Order the final list of bookings by date
    user_bookings = user_bookings.order_by('-booking_date')
    
    context = {
        'bookings': user_bookings,
        'current_filter': status_filter # Pass the current filter to the template
    }
    return render(request, 'checkout/booking_history.html', context)

@require_POST # Ensures this view can only be accessed with a POST request
@login_required
def delete_booking(request, booking_id):
    # Find the booking, ensuring it belongs to the current user
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    # Delete the booking from the database
    booking.delete()
    
    messages.success(request, 'Booking has been successfully deleted.')
    return redirect('checkout:booking_history')