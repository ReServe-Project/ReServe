# blog/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django import forms
from .models import Blogs

class BlogForm(forms.ModelForm):
    class Meta:
        model = Blogs
        fields = ["title", "date_blog", "description", "thumbnail"]
        widgets = {"date_blog": forms.DateInput(attrs={"type": "date"}),
                   "description": forms.Textarea(attrs={"rows": 4})}

def show_blog(request):
    blogs = Blogs.objects.order_by("-date_blog", "-time_blog")
    return render(request, "show_blog.html", {"blogs": blogs})

@login_required
def create_blog(request):
    if request.method == "POST":
        form = BlogForm(request.POST)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.creator = request.user          # <-- fix IntegrityError
            blog.save()
            return redirect("blog:show_blog")
    else:
        form = BlogForm()
    return render(request, "blog_form.html", {"form": form, "mode": "create"})

@login_required
def edit_blog(request, pk):
    blog = get_object_or_404(Blogs, pk=pk, creator=request.user)  # optional ownership check
    if request.method == "POST":
        form = BlogForm(request.POST, instance=blog)
        if form.is_valid():
            form.save()
            return redirect("blog:show_blog")
    else:
        form = BlogForm(instance=blog)
    return render(request, "blog_form.html", {"form": form, "mode": "edit", "blog": blog})

@login_required
def delete_blog(request, pk):
    blog = get_object_or_404(Blogs, pk=pk, creator=request.user)  # optional ownership check
    if request.method == "POST":
        blog.delete()
        return redirect("blog:show_blog")
    return render(request, "confirm_delete.html", {"blog": blog})
