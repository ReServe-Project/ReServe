from __future__ import annotations

from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils import timezone


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
    """
    For editing the **owner's** profile fields (non-credential stuff).
    Intentionally excludes username/email/password/handle; handle edit is a separate flow.
    """
    class Meta:
        model = User
        fields = ["display_name", "bio", "gender", "phone", "birthdate", "location"]
        widgets = {
            "birthdate": forms.DateInput(attrs={"type": "date"}),
        }

    def clean_display_name(self):
        name = (self.cleaned_data.get("display_name") or "").strip()
        if len(name) < 2 or len(name) > 50:
            raise ValidationError("Display name must be between 2 and 50 characters.")
        return name

    def clean_phone(self):
        phone = (self.cleaned_data.get("phone") or "").strip()
        if phone:
            phone_validator(phone)
        return phone

    def clean_birthdate(self):
        bd = self.cleaned_data.get("birthdate")
        if bd and bd > timezone.now().date():
            raise ValidationError("Birthdate cannot be in the future.")
        return bd


class HandleChangeForm(forms.ModelForm):
    """
    Separate form just to change the handle with proper uniqueness + regex validation.
    Use this if later you want a dedicated 'Change handle' UI or AJAX validator.
    """
    class Meta:
        model = User
        fields = ["handle"]

    def clean_handle(self):
        handle = (self.cleaned_data.get("handle") or "").strip().lower()
        handle_validator(handle)

        # Uniqueness check that allows the current user to keep their handle
        qs = User.objects.filter(handle=handle)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("That handle is already taken.")
        return handle


class AvatarForm(forms.ModelForm):
    """
    Minimal form to update avatar with:
    - extension whitelist (jpg/jpeg/png/webp)
    - size limit (2 MB)
    """
    class Meta:
        model = User
        fields = ["avatar"]

    def clean_avatar(self):
        f = self.cleaned_data.get("avatar")
        if not f:
            return f

        # File size
        if getattr(f, "size", 0) > MAX_AVATAR_BYTES:
            raise ValidationError("Image too large (max 2 MB).")

        # Extension check
        name = (getattr(f, "name", "") or "").lower()
        ext = name.rsplit(".", 1)[-1] if "." in name else ""
        if ext not in ALLOWED_IMAGE_EXTS:
            raise ValidationError("Unsupported image type. Use JPG, JPEG, PNG, or WEBP.")
        return f
