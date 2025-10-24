from django.db import models
from django.conf import settings
from django.utils import timezone

User = settings.AUTH_USER_MODEL


class Class(models.Model):
    title = models.CharField(max_length=100)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='instructed_classes')
    location = models.CharField(max_length=100)
    date_time = models.DateTimeField(null=True, blank=True, help_text="Leave blank if by appointment")
    description = models.TextField()
    image = models.ImageField(upload_to='class_images/', blank=True, null=True)

    def display_datetime(self):
        if not self.date_time:
            return "By Appointment"
        return self.date_time.strftime("%d %b %Y, %H:%M")

    def average_rating(self):
        avg = self.reviews.aggregate(models.Avg('rating'))['rating__avg']
        return round(avg or 0, 1)

    def __str__(self):
        return self.title


class Review(models.Model):
    class_session = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='class_reviews')
    rating = models.PositiveSmallIntegerField(default=3)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.class_session.title}"
