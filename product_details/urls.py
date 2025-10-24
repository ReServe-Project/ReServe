from django.urls import path
from . import views

app_name = 'product_details'

urlpatterns = [
    path('<int:pk>/', views.class_detail, name='class_detail'),
    path('<int:pk>/add_review/', views.add_review, name='add_review'),
    path('review/<int:review_id>/edit/', views.edit_review, name='edit_review'),
    path('review/<int:review_id>/delete/', views.delete_review, name='delete_review'),
]
