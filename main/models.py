from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

class PersonalGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    date = models.DateField()
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date", "id"]
        indexes = [
            models.Index(fields=["user", "date"]),
        ]
    def __str__(self):
        return f"{self.title} ({self.date})"

    

