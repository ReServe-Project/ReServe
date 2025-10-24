from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import ClassDetails, Review

def class_detail(request, class_id):
    """Display class details and reviews"""
    class_details = get_object_or_404(ClassDetails, id=class_id)
    reviews = class_details.reviews.all().order_by('-created_at')
    
    user_review = None
    if request.user.is_authenticated:
        user_review = Review.objects.filter(class_details=class_details, user=request.user).first()
    
    return render(request, 'product_details/class_detail.html', {
        'class_details': class_details,
        'reviews': reviews,
        'user_review': user_review,
        'can_review': request.user.is_authenticated and not user_review
    })

@login_required
def book_class(request, class_id):
    """Book a class"""
    class_details = get_object_or_404(ClassDetails, id=class_id)
    
    request.session['booking_info'] = {
        'class_id': class_details.id,
        'class_name': class_details.class_name,
        'instructor': class_details.instructor.display_name,
        'price': str(class_details.price),
        'location': class_details.location,
    }
    
    return redirect('checkout:checkout_page')

@login_required
def add_review(request, class_id):
    """CREATE review"""
    class_details = get_object_or_404(ClassDetails, id=class_id)
    
    if Review.objects.filter(class_details=class_details, user=request.user).exists():
        return redirect('product_details:class_detail', class_id=class_id)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '')
        
        if rating:
            Review.objects.create(
                class_details=class_details,
                user=request.user,
                rating=int(rating),
                comment=comment
            )
    
    return redirect('product_details:class_detail', class_id=class_id)

@login_required
def update_review(request, review_id):
    """UPDATE review"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '')
        
        if rating:
            review.rating = int(rating)
            review.comment = comment
            review.save()
    
    return redirect('product_details:class_detail', class_id=review.class_details.id)

@login_required
def delete_review(request, review_id):
    """DELETE review"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    class_id = review.class_details.id
    review.delete()
    return redirect('product_details:class_detail', class_id=class_id)