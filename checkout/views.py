# checkout/views.py
# checkout/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from home_search.models import Class
from .models import Booking
from .forms import BookingForm

import json


# =====================================================
# WEB VIEWS (CSRF PROTECTED)
# =====================================================

@login_required
def checkout_view(request, class_id):
    class_to_book = get_object_or_404(Class, pk=class_id)

    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.class_booked = class_to_book
            booking.participants = 1
            booking.total_price = class_to_book.price
            booking.save()

            messages.success(
                request, f"Successfully booked {class_to_book.name}!"
            )
            return redirect("checkout:booking_history")

        messages.error(request, "Please fix the errors below.")

    else:
        form = BookingForm()

    return render(
        request,
        "checkout/checkout.html",
        {"class": class_to_book, "form": form},
    )


@login_required
def booking_history_view(request):
    bookings = (
        Booking.objects
        .filter(user=request.user)
        .order_by("-booking_date")
    )

    return render(
        request,
        "checkout/booking_history.html",
        {"bookings": bookings},
    )


@login_required
@require_POST
def delete_booking(request, booking_id):
    booking = get_object_or_404(
        Booking, id=booking_id, user=request.user
    )
    booking.delete()

    messages.success(request, "Booking deleted successfully.")
    return redirect("checkout:booking_history")


@login_required
def edit_booking_view(request, booking_id):
    booking = get_object_or_404(
        Booking, id=booking_id, user=request.user
    )

    if request.method == "POST":
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            messages.success(request, "Booking updated successfully.")
            return redirect("checkout:booking_history")

        messages.error(request, "Please fix the errors below.")
    else:
        form = BookingForm(instance=booking)

    return render(
        request,
        "checkout/edit_booking.html",
        {
            "form": form,
            "booking": booking,
            "class": booking.class_booked,
        },
    )


# =====================================================
# API VIEWS (CSRF EXEMPT – FOR FLUTTER WEB / MOBILE)
# =====================================================

@login_required
def booking_history_api(request):
    bookings = (
        Booking.objects
        .filter(user=request.user)
        .order_by("-booking_date")
    )

    return JsonResponse({
        "success": True,
        "bookings": [
            {
                "id": b.id,
                "class_id": b.class_booked.id, 
                "class_name": b.class_booked.name,
                "full_name": b.full_name,
                "email": b.email,
                "phone_number": b.phone_number,
                "participants": b.participants,
                "total_price": float(b.total_price),
                "payment_status": b.payment_status,
                "booking_date": b.booking_date.isoformat(),
            }
            for b in bookings
        ],
    })


@csrf_exempt
@login_required
@require_POST
def checkout_api(request, class_id):
    class_to_book = get_object_or_404(Class, pk=class_id)

    try:
        data = json.loads(request.body.decode())
    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "error": "Invalid JSON"},
            status=400,
        )

    full_name = data.get("full_name")
    email = data.get("email")
    phone_number = data.get("phone_number")

    if not all([full_name, email, phone_number]):
        return JsonResponse(
            {"success": False, "error": "Missing fields"},
            status=400,
        )

    booking = Booking.objects.create(
        user=request.user,
        class_booked=class_to_book,
        full_name=full_name,
        email=email,
        phone_number=phone_number,
        participants=1,
        total_price=class_to_book.price,
    )

    return JsonResponse(
        {
            "success": True,
            "booking": {
                "id": booking.id,
                "class_name": booking.class_booked.name,
                "total_price": float(booking.total_price),
                "payment_status": booking.payment_status,
                "booking_date": booking.booking_date.isoformat(),
            },
        },
        status=201,
    )


@csrf_exempt
@login_required
@require_POST
def delete_booking_api(request, booking_id):
    booking = get_object_or_404(
        Booking, id=booking_id, user=request.user
    )
    booking.delete()

    return JsonResponse({"success": True})


@csrf_exempt
@login_required
@require_POST
def edit_booking_api(request, booking_id):
    booking = get_object_or_404(
        Booking, id=booking_id, user=request.user
    )

    try:
        data = json.loads(request.body.decode())
    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "error": "Invalid JSON"},
            status=400,
        )

    form = BookingForm(data, instance=booking)
    if form.is_valid():
        form.save()
        return JsonResponse({"success": True})

    return JsonResponse(
        {
            "success": False,
            "error": "Invalid data",
            "details": form.errors,
        },
        status=400,
    )
