from __future__ import annotations

from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm

from accounts.models import User

# --- Constraints used by Avatar upload -------------------------------------------------

MAX_AVATAR_BYTES = 2 * 1024 * 1024  # 2 MB
ALLOWED_IMAGE_EXTS = {"jpg", "jpeg", "png", "webp"}


# --- Profile (slim) --------------------------------------------------------------------

class ProfileCardEditForm(forms.ModelForm):
    """
    Minimal profile form for the new card/modal UX.
    Only what the UI needs: display_name, height_cm, weight_kg.
    """
    class Meta:
        model = User
        fields = ["display_name", "height_cm", "weight_kg"]
        widgets = {
            "display_name": forms.TextInput(attrs={"placeholder": "Your name"}),
            "height_cm": forms.NumberInput(attrs={"min": 80, "max": 260, "step": 1}),
            "weight_kg": forms.NumberInput(attrs={"min": 20, "max": 400, "step": 1}),
        }

    def clean_display_name(self):
        name = (self.cleaned_data.get("display_name") or "").strip()
        if name and not (2 <= len(name) <= 50):
            raise ValidationError("Display name must be between 2 and 50 characters.")
        return name

    def clean_height_cm(self):
        v = self.cleaned_data.get("height_cm")
        if v is None:
            return v
        if not (80 <= v <= 260):
            raise ValidationError("Please enter a realistic height (80–260 cm).")
        return v

    def clean_weight_kg(self):
        v = self.cleaned_data.get("weight_kg")
        if v is None:
            return v
        try:
            f = float(v)
        except (TypeError, ValueError):
            raise ValidationError("Invalid weight.")
        if not (20.0 <= f <= 400.0):
            raise ValidationError("Please enter a realistic weight (20–400 kg).")
        # normalize to 2 decimals if Decimal
        return round(f, 2)


# Backward-compat alias so existing imports/views keep working
ProfileEditForm = ProfileCardEditForm


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


# --- Registration ---------------------------------------------------------------------

class RegistrationForm(UserCreationForm):
    """Signup with username + role + password1/password2. display_name mirrors username."""
    role = forms.ChoiceField(choices=User.ROLE_CHOICES)

    class Meta(UserCreationForm.Meta):
        model = User
        # UserCreationForm supplies password1/password2 automatically
        fields = ("username", "role")

    def save(self, commit=True):
        user: User = super().save(commit=False)
        # mirror username into display_name
        user.display_name = self.cleaned_data["username"]
        user.role = self.cleaned_data["role"]
        if commit:
            user.save()
        return user
