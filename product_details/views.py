from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse, HttpResponseBadRequest, HttpResponse
from django.template.loader import render_to_string
from django.db.models import Avg
from home_search.models import Class
from .models import Review
import json

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

@login_required
def add_review(request, pk):
    class_item = get_object_or_404(Class, id=pk)

    if request.method == "POST":
        # Handle both form data and JSON
        if request.content_type == 'application/json':
            # Flutter sends JSON
            data = json.loads(request.body)
            rating = data.get("rating")
            comment = data.get("comment")
        else:
            # Web sends form data
            rating = request.POST.get("rating")
            comment = request.POST.get("comment")

        if not rating:
            return JsonResponse({"error": "Rating is required"}, status=400)

        # Create or update the user's review
        review, created = Review.objects.update_or_create(
            class_item=class_item,
            user=request.user,
            defaults={"rating": rating, "comment": comment}
        )

        # Recalculate average rating dynamically
        avg_rating = Review.objects.filter(class_item=class_item).aggregate(avg=Avg("rating"))["avg"] or 0
        class_item.average_rating = round(avg_rating, 1)
        class_item.save()

        # Check if request is from Flutter (JSON) or Web (AJAX)
        if request.content_type == 'application/json' or is_ajax(request):
            # Return JSON for Flutter/AJAX
            return JsonResponse({
                "success": True,
                "html": render_to_string("_reviews_list.html", {"c": class_item, "user": request.user}),
                "user_review_data": {
                    "id": review.id,
                    "rating": review.rating,
                    "comment": review.comment
                }
            })
        else:
            # For regular web form submission
            return render(request, "reviews/reviews.html", {"c": class_item})

    return HttpResponseForbidden("Invalid request method")

@login_required
def delete_review(request, pk, review_id):
    review = get_object_or_404(Review, id=review_id, class_item_id=pk)

    if review.user != request.user:
        return HttpResponseForbidden("You can only delete your own review.")

    if request.method == "POST":
        review.delete()
        class_item = get_object_or_404(Class, id=pk)

        # Recalculate average after deletion
        avg_rating = Review.objects.filter(class_item=class_item).aggregate(avg=Avg("rating"))["avg"] or 0
        avg_rating = round(avg_rating, 1)
        class_item.average_rating = avg_rating
        class_item.save()

        # Check if request is from Flutter or Web
        if is_ajax(request) or request.content_type == 'application/json':
            # Return HTML fragment for AJAX or JSON for Flutter
            html = render_to_string("_reviews_list.html", {"c": class_item, "user": request.user})
            if request.content_type == 'application/json':
                return JsonResponse({"success": True, "html": html})
            return HttpResponse(html)
        else:
            return render(request, "reviews/reviews.html", {"c": class_item})

    return HttpResponseBadRequest("Invalid request")

def get_reviews_fragment(request, pk):
    """Used by AJAX to reload the review list without reloading the page"""
    class_item = get_object_or_404(Class, id=pk)

    avg_rating = Review.objects.filter(class_item=class_item).aggregate(avg=Avg("rating"))["avg"] or 0
    class_item.average_rating = round(avg_rating, 1)

    return render(request, "_reviews_list.html", {"c": class_item})

def reviews_json(request, pk):
    reviews = Review.objects.filter(class_item_id=pk).select_related("user")

    data = [
        {
            "id": r.id,
            "user": r.user.username,
            "rating": r.rating,
            "comment": r.comment,
            "created_at": r.created_at.isoformat(),
        }
        for r in reviews
    ]

    return JsonResponse(data, safe=False)
