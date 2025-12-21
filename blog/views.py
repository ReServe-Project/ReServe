from django.shortcuts import render, redirect, get_object_or_404
from blog.forms import BlogForm
from blog.models import Blog
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

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


# API Views for Mobile App
def _blog_to_dict(blog):
    """Convert a Blog model instance to a dictionary for JSON response."""
    return {
        'id': str(blog.id),
        'title': blog.title,
        'content': blog.content,
        'thumbnail': blog.thumbnail,
        'user': blog.user.username,
        'created_at': blog.created_at.isoformat(),
    }


@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_blogs(request):
    """API endpoint to get all blogs or create a new blog."""
    if request.method == 'GET':
        blogs = Blog.objects.all().order_by('-created_at')
        blog_list = [_blog_to_dict(blog) for blog in blogs]
        return JsonResponse(blog_list, safe=False)
    
    elif request.method == 'POST':
        # DEBUG: Log request details
        import sys
        print(f"\n=== DEBUG api_blogs POST ===", file=sys.stderr)
        print(f"request.user: {request.user}", file=sys.stderr)
        print(f"request.user.is_authenticated: {request.user.is_authenticated}", file=sys.stderr)
        print(f"request.session.session_key: {request.session.session_key}", file=sys.stderr)
        print(f"request.COOKIES: {request.COOKIES}", file=sys.stderr)
        print(f"request.META.get('HTTP_COOKIE'): {request.META.get('HTTP_COOKIE')}", file=sys.stderr)
        print(f"request.META.get('HTTP_AUTHORIZATION'): {request.META.get('HTTP_AUTHORIZATION')}", file=sys.stderr)
        print(f"request.POST: {request.POST}", file=sys.stderr)
        print(f"=== END DEBUG ===\n", file=sys.stderr)
        
        # Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return JsonResponse({
                'error': 'Authentication required',
                'user_is_authenticated': False if request.user else None,
            }, status=401)
        
        try:
            # Handle both JSON and form data (pbp_django_auth sends form data)
            content_type = request.META.get('CONTENT_TYPE', '')
            if 'application/json' in content_type:
                data = json.loads(request.body) if request.body else {}
            else:
                # Form data from pbp_django_auth or regular form submission
                data = request.POST.dict()
            
            blog = Blog.objects.create(
                user=request.user,
                title=data.get('title'),
                content=data.get('content'),
                thumbnail=data.get('thumbnail', ''),
            )
            return JsonResponse(_blog_to_dict(blog), status=201)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def api_blog_detail(request, blog_id):
    """API endpoint to get, update, or delete a specific blog."""
    try:
        blog = Blog.objects.get(pk=blog_id)
    except Blog.DoesNotExist:
        return JsonResponse({'error': 'Blog not found'}, status=404)
    
    # Check for method override in JSON body
    method = request.method
    request_data = {}
    
    try:
        if request.method in ['PUT', 'POST']:
            # Handle both JSON and form data
            content_type = request.META.get('CONTENT_TYPE', '')
            if 'application/json' in content_type:
                request_data = json.loads(request.body) if request.body else {}
            else:
                # Form data from pbp_django_auth
                request_data = request.POST.dict()
            
            if request_data.get('_method') == 'DELETE':
                method = 'DELETE'
    except (json.JSONDecodeError, ValueError):
        # If JSON parsing fails, try form data
        request_data = request.POST.dict()
        if request_data.get('_method') == 'DELETE':
            method = 'DELETE'
    
    if request.method == 'GET':
        return JsonResponse(_blog_to_dict(blog))
    
    elif request.method in ['PUT', 'POST'] and method != 'DELETE':
        if not request.user or not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        if blog.user != request.user:
            return JsonResponse({'error': 'Not authorized to edit this blog'}, status=403)
        
        try:
            blog.title = request_data.get('title', blog.title)
            blog.content = request_data.get('content', blog.content)
            if 'thumbnail' in request_data:
                blog.thumbnail = request_data.get('thumbnail')
            blog.save()
            return JsonResponse(_blog_to_dict(blog))
        except (ValueError, KeyError) as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    elif method == 'DELETE':
        if not request.user or not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        if blog.user != request.user:
            return JsonResponse({'error': 'Not authorized to delete this blog'}, status=403)
        
        blog.delete()
        # 204 responses must not include a response body; many HTTP clients
        # will fail to decode JSON if we return any content.
        return JsonResponse({'message': 'Blog deleted successfully'}, status=200)


@csrf_exempt
@require_http_methods(["GET"])
def api_user_blogs(request):
    """API endpoint to get user's own blogs."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    blogs = Blog.objects.filter(user=request.user).order_by('-created_at')
    blog_list = [_blog_to_dict(blog) for blog in blogs]
    return JsonResponse(blog_list, safe=False)
