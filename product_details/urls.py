from django.urls import path
from . import views

app_name = "product_details"

urlpatterns = [
    path("classes/<int:pk>/add_review/", views.add_review, name="add_review"),
    path("classes/<int:pk>/reviews/fragment/", views.get_reviews_fragment, name="get_reviews_fragment"),
    path('classes/<int:pk>/delete_review/<int:review_id>/', views.delete_review, name='delete_review'),

]
