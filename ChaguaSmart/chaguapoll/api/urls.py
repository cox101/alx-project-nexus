from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PollViewSet, VoteAPIView, PollResultsAPIView

router = DefaultRouter()
router.register(r'polls', PollViewSet, basename='poll')

urlpatterns = [
    path('', include(router.urls)),
    path('votes/', VoteAPIView.as_view(), name='vote'),
    path('polls/<int:pk>/results/', PollResultsAPIView.as_view(), name='poll-results'),
]
