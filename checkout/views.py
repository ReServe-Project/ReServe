# checkout/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from home_search.models import Class
from .models import Booking
from .forms import BookingForm
from django.views.decorators.http import require_POST
from django.http import JsonResponse


@login_required
def checkout_view(request, class_id):
    class_to_book = get_object_or_404(Class, pk=class_id)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.class_booked = class_to_book
            booking.participants = 1
            booking.total_price = class_to_book.price
            booking.save()

            messages.success(request, f'Successfully booked {class_to_book.name}!')
            return redirect('checkout:booking_history')
    else:
        form = BookingForm()

    return render(request, 'checkout/checkout.html', {
        'class': class_to_book,
        'form': form,
    })


@login_required
def booking_history_view(request):
    status_filter = request.GET.get('status')
    user_bookings = Booking.objects.filter(user=request.user)

    if status_filter in ['PENDING', 'PAID', 'CANCELLED']:
        user_bookings = user_bookings.filter(payment_status=status_filter)

    user_bookings = user_bookings.order_by('-booking_date')

    return render(request, 'checkout/booking_history.html', {
        'bookings': user_bookings,
        'current_filter': status_filter,
    })

@login_required
def booking_history_api(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')

    data = []
    for b in bookings:
        data.append({
            "id": b.id,
            "class_name": b.class_booked.name,
            "full_name": b.full_name,
            "email": b.email,
            "phone_number": b.phone_number,
            "participants": b.participants,
            "total_price": float(b.total_price),
            "payment_status": b.payment_status,
            "booking_date": b.booking_date.isoformat(),
        })

    return JsonResponse({
        "success": True,
        "bookings": data
    })


@require_POST
@login_required
def delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    booking.delete()
    
    messages.success(request, 'Booking has been successfully deleted.')
    return redirect('checkout:booking_history')

@require_POST
@login_required
def delete_booking_api(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    booking.delete()

    return JsonResponse({
        "success": True,
        "message": "Booking deleted successfully"
    })



@login_required
def edit_booking_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    class_booked = booking.class_booked

    if request.method == "POST":
        import json
        try:
            data = json.loads(request.body)
        except:
            return JsonResponse({"success": False, "error": "Invalid JSON format."})

        form = BookingForm(data, instance=booking)

        if form.is_valid():
            form.save()
            return JsonResponse({
                "success": True,
                "message": "Booking updated successfully!"
            })
        else:
            return JsonResponse({
                "success": False,
                "error": "Invalid input. Please check your fields."
            })

    # GET request
    form = BookingForm(instance=booking)
    context = {
        "form": form,
        "booking": booking,
        "class": class_booked
    }
    return render(request, "checkout/edit_booking.html", context)
