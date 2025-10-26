# checkout/forms.py

from django import forms
from .models import Booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        # Only include the fields shown in the design
        fields = ['full_name', 'email', 'phone_number']