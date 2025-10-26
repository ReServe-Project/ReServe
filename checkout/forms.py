from django import forms
from .models import Booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        # These are the fields from your model
        fields = ['full_name', 'email', 'phone_number'] 
        
        # This part adds the CSS class to each field
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Enter your full name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'user@gmail.com'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Ex: 81234567890'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # This loop adds your new CSS class to all fields
        for field_name in self.fields:
            self.fields[field_name].widget.attrs['class'] = 'form-control'