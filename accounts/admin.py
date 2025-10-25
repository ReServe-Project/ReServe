# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile', {
            'fields': (
                'display_name', 'handle', 'role', 'avatar',
                'height_cm', 'weight_kg',
            )
        }),
    )

    list_display = (
        'username', 'display_name', 'handle', 'role', 'email',
        'height_cm', 'weight_kg',
        'is_staff', 'date_joined',
    )

    list_filter = BaseUserAdmin.list_filter + ('role',)
    search_fields = ('username', 'display_name', 'handle', 'email')
