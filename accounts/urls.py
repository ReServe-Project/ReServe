from django.urls import path
from . import views

urlpatterns = [
    # owner (private) pages
    path("profile/", views.ProfileView.as_view(), name="profile_view"),
    path("profile/edit/", views.ProfileEditView.as_view(), name="profile_edit"),
    path("profile/avatar/", views.AvatarUpdateView.as_view(), name="profile_avatar_update"),

    # public profile
    path("u/<slug:handle>/", views.PublicProfileView.as_view(), name="public_profile"),

    # AJAX endpoints
    path("profile/ajax/validate-handle/", views.validate_handle, name="ajax_validate_handle"),
    path("profile/ajax/update-phone/", views.UpdatePhoneAjax.as_view(), name="ajax_update_phone"),
]
