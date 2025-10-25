from django.db import models
from accounts.models import User

CATEGORY_CHOICES = [
    ("yoga","Yoga"), ("pilates","Pilates"), ("dance","Dance"),
    ("boxing","Boxing"), ("muaythai","Muaythai"), ("ice-skating","Ice Skating"),
]

class Class(models.Model):
    owner       = models.ForeignKey(User, null=True, blank=True,
                                    on_delete=models.SET_NULL, related_name="my_classes")
    name        = models.CharField(max_length=200)
    category    = models.CharField(max_length=50, choices=CATEGORY_CHOICES, db_index=True)
    price       = models.IntegerField(default=0)
    image_url   = models.URLField(blank=True)
    description = models.TextField(blank=True)


    datetime   = models.DateTimeField(null=True, blank=True)
    location    = models.CharField(max_length=200, blank=True)

    def __str__(self): return self.name

    @property
    def hero_image(self) -> str:
        return self.image_url or ""






    