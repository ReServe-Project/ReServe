# accounts/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # AUTH
    path("login/", views.AuthLoginView.as_view(), name="login"),
    path("logout/", views.AuthLogoutView.as_view(), name="logout"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("post-login/", views.post_login, name="post_login"),

    path("api/register/", views.api_register, name="api_register"),
    path("api/login/", views.api_login, name="api_login"),
    path("api/logout/", views.api_logout, name="api_logout"),

    # PROFILE API (for Flutter)
    path("api/profile/", views.api_profile, name="api_profile"),
    path("api/profile/update/", views.api_profile_update, name="api_profile_update"),
    path("api/profile/avatar/", views.api_profile_avatar, name="api_profile_avatar"),

    # PRIVATE PROFILE
    path("profile/", views.ProfileView.as_view(), name="profile_view"),
    path("profile/edit/", views.ProfileEditView.as_view(), name="profile_edit"),
    path("profile/avatar/", views.AvatarUpdateView.as_view(), name="profile_avatar_update"),
    path("profile/update/", views.ProfileUpdateAjax.as_view(), name="profile_update_ajax"),

    # PUBLIC PROFILE
    path("u/<slug:handle>/", views.PublicProfileView.as_view(), name="public_profile"),

    # LEGACY AJAX (temporary stubs)
    path("profile/ajax/validate-handle/", views.validate_handle, name="ajax_validate_handle"),
    path("profile/ajax/update-phone/", views.UpdatePhoneAjax.as_view(), name="ajax_update_phone"),
]
