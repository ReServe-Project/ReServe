from django.db import models
from django.conf import settings

# Create your models here.

class PersonalGoal(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="personal_goals",
    )
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


class Blog(models.Model):
    title = models.CharField(max_length=200)
    date_blog = models.DateField()
    time_blog = models.TimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    