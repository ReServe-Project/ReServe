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

def _unique_handle_for(base: str, max_len: int = 30, instance_pk=None) -> str:
    """
    Build a unique handle from base, truncated to max_len, using _N suffix if needed.
    """
    root = slugify(base or "user").replace("-", "_")
    root = root[:max_len] or "user"
    handle = root
    i = 1
    # Late reference to User is fine; function is called after class definition exists.
    while User.objects.filter(handle=handle).exclude(pk=instance_pk).exists():
        suffix = f"_{i}"
        handle = f"{root[: max_len - len(suffix)]}{suffix}"
        i += 1
    return handle


# --- Model -------------------------------------------------------------------

class User(AbstractUser):
    ROLE_CHOICES = [('member', 'Member'), ('instructor', 'Instructor')]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    display_name = models.CharField(max_length=50)
    handle = models.SlugField(
        max_length=30,
        unique=True,
        help_text="3–20 chars: a–z, 0–9, underscore, dot",
    )
    bio = models.TextField(blank=True)
    gender = models.CharField(max_length=10, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    birthdate = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, default='avatars/default.png')

    # NEW: physical attributes
    height_cm = models.PositiveSmallIntegerField(
        null=True, blank=True, help_text="User height in centimeters (80–250)."
    )
    weight_kg = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text="User weight in kilograms (25.00–300.00)."
    )

    # validators (kept for reference/usage)
    handle_validator = RegexValidator(regex=HANDLE_REGEX, message="Handle must be 3–20 chars (a–z, 0–9, _ or .)")
    phone_validator = phone_validator

    def clean(self):
        super().clean()
        # existing validators you already had...
        if self.handle:
            handle_validator(self.handle)
        if self.phone:
            phone_validator(self.phone)
        if self.birthdate:
            validate_birthdate_not_future(self.birthdate)

        # NEW: sanity ranges (only if provided)
        if self.height_cm is not None:
            if not (80 <= self.height_cm <= 250):
                raise ValidationError({"height_cm": "Height must be between 80 and 250 cm."})

        if self.weight_kg is not None:
            # Convert Decimal to float safely for comparison
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
