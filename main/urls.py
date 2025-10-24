from django.urls import path, include
from main.views import register, login_user, logout_user
app_name = 'main'
urlpatterns = [
    path('register/', register, name='register'),
    path('', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
]
