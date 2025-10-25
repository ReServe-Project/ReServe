from django.urls import path
from . import views

app_name = "home_search"

urlpatterns = [
    path("", views.home, name="home"),
    path("search/", views.search, name="search"),
    path("classes/create/", views.ClassCreateView.as_view(), name="class_create"),
    path("classes/<int:pk>/", views.ClassDetailView.as_view(), name="class_detail"),
    path("classes/<int:pk>/edit/", views.ClassUpdateView.as_view(), name="class_edit"),
    path("classes/<int:pk>/delete/", views.ClassDeleteView.as_view(), name="class_delete"),
]
