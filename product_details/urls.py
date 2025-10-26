from django.urls import path
from . import views

app_name = "product_details"

urlpatterns = [
    path("class/<int:class_id>/", views.class_detail, name="class_detail"),
    path("class/<int:class_id>/book/", views.book_class, name="book_class"),
    path("class/<int:class_id>/review/add/", views.add_review, name="add_review"),
    path("review/<int:review_id>/update/", views.update_review, name="update_review"),
    path("review/<int:review_id>/delete/", views.delete_review, name="delete_review"),
    path("class/<int:class_id>/reviews/fragment/", views.get_reviews_fragment, name="get_reviews_fragment"),
]
