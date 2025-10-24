from django.urls import path
from blog.views import main_blog, create_blog, blog_details, show_json_by_id, show_xml, show_json, show_xml_by_id

app_name = 'blog'

urlpatterns = [
    path('', main_blog, name='main_blog'),
    path('create-blog/', create_blog, name='create_blog'),
    path('blog/<str:id>/', blog_details, name='blog_details'),
    path('xml/', show_xml, name='show_xml'),
    path('json/', show_json, name='show_json'),
    path('xml/<str:id>/', show_xml_by_id, name='show_xml_by_id'),
    path('json/<str:id>/', show_json_by_id, name='show_json_by_id'),
]