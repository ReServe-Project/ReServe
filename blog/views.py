from django.shortcuts import render, redirect, get_object_or_404
from blog.forms import BlogForm
from blog.models import Blog
from django.utils import timezone
from django.http import HttpResponse
from django.core import serializers
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def main_blog(request):
    filter_type = request.GET.get('filter', 'all') 
    if filter_type == 'my':
        blog_list = Blog.objects.filter(user=request.user)
    else:
        blog_list = Blog.objects.all()
    context = {
        'blog_list': blog_list,
        'filter_type': filter_type,
    }
    return render(request, "main_blog.html", context)

def create_blog(request):
    form = BlogForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.created_at = timezone.now().date()
            obj.save()
            return redirect('blog:main_blog')
    return render(request, "create_blog.html", {"form": form})

def blog_details(request, id):
    blog = get_object_or_404(Blog, pk=id)

    context = {
        'blog': blog
    }

    return render(request, "blog_details.html", context)

def show_xml(request):
    blog_list = Blog.objects.all()
    xml_data = serializers.serialize("xml", blog_list)
    return HttpResponse(xml_data, content_type="blog/xml")

def show_json(request):
    blog_list = Blog.objects.all()
    json_data = serializers.serialize("json", blog_list)
    return HttpResponse(json_data, content_type="blog/json")

def show_xml_by_id(request, blog_id):
    try:
        blog_item = Blog.objects.filter(pk=blog_id)
        xml_data = serializers.serialize("xml", blog_item)
        return HttpResponse(xml_data, content_type="blog/xml")
    except Blog.DoesNotExist:
        return HttpResponse(status=404)
    
def show_json_by_id(request, blog_id):
    try:
        blog_item = Blog.objects.get(pk=blog_id)
        json_data = serializers.serialize("json", [blog_item])
        return HttpResponse(json_data, content_type="application/json")
    except Blog.DoesNotExist:
        return HttpResponse(status=404)
    
@login_required
def edit_blog(request, id):
    blog = get_object_or_404(Blog, pk=id)
    if blog.user != request.user:
        messages.error(request, "You are not allowed to edit this blog.")
        return redirect('blog:main_blog')
    form = BlogForm(request.POST or None, instance=blog)
    if form.is_valid() and request.method == 'POST':
        form.save()
        print("Blog updated successfully")
        return redirect('blog:main_blog')
    return render(request, "edit_blog.html", {"form": form, "blog": blog})

@login_required
def delete_blog(request, id):
    blog = get_object_or_404(Blog, pk=id)
    if blog.user != request.user:
        messages.error(request, "You are not allowed to delete this blog.")
        return redirect('blog:main_blog')
    blog.delete()
    return redirect('blog:main_blog')
