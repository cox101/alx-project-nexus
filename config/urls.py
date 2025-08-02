from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings
from django.conf.urls.static import static

schema_view = get_schema_view(
   openapi.Info(
      title="ChaguaSmart API",
      default_version='v1',
      description="Backend API for campus elections.",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Add a root URL pattern that redirects to the API documentation
    path('', RedirectView.as_view(url='/api/docs/', permanent=False), name='home'),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # Include app URLs when you're ready
    # path('api/polls/', include('polls.urls')),
    # path('api/users/', include('users.urls')),
]

# Add debug static files support in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

