from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from home_search.models import Class  # import your friend's Class model
from accounts.models import User
from django.db.models import Avg

class Review(models.Model):
    class_item = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='class_reviews')
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['class_item', 'user']

    def __str__(self):
        return f"Review by {self.user} on {self.class_item.name}"

    @property
    def stars(self):
        return "★" * self.rating + "☆" * (3 - self.rating)
    
    @staticmethod
    def get_average_for_class(class_instance):
        result = Review.objects.filter(class_item=class_instance).aggregate(avg=Avg("rating"))
        return round(result["avg"] or 0, 1)

