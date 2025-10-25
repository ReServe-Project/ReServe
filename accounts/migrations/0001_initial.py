from __future__ import annotations

from django.db import migrations, models
import django.utils.timezone
import django.contrib.auth.models


class Migration(migrations.Migration):

    initial = True

    # Keep auth dependency so Group/Permission tables exist first
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
                ("is_superuser", models.BooleanField(default=False, help_text="Designates that this user has all permissions without explicitly assigning them.", verbose_name="superuser status")),
                ("username", models.CharField(
                    max_length=150,
                    unique=True,
                    verbose_name="username",
                    help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
                    error_messages={"unique": "A user with that username already exists."},
                )),
                ("first_name", models.CharField(blank=True, max_length=150, verbose_name="first name")),
                ("last_name", models.CharField(blank=True, max_length=150, verbose_name="last name")),
                ("email", models.EmailField(blank=True, max_length=254, verbose_name="email address")),
                ("is_staff", models.BooleanField(default=False, help_text="Designates whether the user can log into this admin site.", verbose_name="staff status")),
                ("is_active", models.BooleanField(default=True, help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.", verbose_name="active")),
                ("date_joined", models.DateTimeField(default=django.utils.timezone.now, verbose_name="date joined")),

                # ---- Your custom fields (final schema) ----
                ("role", models.CharField(max_length=20, choices=[("member", "Member"), ("instructor", "Instructor")], default="member")),
                ("display_name", models.CharField(max_length=50)),
                ("handle", models.SlugField(max_length=30, unique=True, help_text="3–20 chars: a–z, 0–9, underscore, dot")),
                ("avatar", models.ImageField(upload_to="avatars/", blank=True, default="avatars/default.png")),
                ("height_cm", models.PositiveSmallIntegerField(null=True, blank=True, help_text="User height in centimeters (80–250).")),
                ("weight_kg", models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="User weight in kilograms (25.00–300.00).")),

                # Groups / permissions (same as AbstractUser)
                ("groups", models.ManyToManyField(
                    to="auth.group",
                    blank=True,
                    related_name="user_set",
                    related_query_name="user",
                    verbose_name="groups",
                    help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                )),
                ("user_permissions", models.ManyToManyField(
                    to="auth.permission",
                    blank=True,
                    related_name="user_set",
                    related_query_name="user",
                    verbose_name="user permissions",
                    help_text="Specific permissions for this user.",
                )),
            ],
            options={
                "verbose_name": "user",
                "verbose_name_plural": "users",
                # Important: this marks the model as swappable (custom user)
                "swappable": "AUTH_USER_MODEL",
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
