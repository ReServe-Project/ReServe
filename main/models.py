from django.db import models

# Create your models here.

class User (models.Model):
    username = models.CharField(max_length=150, unique=True)
    
class PersonalGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    date = models.DateField()
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} ({'Done' if self.is_completed else 'Pending'})"

    