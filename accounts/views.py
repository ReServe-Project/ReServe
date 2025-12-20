from __future__ import annotations

from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import DetailView, UpdateView, CreateView
from django.utils.decorators import method_decorator

from accounts.models import User
from .forms import (
    ProfileCardEditForm as ProfileEditForm,
    AvatarForm,
    RegistrationForm,
)

# --- Constants ---------------------------------------------------------------

ALLOWED_ROLES = {"member", "instructor"}


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
    template_name = "registration/login.html"


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
    """
    return redirect("profile_view")


# -----------------------
# Flutter API endpoints
# -----------------------

@csrf_exempt
@require_POST
def api_register(request: HttpRequest) -> JsonResponse:
    """
    JSON registration endpoint for Flutter.
    """
    data = request.POST.copy()

    # --- Role handling ---
    role = data.get("role", "").strip()
    if not role:
        return JsonResponse({
            "status": False,
            "message": "Registration failed.",
            "errors": ["role: This field is required."]
        }, status=400)

    # Validate role against model choices (single source of truth)
    allowed_roles = {choice[0] for choice in User.ROLE_CHOICES}
    if role not in allowed_roles:
        return JsonResponse({
            "status": False,
            "message": "Registration failed.",
            "errors": ["role: Invalid role."]
        }, status=400)

    # Inject role into form data
    data["role"] = role

    # --- Form validation ---
    form = RegistrationForm(data)
    if form.is_valid():
        user = form.save(commit=False)

        # Safety: ensure role is set even if form Meta excludes it
        user.role = role
        user.save()

        return JsonResponse({
            "status": True,
            "message": "Registration successful."
        })

    # --- Error formatting (Flutter-friendly) ---
    errors = []
    for field, field_errors in form.errors.items():
        for err in field_errors:
            if field == "__all__":
                errors.append(str(err))
            else:
                errors.append(f"{field}: {err}")

    return JsonResponse({
        "status": False,
        "message": "Registration failed.",
        "errors": errors,
    }, status=400)

@csrf_exempt
def api_login(request: HttpRequest) -> JsonResponse:
    """
    JSON login endpoint for Flutter (session-cookie based).
    Compatible with pbp_django_auth CookieRequest.login().

    Expects POST: username, password
    Returns JSON: {status: bool, message: str, ...}
    """
    if request.method != "POST":
        return JsonResponse({"status": False, "message": "Only POST is allowed."}, status=405)

    username = request.POST.get("username", "")
    password = request.POST.get("password", "")

    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({
            "status": False,
            "success": False,
            "logged_in": False,
            "message": "Invalid username or password.",
            "detail": "Invalid username or password.",
        }, status=401)

    auth_login(request, user)
    return JsonResponse({
        "status": True,
        "success": True,
        "logged_in": True,
        "message": "Login successful.",
        "detail": "Login successful.",
        "username": user.username,
        "handle": getattr(user, "handle", None),
        "role": getattr(user, "role", None),
    })


@csrf_exempt
def api_logout(request: HttpRequest) -> JsonResponse:
    """
    JSON logout endpoint for Flutter.
    Compatible with pbp_django_auth CookieRequest.logout().
    """
    if request.method != "POST":
        return JsonResponse({"status": False, "message": "Only POST is allowed."}, status=405)

    auth_logout(request)
    return JsonResponse({"status": True, "message": "Logged out."})


def _profile_json(user: User) -> dict:
    """
    Convert the User object into JSON-safe dict for Flutter.
    """
    avatar_url = None
    try:
        if user.avatar:
            avatar_url = user.avatar.url
    except Exception:
        avatar_url = None

    return {
        "rs_id": getattr(user, "reserve_id", None),
        "username": user.username,
        "display_name": getattr(user, "display_name", None) or user.username,
        "handle": getattr(user, "handle", None),
        "role": getattr(user, "role", None),
        "height_cm": getattr(user, "height_cm", None),
        "weight_kg": float(user.weight_kg) if getattr(user, "weight_kg", None) is not None else None,
        "last_login": user.last_login.isoformat() if user.last_login else None,
        "avatar_url": avatar_url,
    }


@require_GET
@login_required
def api_profile(request: HttpRequest) -> JsonResponse:
    """
    Get current logged-in user's profile in JSON.
    """
    user = request.user
    return JsonResponse({
        "status": True,
        "profile": _profile_json(user),
    })


@csrf_exempt
@require_POST
@login_required
def api_profile_update(request: HttpRequest) -> JsonResponse:
    if not request.user.is_authenticated:
        return JsonResponse(
            {"status": False, "message": "Not logged in."},
            status=401
        )

    form = ProfileEditForm(request.POST, instance=request.user)
    if form.is_valid():
        user = form.save()
        return JsonResponse({
            "status": True,
            "message": "Profile updated.",
            "profile": {
                "rs_id": getattr(user, "rs_id", None),
                "username": user.username,
                "display_name": user.display_name or user.username,
                "handle": user.handle,
                "role": user.role,
                "height_cm": user.height_cm,
                "weight_kg": float(user.weight_kg) if user.weight_kg is not None else None,
                "last_login": user.last_login.isoformat() if user.last_login else None,
            }
        })

    # field-level errors
    errors = {}
    for field, errs in form.errors.get_json_data().items():
        errors[field] = [e["message"] for e in errs]

    return JsonResponse({
        "status": False,
        "message": "Validation failed.",
        "errors": errors,
    }, status=400)

@csrf_exempt
@require_POST
@login_required
def api_profile_avatar(request: HttpRequest) -> JsonResponse:
    """
    Update avatar image (multipart/form-data).
    Uses existing AvatarForm to keep behavior consistent with web.
    """
    user = request.user
    form = AvatarForm(request.POST, request.FILES, instance=user)
    if form.is_valid():
        form.save()
        return JsonResponse({
            "status": True,
            "message": "Avatar updated.",
            "profile": _profile_json(user),
        })
    return JsonResponse({
        "status": False,
        "message": "Invalid avatar upload.",
        "errors": form.errors.get_json_data(),
    }, status=400)