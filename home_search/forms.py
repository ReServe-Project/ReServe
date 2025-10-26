from django import forms
from .models import Class

# HTML datetime-local expects "YYYY-MM-DDTHH:MM"
DT_FORMAT = "%Y-%m-%dT%H:%M"

class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ["category", "name", "price", "description", "image_url", "datetime", "location"]
        widgets = {
            "datetime": forms.DateTimeInput(attrs={"type": "datetime-local"}, format=DT_FORMAT),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-fill datetime-local value when editing
        if self.instance and self.instance.pk and self.instance.datetime:
            self.initial["datetime"] = self.instance.datetime.strftime(DT_FORMAT)

