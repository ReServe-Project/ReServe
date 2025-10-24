# Django admin configuration for the custom User model.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from accounts.models import User



@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile', {
            'fields': (
                'display_name', 'handle', 'role', 'bio', 'gender', 'phone',
                'birthdate', 'location', 'avatar',
                # NEW:
                'height_cm', 'weight_kg',
            )
        }),
    )

    list_display = (
        'username', 'display_name', 'handle', 'role', 'email',
        # NEW:
        'height_cm', 'weight_kg',
        'is_staff', 'date_joined',
    )

    list_filter = BaseUserAdmin.list_filter + ('role',)

    search_fields = ('username', 'display_name', 'handle', 'email')