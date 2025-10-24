# blog/urls.py
from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    path("", views.show_blog, name="show_blog"),
    path("create/", views.create_blog, name="create_blog"),
    path("<uuid:pk>/edit/", views.edit_blog, name="edit_blog"),
    path("<uuid:pk>/delete/", views.delete_blog, name="delete_blog"),
]
