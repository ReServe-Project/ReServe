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
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator

from .forms import (
    ProfileCardEditForm as ProfileEditForm,  # slim form (display_name, height, weight)
    AvatarForm,
    RegistrationForm,
)

# -----------------------
# Private (owner) views
# -----------------------

class ProfileView(LoginRequiredMixin, DetailView):
    """Show the logged-in user's profile (card view)."""
    model = User
    template_name = "accounts/profile_view.html"

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        """
        Inject the slim edit form + avatar form so the modal can render
        without a separate page.
        """
        ctx = super().get_context_data(**kwargs)
        u = self.request.user
        ctx["edit_form"] = ProfileEditForm(instance=u)
        ctx["avatar_form"] = AvatarForm(instance=u)
        return ctx


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """
    Edit only the fields used by the new UI:
    display_name, height_cm, weight_kg (avatar handled separately).
    """
    model = User
    form_class = ProfileEditForm
    template_name = "accounts/profile_edit.html"  # keeps fallback page if needed

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


@method_decorator(csrf_protect, name="dispatch")
class ProfileUpdateAjax(LoginRequiredMixin, View):
    def post(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        user = request.user
        form = ProfileEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return JsonResponse({
                "success": True,
                "updated": {
                    "display_name": user.display_name or user.username,
                    "height_cm": user.height_cm,
                    "weight_kg": float(user.weight_kg) if user.weight_kg is not None else None,
                }
            })
        return JsonResponse({"success": False, "errors": form.errors.get_json_data()}, status=400)

# -----------------------
# Public view
# -----------------------

class PublicProfileView(DetailView):
    """
    Public profile by handle (legacy). Kept temporarily to avoid breaking links.
    Currently visually identical to the private card per product decision.
    """
    model = User
    template_name = "accounts/public_profile.html"
    slug_field = "handle"
    slug_url_kwarg = "handle"

# -----------------------
# Deprecated AJAX endpoints (kept as safe stubs)
# -----------------------

@require_GET
def validate_handle(request: HttpRequest) -> JsonResponse:
    """
    Deprecated: handle is no longer editable/required in the new UI.
    Keeping a stub to avoid 404 if old JS still calls it while we refactor.
    """
    return JsonResponse({"valid": False, "error": "Handle validation is deprecated."}, status=410)


class UpdatePhoneAjax(LoginRequiredMixin, View):
    """
    Deprecated: phone is no longer part of the profile.
    Kept as a 410 stub to avoid breaking old calls during the transition.
    """
    def post(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        return JsonResponse({"success": False, "error": "Phone update is deprecated."}, status=410)

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
    After login, always go to the profile page.
    (User can open the edit modal from the button on that page.)
    """
    return redirect("profile_view")
