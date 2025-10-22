from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


# --- Validators --------------------------------------------------------------

HANDLE_REGEX = r"^[a-z0-9_.]{3,20}$"
handle_validator = RegexValidator(
    regex=HANDLE_REGEX,
    message="Handle must be 3–20 chars, lowercase a–z, digits 0–9, underscore (_) or dot (.).",
)

phone_validator = RegexValidator(
    regex=r"^\+?[0-9]{6,20}$",
    message="Phone must be 6–20 digits, optional leading +.",
)


def validate_birthdate_not_future(value):
    if value and value > timezone.now().date():
        raise ValidationError("Birthdate cannot be in the future.")


# --- Utilities ---------------------------------------------------------------

def _unique_handle_for(base: str, max_len: int = 30) -> str:
    """
    Generate a unique slug/handle from a base string within max_len.
    Appends -2, -3, ... if needed.
    """
    from django.contrib.auth import get_user_model

    base_slug = slugify(base)[:max_len] or "user"
    User = get_user_model()

    # If available, use it
    if not User.objects.filter(handle=base_slug).exists():
        return base_slug

    # Else append a counter
    i = 2
    while True:
        candidate = f"{base_slug[: max_len - (len(str(i)) + 1)]}-{i}"
        if not User.objects.filter(handle=candidate).exists():
            return candidate
        i += 1


# --- Custom User -------------------------------------------------------------

class User(AbstractUser):
    MEMBER = "member"
    INSTRUCTOR = "instructor"
    ROLE_CHOICES = (
        (MEMBER, "Member"),
        (INSTRUCTOR, "Instructor"),
    )

    # Extra profile fields
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=MEMBER)
    display_name = models.CharField(max_length=50, blank=True, help_text="Public display name.")
    handle = models.SlugField(
        max_length=30,
        unique=True,
        help_text="Unique handle used in profile URLs, e.g., @john_doe",
        validators=[handle_validator],
    )
    bio = models.TextField(blank=True)
    gender = models.CharField(max_length=10, blank=True)
    phone = models.CharField(max_length=20, blank=True, validators=[phone_validator])
    birthdate = models.DateField(null=True, blank=True, validators=[validate_birthdate_not_future])
    location = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        default="avatars/default.png",
        help_text="JPEG/PNG/WebP up to ~2MB.",
    )

    def clean(self):
        super().clean()
        # Re-run validators explicitly for safety when saving via admin/forms
        if self.handle:
            handle_validator(self.handle)
        if self.phone:
            phone_validator(self.phone)
        if self.birthdate:
            validate_birthdate_not_future(self.birthdate)

    def save(self, *args, **kwargs):
        # Auto-populate display_name if empty
        if not self.display_name:
            self.display_name = self.get_full_name().strip() or self.username

        # If no handle set, generate a unique one from display_name/username
        if not self.handle:
            base = self.display_name or self.username or "user"
            self.handle = _unique_handle_for(base, max_len=30)

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        dn = self.display_name or self.username
        return f"{dn} (@{self.handle})"
