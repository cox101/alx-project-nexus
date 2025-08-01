from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PollViewSet, 
    VoteAPIView, 
    PollResultsAPIView,
    UserVotesAPIView,
    ActivePollsAPIView
)

router = DefaultRouter()
router.register(r'polls', PollViewSet, basename='poll')

urlpatterns = [
    # Router URLs (includes CRUD operations for polls)
    path('', include(router.urls)),
    
    # Voting endpoints
    path('votes/', VoteAPIView.as_view(), name='vote-create'),
    path('votes/my-votes/', UserVotesAPIView.as_view(), name='user-votes'),
    
    # Poll results and analytics
    path('polls/<int:pk>/results/', PollResultsAPIView.as_view(), name='poll-results'),
    path('polls/<int:pk>/vote/', VoteAPIView.as_view(), name='poll-vote'),
    
    # Filtered poll views
    path('polls/active/', ActivePollsAPIView.as_view(), name='active-polls'),
    
    # Additional poll actions
    path('polls/<int:pk>/close/', PollViewSet.as_view({'post': 'close_poll'}), name='close-poll'),
]
