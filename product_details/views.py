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

def is_flutter_request(request):
    """Check if request is from Flutter app"""
    user_agent = request.headers.get('User-Agent', '').lower()
    has_flutter_header = request.headers.get('X-Request-Source') == 'flutter'
    is_json_content = request.content_type == 'application/json'
    
    return has_flutter_header or 'flutter' in user_agent or is_json_content

@login_required
def add_review(request, pk):
    class_item = get_object_or_404(Class, id=pk)

    if request.method == "POST":
        from_flutter = is_flutter_request(request)
        
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                rating = data.get("rating")
                comment = data.get("comment", "")
            except json.JSONDecodeError:
                if from_flutter:
                    return JsonResponse({"error": "Invalid JSON format"}, status=400)
                else:
                    return HttpResponseBadRequest("Invalid JSON format")
        else:
            rating = request.POST.get("rating")
            comment = request.POST.get("comment", "")

        if not rating:
            if from_flutter:
                return JsonResponse({"error": "Rating is required"}, status=400)
            else:
                return HttpResponseBadRequest("Rating is required")

        try:
            rating = int(rating)
            if rating < 1 or rating > 3:
                error_msg = "Rating must be between 1 and 3"
                if from_flutter:
                    return JsonResponse({"error": error_msg}, status=400)
                else:
                    return HttpResponseBadRequest(error_msg)
        except ValueError:
            error_msg = "Rating must be a number"
            if from_flutter:
                return JsonResponse({"error": error_msg}, status=400)
            else:
                return HttpResponseBadRequest(error_msg)

        review, created = Review.objects.update_or_create(
            class_item=class_item,
            user=request.user,
            defaults={
                "rating": rating,
                "comment": comment.strip()
            }
        )

        avg_rating = Review.objects.filter(class_item=class_item).aggregate(
            avg=Avg("rating")
        )["avg"] or 0
        class_item.average_rating = round(avg_rating, 1)
        class_item.save()

        if from_flutter:
            return JsonResponse({
                "success": True,
                "message": "Review submitted successfully",
                "review": {
                    "id": review.id,
                    "rating": review.rating,
                    "comment": review.comment,
                    "user": request.user.username,
                    "created_at": review.created_at.isoformat() if hasattr(review, 'created_at') else None
                }
            })
        elif is_ajax(request):
            html = render_to_string("_reviews_list.html", {
                "c": class_item,
                "user": request.user
            })
            return JsonResponse({
                "success": True,
                "html": html,
                "user_review_data": {
                    "id": review.id,
                    "rating": review.rating,
                    "comment": review.comment
                }
            })
        else:
            return render(request, "reviews/reviews.html", {"c": class_item})

    if is_flutter_request(request):
        return JsonResponse({"error": "POST method required"}, status=405)
    elif is_ajax(request):
        return JsonResponse({"error": "POST method required"}, status=405)
    else:
        return HttpResponseForbidden("Invalid request method")

@login_required
def delete_review(request, pk, review_id):
    review = get_object_or_404(Review, id=review_id, class_item_id=pk)

    if review.user != request.user:
        if is_flutter_request(request):
            return JsonResponse({"error": "You can only delete your own review."}, status=403)
        else:
            return HttpResponseForbidden("You can only delete your own review.")

    if request.method == "POST":
        from_flutter = is_flutter_request(request)
        
        review.delete()
        class_item = get_object_or_404(Class, id=pk)

        avg_rating = Review.objects.filter(class_item=class_item).aggregate(
            avg=Avg("rating")
        )["avg"] or 0
        class_item.average_rating = round(avg_rating, 1)
        class_item.save()

        if from_flutter:
            return JsonResponse({
                "success": True,
                "message": "Review deleted successfully"
            })
        elif is_ajax(request):
            html = render_to_string("_reviews_list.html", {
                "c": class_item,
                "user": request.user
            })
            return HttpResponse(html)
        else:
            return render(request, "reviews/reviews.html", {"c": class_item})

    if is_flutter_request(request):
        return JsonResponse({"error": "Invalid request"}, status=400)
    else:
        return HttpResponseBadRequest("Invalid request")

def get_reviews_fragment(request, pk):
    class_item = get_object_or_404(Class, id=pk)
    avg_rating = Review.objects.filter(class_item=class_item).aggregate(
        avg=Avg("rating")
    )["avg"] or 0
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
