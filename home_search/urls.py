from django.urls import path
from . import views

app_name = "home_search"

urlpatterns = [
    # ----- Pages (existing) -----
    path("", views.home, name="home"),
    path("search/", views.search, name="search"),
    path("classes/create/", views.ClassCreateView.as_view(), name="class_create"),
    path("classes/<int:pk>/", views.ClassDetailView.as_view(), name="class_detail"),
    path("classes/<int:pk>/edit/", views.ClassUpdateView.as_view(), name="class_edit"),
    path("classes/<int:pk>/delete/", views.ClassDeleteView.as_view(), name="class_delete"),

    # ----- API (NEW for Flutter) -----
    path("api/classes/", views.api_classes_list, name="api_classes_list"),
    path("api/classes/<int:pk>/", views.api_class_detail, name="api_class_detail"),
    path("api/classes/create/", views.api_class_create, name="api_class_create"),
    path("api/classes/<int:pk>/update/", views.api_class_update, name="api_class_update"),
    path("api/classes/<int:pk>/delete/", views.api_class_delete, name="api_class_delete"),
    path("api/image-proxy/", views.api_image_proxy, name="api_image_proxy"),

]
