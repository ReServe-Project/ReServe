# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

HANDLE_REGEX = r"^[a-z0-9_.]{3,20}$"
handle_validator = RegexValidator(
    regex=HANDLE_REGEX,
    message="Handle must be 3–20 chars, lowercase a–z, digits 0–9, underscore (_) or dot (.).",
)

def validate_birthdate_not_future(value):
    """
    Kept for historical migrations compatibility (0001_initial).
    """
    if value and value > timezone.now().date():
        raise ValidationError("Birthdate cannot be in the future.")

def _unique_handle_for(base: str, max_len: int = 30, instance_pk=None) -> str:
    root = slugify(base or "user").replace("-", "_")
    root = root[:max_len] or "user"
    handle = root
    i = 1
    while User.objects.filter(handle=handle).exclude(pk=instance_pk).exists():
        suffix = f"_{i}"
        handle = f"{root[: max_len - len(suffix)]}{suffix}"
        i += 1
    return handle


class User(AbstractUser):
    ROLE_CHOICES = [
        ("member", "Member"),
        ("instructor", "Instructor"),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="member")
    display_name = models.CharField(max_length=50)
    handle = models.SlugField(
        max_length=30,
        unique=True,
        help_text="3–20 chars: a–z, 0–9, underscore, dot",
    )
    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        default="avatars/default.png",
    )

    # Physical attributes only
    height_cm = models.PositiveSmallIntegerField(
        null=True, blank=True, help_text="User height in centimeters (80–250)."
    )
    weight_kg = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text="User weight in kilograms (25.00–300.00)."
    )

    def clean(self):
        super().clean()
        if self.handle:
            handle_validator(self.handle)

        if self.height_cm is not None and not (80 <= self.height_cm <= 250):
            raise ValidationError({"height_cm": "Height must be between 80 and 250 cm."})

        if self.weight_kg is not None:
            w = float(self.weight_kg)
            if not (25.0 <= w <= 300.0):
                raise ValidationError({"weight_kg": "Weight must be between 25 and 300 kg."})

    def save(self, *args, **kwargs):
        if not self.handle:
            base = self.display_name or self.username or "user"
            self.handle = _unique_handle_for(base, max_len=30, instance_pk=self.pk)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.display_name or self.username} (@{self.handle})"

    @property
    def reserve_id(self) -> str:
        if self.pk:
            return f"RS-{self.pk:06d}"
        return "RS-000000"

    @property
    def display_label(self) -> str:
        return (self.display_name or "").strip() or self.username
