from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import RegionViewSet

router = DefaultRouter()
router.register('', RegionViewSet, basename='regions')

urlpatterns = router.urls

from .models import Region
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import RegionSerializer  # You'll need to create this

class RegionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing regions"""
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    permission_classes = [IsAuthenticated]