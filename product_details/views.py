from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Class, Review
from .forms import ReviewForm


def class_detail(request, pk):
    class_obj = get_object_or_404(Class, pk=pk)
    reviews = class_obj.reviews.select_related('user')
    form = ReviewForm()

    return render(request, 'product_details/class_detail.html', {
        'class_obj': class_obj,
        'reviews': reviews,
        'form': form,
    })


@login_required
def add_review(request, pk):
    class_obj = get_object_or_404(Class, pk=pk)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.class_session = class_obj
            review.save()
    return redirect('product_details:class_detail', pk=pk)


@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id, user=request.user)
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('product_details:class_detail', pk=review.class_session.pk)
    else:
        form = ReviewForm(instance=review)
    return render(request, 'product_details/review_modal.html', {'form': form, 'review': review})


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id, user=request.user)
    class_pk = review.class_session.pk
    review.delete()
    return redirect('product_details:class_detail', pk=class_pk)

