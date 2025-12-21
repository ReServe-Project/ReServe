from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse, HttpResponseBadRequest, HttpResponse
from django.template.loader import render_to_string
from django.db.models import Avg
from home_search.models import Class
from .models import Review

@login_required
def add_review(request, pk):
    class_item = get_object_or_404(Class, id=pk)

    if request.method == "POST":
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

        # Render the updated reviews list
        html = render_to_string("_reviews_list.html", {"c": class_item, "user": request.user})

        # Return JSON with HTML and user review data
        return JsonResponse({
            "html": html,
            "user_review_data": {
                "id": review.id,
                "rating": review.rating,
                "comment": review.comment
            }
        })

    return HttpResponseForbidden("Invalid request method")



@login_required
def delete_review(request, pk, review_id):
    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
        review = get_object_or_404(Review, id=review_id, class_item_id=pk)

        if review.user != request.user:
            return HttpResponseForbidden("You can only delete your own review.")

        review.delete()
        class_item = get_object_or_404(Class, id=pk)

        # Recalculate average after deletion
        avg_rating = Review.objects.filter(class_item=class_item).aggregate(avg=Avg("rating"))["avg"] or 0
        avg_rating = round(avg_rating, 1)
        class_item.average_rating = avg_rating

        html = render_to_string("_reviews_list.html", {"c": class_item, "user": request.user})
        return HttpResponse(html)

    return HttpResponseBadRequest("Invalid request")


def get_reviews_fragment(request, pk):
    """Used by AJAX to reload the review list without reloading the page"""
    class_item = get_object_or_404(Class, id=pk)

    avg_rating = Review.objects.filter(class_item=class_item).aggregate(avg=Avg("rating"))["avg"] or 0
    class_item.average_rating = round(avg_rating, 1)

    return render(request, "_reviews_list.html", {"c": class_item})

from django.http import JsonResponse
from .models import Review

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
