# checkout/models.py

from django.db import models
# FIX 1: Import your custom User model, not the default one
from accounts.models import User 
# FIX 2: Import the 'Class' model from 'home_search', not 'product_details'
from home_search.models import Class 

class Booking(models.Model):
    # FIX 3: Point to the correct User model
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # FIX 4: Point to the correct Class model (it was Class, not ClassDetails)
    class_booked = models.ForeignKey(Class, on_delete=models.CASCADE)

    # --- Add these new fields ---
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.IntegerField()
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
        # FIX 5: Your Class model uses '.name' (based on your Review model's __str__)
        return f'Booking for {self.class_booked.name} by {self.user.username}'