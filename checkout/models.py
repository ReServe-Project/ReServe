# checkout/models.py

from django.db import models
from django.contrib.auth.models import User
from product_details.models import ClassDetails 

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    class_booked = models.ForeignKey(ClassDetails, on_delete=models.CASCADE)

    # --- Add these new fields ---
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    # --- End of new fields ---

    participants = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('CANCELLED', 'Cancelled'),
    ]
    payment_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    booking_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Booking for {self.class_booked.class_name} by {self.user.username}'