from django.urls import path
from . import views

app_name = 'checkout'

urlpatterns = [
    # -------- WEB --------
    path('book/<int:class_id>/', views.checkout_view, name='checkout'),
    path('history/', views.booking_history_view, name='booking_history'),
    path('delete/<int:booking_id>/', views.delete_booking, name='delete_booking'),
    path('edit/<int:booking_id>/', views.edit_booking_view, name='edit_booking'),

    # -------- API --------
    path("api/history/", views.booking_history_api),
    path("api/book/<int:class_id>/", views.checkout_api),
    path("api/delete/<int:booking_id>/", views.delete_booking_api),
    path("api/edit/<int:booking_id>/", views.edit_booking_api),

]
