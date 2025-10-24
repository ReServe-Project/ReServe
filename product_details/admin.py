from django.contrib import admin
from .models import Class, Review

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'location', 'display_datetime')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('class_session', 'user', 'rating', 'created_at')
