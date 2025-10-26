from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from .models import ClassDetails, Review


def class_detail(request, class_id):
    """Display class details and reviews"""
    class_details = get_object_or_404(ClassDetails, id=class_id)
    reviews = class_details.reviews.select_related('user').all().order_by('-created_at')

    user_review = None
    if request.user.is_authenticated:
        user_review = Review.objects.filter(class_details=class_details, user=request.user).first()

    context = {
        'class_details': class_details,
        'reviews': reviews,
        'user_review': user_review,
        'can_review': request.user.is_authenticated and not user_review,
    }
    return render(request, 'product_details/product_details.html', context)


@login_required
@require_POST
def book_class(request, class_id):
    """Book a class - redirects to checkout"""
    class_details = get_object_or_404(ClassDetails, id=class_id)
    
    # ✅ Booking logic preserved
    request.session['booking_info'] = {
        'class_id': class_details.id,
        'class_name': class_details.class_name,
        'instructor': class_details.instructor.get_full_name() or class_details.instructor.username,
        'price': str(class_details.price),
        'location': class_details.location,
        'schedule': class_details.get_schedule_display(),
        'category': class_details.get_category_display(),
    }
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'Proceeding to checkout...',
            'redirect_url': 'checkout:checkout_page'
        })
    
    messages.success(request, "Proceeding to checkout...")
    return redirect('checkout:checkout_page')


@login_required
@require_POST
def add_review(request, class_id):
    """CREATE review via AJAX (or fallback)"""
    class_details = get_object_or_404(ClassDetails, id=class_id)

    # Prevent duplicate reviews by same user
    if Review.objects.filter(class_details=class_details, user=request.user).exists():
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'You have already reviewed this class!'}, status=400)
        messages.error(request, "You have already reviewed this class!")
        return redirect('product_details:class_detail', class_id=class_id)

    rating = request.POST.get('rating')
    comment = request.POST.get('comment', '').strip()

    try:
        rating_int = int(rating)
    except (TypeError, ValueError):
        rating_int = None

    if rating_int and 1 <= rating_int <= 3:
        Review.objects.create(
            class_details=class_details,
            user=request.user,
            rating=rating_int,
            comment=comment
        )

        # ✅ Corrected file name: _reviews_list.html
        reviews = class_details.reviews.select_related('user').all().order_by('-created_at')
        reviews_html = render_to_string('product_details/_reviews_list.html', {
            'class_details': class_details,
            'reviews': reviews,
            'user': request.user,
            'can_review': False,
        }, request=request)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Thank you for your review!',
                'reviews_html': reviews_html,
                'average_rating': class_details.average_rating(),
                'review_count': class_details.review_count()
            })

        messages.success(request, "Thank you for your review!")
        return redirect('product_details:class_detail', class_id=class_id)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'message': 'Please provide a valid rating.'}, status=400)
    messages.error(request, "Please provide a valid rating.")
    return redirect('product_details:class_detail', class_id=class_id)


@login_required
@require_POST
def update_review(request, review_id):
    """UPDATE review via AJAX (or fallback)"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    class_details = review.class_details

    rating = request.POST.get('rating')
    comment = request.POST.get('comment', '').strip()

    try:
        rating_int = int(rating)
    except (TypeError, ValueError):
        rating_int = None

    if rating_int and 1 <= rating_int <= 3:
        review.rating = rating_int
        review.comment = comment
        review.save()

        reviews = class_details.reviews.select_related('user').all().order_by('-created_at')
        reviews_html = render_to_string('product_details/_reviews_list.html', {
            'class_details': class_details,
            'reviews': reviews,
            'user': request.user,
            'can_review': False,
        }, request=request)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Review updated successfully!',
                'reviews_html': reviews_html,
                'average_rating': class_details.average_rating(),
                'review_count': class_details.review_count()
            })

        messages.success(request, "Review updated successfully!")
        return redirect('product_details:class_detail', class_id=class_details.id)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'message': 'Please provide a valid rating.'}, status=400)
    messages.error(request, "Please provide a valid rating.")
    return redirect('product_details:class_detail', class_id=class_details.id)


@login_required
@require_POST
def delete_review(request, review_id):
    """DELETE review via AJAX (or fallback)"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    class_details = review.class_details
    review.delete()

    reviews = class_details.reviews.select_related('user').all().order_by('-created_at')
    reviews_html = render_to_string('product_details/_reviews_list.html', {
        'class_details': class_details,
        'reviews': reviews,
        'user': request.user,
        'can_review': True,
    }, request=request)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'Review deleted successfully!',
            'reviews_html': reviews_html,
            'average_rating': class_details.average_rating(),
            'review_count': class_details.review_count()
        })

    messages.success(request, "Review deleted successfully!")
    return redirect('product_details:class_detail', class_id=class_details.id)


def get_reviews_fragment(request, class_id):
    """Return rendered reviews HTML fragment for AJAX updates"""
    class_details = get_object_or_404(ClassDetails, id=class_id)
    reviews = class_details.reviews.select_related('user').all().order_by('-created_at')

    user_review = None
    if request.user.is_authenticated:
        user_review = Review.objects.filter(class_details=class_details, user=request.user).first()

    reviews_html = render_to_string('product_details/_reviews_list.html', {
        'class_details': class_details,
        'reviews': reviews,
        'user': request.user,
        'user_review': user_review,
        'can_review': request.user.is_authenticated and not user_review,
    }, request=request)

    return JsonResponse({
        'success': True,
        'reviews_html': reviews_html,
        'average_rating': class_details.average_rating(),
        'review_count': class_details.review_count()
    })
