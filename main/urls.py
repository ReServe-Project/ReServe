from django.urls import path, include
from main.views import register, login_user, logout_user, show_main

app_name = 'main'

urlpatterns = [
    path("", show_main, name="show_main"),

]
