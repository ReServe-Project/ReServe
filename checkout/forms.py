from django import forms
from django.core.validators import RegexValidator
from .models import Booking

phone_validator = RegexValidator(regex=r'^\d{11}$', message='Phone number must be exactly 11 digits.')

class BookingForm(forms.ModelForm):
    phone_number = forms.CharField(
        max_length=11,
        validators=[phone_validator],
        widget=forms.TextInput(attrs={
            'placeholder': 'Ex: 81234567890',
            'inputmode': 'numeric',
            'pattern': r'\d{11}'
        })
    )

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

    def clean_phone_number(self):
        pn = self.cleaned_data.get('phone_number', '') or ''
        # remove non-digit characters (in case user types spaces/dashes)
        digits = ''.join(ch for ch in pn if ch.isdigit())
        if len(digits) != 11:
            raise forms.ValidationError('Phone number must contain exactly 11 digits.')
        return digits