"""
URL configuration for va_assistant project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('va_core.urls')),
]

# Serve React frontend for all non-API routes
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Catch-all pattern for React Router
urlpatterns += [
    re_path(r'^.*$', TemplateView.as_view(template_name='index.html')),
] 