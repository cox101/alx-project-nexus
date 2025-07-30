from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.urls import include

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
    path('admin/', admin.site.urls),
    path('api/polls/', include('polls.urls')),
     path('api/users/', include('users.urls')),
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]

