from django.contrib import admin
from .models import ClassDetails, Review

@admin.register(ClassDetails)
class ClassDetailsAdmin(admin.ModelAdmin):
    list_display = ['class_name', 'category', 'instructor', 'price']
    list_filter = ['category']
    search_fields = ['class_name', 'instructor__username']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['class_details', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['class_details__class_name', 'user__username']
