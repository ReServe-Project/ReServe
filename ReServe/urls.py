from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # master added this app routing — keep it
    path('', include(('home_search.urls', 'home_search'))),
    # your existing apps
    path('', include('accounts.urls')),
    path('', include('main.urls')),
    path('', include('product_details.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
