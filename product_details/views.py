from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ClassDetails, Review

def class_detail(request, class_id):
    class_details = get_object_or_404(ClassDetails, id=class_id)
    reviews = class_details.reviews.all().order_by('-created_at')
    
    # Check if user has already reviewed this class
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
    class_details = get_object_or_404(ClassDetails, id=class_id)
    
    request.session['booking_info'] = {
        'class_id': class_details.id,
        'class_name': class_details.class_name,
        'instructor': class_details.instructor.display_name,
        'price': str(class_details.price),
        'location': class_details.location,
    }
    
    messages.success(request, f"Ready to book {class_details.class_name}!")
    return redirect('checkout:checkout_page')

@login_required
def add_review(request, class_id):
    class_details = get_object_or_404(ClassDetails, id=class_id)
    
    # Check if user already reviewed this class
    if Review.objects.filter(class_details=class_details, user=request.user).exists():
        messages.error(request, "You have already reviewed this class.")
        return redirect('product_details:class_detail', class_id=class_id)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '')
        
        if rating:
            # Create the review
            Review.objects.create(
                class_details=class_details,
                user=request.user,
                rating=int(rating),
                comment=comment
            )
            messages.success(request, "Thank you for your review!")
        else:
            messages.error(request, "Please select a rating!")
    
    return redirect('product_details:class_detail', class_id=class_id)