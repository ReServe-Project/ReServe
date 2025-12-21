from django.urls import path
from blog.views import (
    main_blog, create_blog, blog_details, show_json_by_id, show_xml, show_json, 
    show_xml_by_id, edit_blog, delete_blog, api_blogs, api_blog_detail, api_user_blogs,
    proxy_image,
)

app_name = 'blog'

urlpatterns = [
    # Traditional views
    path('', main_blog, name='main_blog'),
    path('create-blog/', create_blog, name='create_blog'),
    path('blog/<str:id>/', blog_details, name='blog_details'),
    path('xml/', show_xml, name='show_xml'),
    path('json/', show_json, name='show_json'),
    path('xml/<str:id>/', show_xml_by_id, name='show_xml_by_id'),
    path('json/<str:id>/', show_json_by_id, name='show_json_by_id'),
    path('edit/<str:id>/', edit_blog, name='edit_blog'),
    path('delete/<str:id>/', delete_blog, name='delete_blog'),
    
    # API endpoints for mobile app
    path('api/blogs/', api_blogs, name='api_blogs'),
    path('api/blogs/<str:blog_id>/', api_blog_detail, name='api_blog_detail'),
    path('api/user-blogs/', api_user_blogs, name='api_user_blogs'),
    path('api/proxy-image/', proxy_image, name='proxy_image'),
]