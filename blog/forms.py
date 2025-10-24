from django import forms
from .models import Blogs

class BlogForm(forms.ModelForm):
    class Meta:
        model = Blogs
        fields = ['title', 'date_blog', 'description', 'thumbnail']
        widgets = {
            'date_blog': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 5}),
        }
