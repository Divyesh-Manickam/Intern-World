from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render

# Custom Error Views
def custom_400(request, exception=None):
    return render(request, 'errors/400.html', status=400)

def custom_403(request, exception=None):
    return render(request, 'errors/403.html', status=403)

def custom_404(request, exception=None):
    return render(request, 'errors/404.html', status=404)

def custom_500(request):
    return render(request, 'errors/500.html', status=500)

handler400 = 'config.urls.custom_400'
handler403 = 'config.urls.custom_403'
handler404 = 'config.urls.custom_404'
handler500 = 'config.urls.custom_500'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('students/', include('students.urls')),
    path('recruiters/', include('recruiters.urls')),
    path('applications/', include('applications.urls')),
    path('interviews/', include('interviews.urls')),
    path('notifications/', include('notifications.urls')),
    path('', include('analytics.urls')),
    path('api/', include('api.urls')),
    path('', include('opportunities.urls')),
]

# Serve media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
