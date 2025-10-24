# accounts/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # AUTH
    path("login/", views.AuthLoginView.as_view(), name="login"),
    path("logout/", views.AuthLogoutView.as_view(), name="logout"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("post-login/", views.post_login, name="post_login"),

    # PRIVATE PROFILE
    path("profile/", views.ProfileView.as_view(), name="profile_view"),
    path("profile/edit/", views.ProfileEditView.as_view(), name="profile_edit"),
    path("profile/avatar/", views.AvatarUpdateView.as_view(), name="profile_avatar_update"),

    # PUBLIC PROFILE
    path("u/<slug:handle>/", views.PublicProfileView.as_view(), name="public_profile"),

    # AJAX
    path("profile/ajax/validate-handle/", views.validate_handle, name="ajax_validate_handle"),
    path("profile/ajax/update-phone/", views.UpdatePhoneAjax.as_view(), name="ajax_update_phone"),
]