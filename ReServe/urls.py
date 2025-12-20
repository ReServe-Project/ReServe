from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from checkout import views as checkout_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),

    # master added this app routing — keep it
    path('', include(('home_search.urls', 'home_search'))),
    # your existing apps

    path('blog/', include('blog.urls')),
    path('goals/', include('PersonalGoals.urls')),
    # Map history directly to the booking_history view instead of including the
    # `checkout` urls again (including the same URLconf twice caused the
    # "URL namespace 'checkout' isn't unique" warning).
    path('history/', checkout_views.booking_history_view, name='booking_history'),
    path('', include('product_details.urls')),
    path('checkout/', include('checkout.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
