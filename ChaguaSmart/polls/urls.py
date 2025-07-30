from django.urls import path
from .views import PollListCreateView, CastVoteView, PollResultsView

urlpatterns = [
    path('', PollListCreateView.as_view(), name='poll-list-create'),
    path('<int:poll_id>/vote/', CastVoteView.as_view(), name='cast-vote'),
    path('<int:poll_id>/results/', PollResultsView.as_view(), name='poll-results'),
]
