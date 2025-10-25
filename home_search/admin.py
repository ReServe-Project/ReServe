from django.contrib import admin
from .models import Class

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "price", "owner", "image_url")
    list_filter = ("category", "owner")
    search_fields = ("name",)

