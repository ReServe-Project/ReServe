from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.decorators.http import require_GET
from django.views.generic import DetailView, UpdateView, CreateView

from accounts.models import User

from .forms import ProfileEditForm, AvatarForm, HandleChangeForm, RegistrationForm

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
    """Edit display_name, bio, gender, phone, birthdate, location, height, weight."""
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
                return JsonResponse({"success": True, "avatar_url": user.avatar.url})
            return redirect(reverse("profile_view"))
        errors = form.errors.get_json_data()
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"success": False, "errors": errors}, status=400)
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

    temp_form = HandleChangeForm(
        data={"handle": handle},
        instance=request.user if request.user.is_authenticated else None,
    )
    if temp_form.is_valid():
        return JsonResponse({"valid": True})
    return JsonResponse({"valid": False, "errors": temp_form.errors.get_json_data()}, status=400)


class UpdatePhoneAjax(LoginRequiredMixin, View):
    """
    Update phone via AJAX.
    POST /profile/ajax/update-phone/  (form-data: phone=+62812...)
    """
    def post(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        phone = (request.POST.get("phone") or "").strip()
        form = ProfileEditForm(
            {"display_name": request.user.display_name, "phone": phone},
            instance=request.user,
        )
        if form.is_valid():
            request.user.phone = form.cleaned_data["phone"]
            request.user.save(update_fields=["phone"])
            return JsonResponse({"success": True, "phone": request.user.phone})
        return JsonResponse({"success": False, "errors": form.errors.get_json_data()}, status=400)

# -----------------------
# Auth views
# -----------------------

class AuthLoginView(LoginView):
    template_name = "registration/login.html"  # LOGIN_REDIRECT_URL -> post_login


class AuthLogoutView(LogoutView):
    next_page = "login"


class RegisterView(CreateView):
    form_class = RegistrationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("login")

@login_required
def post_login(request: HttpRequest):
    """
    Smart redirect after login:
    If profile is incomplete (missing height or weight), go to edit (onboarding),
    else go to private profile view.
    """
    u = request.user
    if not getattr(u, "height_cm", None) or not getattr(u, "weight_kg", None):
        return redirect("profile_edit")
    return redirect("profile_view")
