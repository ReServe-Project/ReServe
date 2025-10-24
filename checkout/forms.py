# checkout/forms.py

from django import forms
from .models import Booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        # List the fields you want the user to fill out
        fields = ['full_name', 'email', 'phone_number']