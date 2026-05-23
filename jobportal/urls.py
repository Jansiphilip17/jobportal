from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('jobs.urls')),
    path('accounts/', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('candidate/', include('candidates.urls')),
    path('applications/', include('applications.urls')),
    path('recruiters/', include('recruiters.urls')),
    path('companies/', include('companies.urls')),
    path('interviews/', include('interviews.urls')),
    path('notifications/', include('notifications.urls')),
    # API
    path('api/accounts/', include('accounts.api_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
