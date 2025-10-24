from __future__ import annotations

from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()

# --- Shared validators/constraints -------------------------------------------------

HANDLE_REGEX = r"^[a-z0-9_.]{3,20}$"
handle_validator = RegexValidator(
    regex=HANDLE_REGEX,
    message="Handle must be 3–20 chars, lowercase a–z, digits 0–9, underscore (_) or dot (.).",
)

phone_validator = RegexValidator(
    regex=r"^\+?[0-9]{6,20}$",
    message="Phone must be 6–20 digits, optional leading +.",
)

MAX_AVATAR_BYTES = 2 * 1024 * 1024  # 2 MB
ALLOWED_IMAGE_EXTS = {"jpg", "jpeg", "png", "webp"}


# --- Forms ------------------------------------------------------------------------

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "display_name",
            "bio",
            "gender",
            "phone",
            "birthdate",
            "location",
            # NEW:
            "height_cm",
            "weight_kg",
        ]
        widgets = {
            "birthdate": forms.DateInput(attrs={"type": "date"}),
        }

    # Existing validations
    def clean_display_name(self):
        name = (self.cleaned_data.get("display_name") or "").strip()
        if name and not (2 <= len(name) <= 50):
            raise ValidationError("Display name must be between 2 and 50 characters.")
        return name

    def clean_phone(self):
        phone = (self.cleaned_data.get("phone") or "").strip()
        if phone:
            phone_validator(phone)
        return phone

    def clean_birthdate(self):
        b = self.cleaned_data.get("birthdate")
        if b and b > timezone.now().date():
            raise ValidationError("Birthdate cannot be in the future.")
        return b

    # NEW:
    def clean_height_cm(self):
        h = self.cleaned_data.get("height_cm")
        if h is None:
            return h
        if not (80 <= h <= 250):
            raise ValidationError("Height must be between 80 and 250 cm.")
        return h

    def clean_weight_kg(self):
        w = self.cleaned_data.get("weight_kg")
        if w is None:
            return w
        if not (25 <= float(w) <= 300):
            raise ValidationError("Weight must be between 25 and 300 kg.")
        # Optional: normalize to 2 decimals
        return round(w, 2)


class HandleChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["handle"]

    def clean_handle(self):
        handle = (self.cleaned_data.get("handle") or "").strip().lower()
        handle_validator(handle)
        # Ensure uniqueness excluding current user
        qs = User.objects.filter(handle__iexact=handle)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("This handle is already taken.")
        return handle


class AvatarForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["avatar"]

    def clean_avatar(self):
        f = self.cleaned_data.get("avatar")
        if not f:
            return f
        # Size
        if hasattr(f, "size") and f.size > MAX_AVATAR_BYTES:
            raise ValidationError("Avatar file is too large (max 2 MB).")
        # Extension
        name = getattr(f, "name", "") or ""
        ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
        if ext not in ALLOWED_IMAGE_EXTS:
            raise ValidationError("Unsupported image type. Use JPG, PNG, or WebP.")
        return f


# --- Registration -----------------------------------------------------------------

class RegistrationForm(UserCreationForm):
    """Simple signup: username, email, password + display_name and role."""
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username", "email", "display_name", "role")

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()
        if not email:
            return email
        UserModel = get_user_model()
        if UserModel.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email