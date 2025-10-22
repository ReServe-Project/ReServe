from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Add our custom fields to the admin detail page
    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "Profile",
            {
                "fields": (
                    "display_name",
                    "handle",
                    "role",
                    "bio",
                    "gender",
                    "phone",
                    "birthdate",
                    "location",
                    "avatar",
                )
            },
        ),
    )

    # What columns to show in the list
    list_display = (
        "username",
        "display_name",
        "handle",
        "role",
        "email",
        "is_staff",
        "date_joined",
    )
    list_filter = BaseUserAdmin.list_filter + ("role",)
    search_fields = ("username", "display_name", "handle", "email")
    ordering = ("-date_joined",)
