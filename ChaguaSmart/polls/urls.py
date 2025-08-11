from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PollViewSet,
)

app_name = 'polls'

# Router for ViewSet-based endpoints
router = DefaultRouter()
router.register(r'', PollViewSet, basename='polls')

urlpatterns = [
    # Router URLs (includes CRUD operations for polls)
    path('', include(router.urls)),
]
