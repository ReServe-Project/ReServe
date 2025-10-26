from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

class ClassDetails(models.Model):
    CATEGORY_CHOICES = [
        ('yoga', 'Yoga'),
        ('pilates', 'Pilates'),
        ('dance', 'Dance'),
        ('muay_thai', 'Muay Thai'),
        ('boxing', 'Boxing'),
        ('ice_skating', 'Ice Skating'),
    ]
    
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    class_name = models.CharField(max_length=200)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='classes_teaching')
    date_time = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='class_images/', null=True, blank=True)
    
    def get_schedule_display(self):
        if self.date_time:
            return self.date_time.strftime("%Y-%m-%d %H:%M")
        return "Schedule not set"
    
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum(review.rating for review in reviews) / len(reviews), 1)
        return 0
    
    def review_count(self):
        return self.reviews.count()
    
    def __str__(self):
        return self.class_name

class Review(models.Model):
    class_details = models.ForeignKey(ClassDetails, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='class_reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(3)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['class_details', 'user']
    
    def __str__(self):
        return f"Review #{self.id}"