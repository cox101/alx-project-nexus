from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

# Import for API documentation
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Create schema view for API documentation
schema_view = get_schema_view(
   openapi.Info(
      title="ChaguaSmart API",
      default_version='v1',
      description="API for campus voting and polls",
      terms_of_service="https://www.example.com/terms/",
      contact=openapi.Contact(email="contact@example.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Root URL redirects to admin
    path('', RedirectView.as_view(url='/admin/', permanent=False)),
    
    # Admin URL
    path('admin/', admin.site.urls),
    
    # Users app URLs
    path('api/users/', include('users.urls')),
    
    # Polls app URLs
    path('api/polls/', include('polls.urls')),
    
    # API Documentation
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Add static/media URLs
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

