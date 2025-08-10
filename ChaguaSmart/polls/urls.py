from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PollListCreateView,
    PollDetailView,
    CastVoteView,    
    PollResultsView,  
    PollViewSet,
    ActivePollsView,
    UserVotesView,
    FilteredPollListView,
)

app_name = 'polls'

# Router for ViewSet-based endpoints
router = DefaultRouter()
router.register(r'', PollViewSet, basename='polls')

urlpatterns = [
    # Router URLs (includes CRUD operations for polls)
    path('', include(router.urls)),
    
    # Voting endpoints
    path('votes/', CastVoteView.as_view(), name='vote-create'),
    path('votes/my-votes/', UserVotesView.as_view(), name='user-votes'),
    
    # Poll-specific actions
    path('polls/<int:pk>/results/', PollResultsView.as_view(), name='poll-results'),
    path('polls/<int:poll_id>/vote/', CastVoteView.as_view(), name='poll-vote'),
    
    # Additional endpoints
    path('polls/active/', ActivePollsView.as_view(), name='active-polls'),
    path('filtered/', FilteredPollListView.as_view(), name='filtered-polls'),

    # New poll list and create view
    path('polls/new/', PollListCreateView.as_view(), name='poll-list-create'),
    path('polls/<int:pk>/', PollDetailView.as_view(), name='poll-detail'),
]
