from __future__ import annotations

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import DetailView, UpdateView

from .forms import ProfileEditForm, AvatarForm, HandleChangeForm


User = get_user_model()


# -----------------------
# Private (owner) views
# -----------------------

class ProfileView(LoginRequiredMixin, DetailView):
    """Show the logged-in user's full profile (private fields included)."""
    model = User
    template_name = "accounts/profile_view.html"

    def get_object(self, queryset=None):
        return self.request.user


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """Edit display_name, bio, gender, phone, birthdate, location."""
    model = User
    form_class = ProfileEditForm
    template_name = "accounts/profile_edit.html"

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        form.save()
        return redirect(reverse("profile_view"))


class AvatarUpdateView(LoginRequiredMixin, View):
    """
    Accept avatar updates via normal POST or AJAX (multipart/form-data).
    Returns JSON on AJAX; redirects on normal POST.
    """
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        user = request.user
        form = AvatarForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                # return new avatar url
                return JsonResponse({"success": True, "avatar_url": user.avatar.url})
            return redirect(reverse("profile_view"))
        else:
            errors = form.errors.get_json_data()
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"success": False, "errors": errors}, status=400)
            # For non-AJAX, just show edit page with errors
            return redirect(reverse("profile_edit"))


# -----------------------
# Public view
# -----------------------

class PublicProfileView(DetailView):
    """Public profile by handle (no private fields)."""
    model = User
    template_name = "accounts/public_profile.html"
    slug_field = "handle"
    slug_url_kwarg = "handle"


# -----------------------
# AJAX endpoints
# -----------------------

@require_GET
def validate_handle(request: HttpRequest) -> JsonResponse:
    """
    Check if a handle is available.
    GET /profile/ajax/validate-handle/?handle=foo
    """
    handle = (request.GET.get("handle") or "").strip().lower()
    if not handle:
        return JsonResponse({"valid": False, "error": "No handle provided."}, status=400)

    # Use the same validation as the form
    temp_form = HandleChangeForm(data={"handle": handle}, instance=request.user if request.user.is_authenticated else None)
    if temp_form.is_valid():
        return JsonResponse({"valid": True})
    else:
        # If only error is "already taken", valid=False; otherwise return first error
        return JsonResponse({"valid": False, "errors": temp_form.errors.get_json_data()}, status=400)


class UpdatePhoneAjax(LoginRequiredMixin, View):
    """
    Update phone via AJAX.
    POST /profile/ajax/update-phone/  (form-data: phone=+62812...)
    """
    def post(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        phone = (request.POST.get("phone") or "").strip()
        # Reuse ProfileEditForm validation for phone field
        form = ProfileEditForm({"display_name": request.user.display_name, "phone": phone}, instance=request.user)
        if form.is_valid():
            request.user.phone = form.cleaned_data["phone"]
            request.user.save(update_fields=["phone"])
            return JsonResponse({"success": True, "phone": request.user.phone})
        return JsonResponse({"success": False, "errors": form.errors.get_json_data()}, status=400)
