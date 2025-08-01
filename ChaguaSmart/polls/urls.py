from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PollViewSet,
    VoteAPIView,
    PollResultsAPIView,
    UserVotesAPIView,
    ActivePollsAPIView
)

app_name = 'polls'

# Router for ViewSet-based endpoints
router = DefaultRouter()
router.register(r'polls', PollViewSet, basename='poll')

urlpatterns = [
    # Router URLs (includes CRUD operations for polls)
    path('', include(router.urls)),
    
    # Voting endpoints
    path('votes/', VoteAPIView.as_view(), name='vote-create'),
    path('votes/my-votes/', UserVotesAPIView.as_view(), name='user-votes'),
    
    # Poll-specific actions
    path('polls/<int:pk>/results/', PollResultsAPIView.as_view(), name='poll-results'),
    path('polls/<int:pk>/vote/', VoteAPIView.as_view(), name='poll-vote'),
    
    # Additional endpoints
    path('polls/active/', ActivePollsAPIView.as_view(), name='active-polls'),
]

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('polls.urls')),
]
