from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 3, 'class': 'border rounded p-1'}),
            'comment': forms.Textarea(attrs={'rows': 3, 'class': 'w-full border rounded p-2'}),
        }
