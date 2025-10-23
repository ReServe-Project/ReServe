from django.db import models
from django.contrib.auth import get_user_model

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
    
    # only instructors can be assigned
    instructor = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='classes_teaching'
    )
    
    is_by_appointment = models.BooleanField(default=False)
    date_time = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.class_name