# blog/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid

class Blogs(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    date_blog = models.DateField(default=timezone.now)
    time_blog = models.TimeField(auto_now_add=True)
    description = models.TextField()
    thumbnail = models.URLField(blank=True, null=True)
    creator = models.ForeignKey(   # <- this is the column your DB already has
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="blogs",
    )

    def __str__(self):
        return self.title
