from django.forms import ModelForm
from blog.models import Blog

class BlogForm(ModelForm):
    class Meta:
        model = Blog
        fields = ["title", "content", "thumbnail"]  