# Django admin configuration for the custom User model
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from accounts.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile', {
            'fields': (
                'display_name', 'handle', 'role', 'birthdate', 'location', 'avatar',
                'height_cm', 'weight_kg',
            ),
        }),
    )
