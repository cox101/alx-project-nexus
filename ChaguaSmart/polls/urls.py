from django.urls import path
from .views import PollListCreateView, CastVoteView, PollResultsView

urlpatterns = [
    path('', PollListCreateView.as_view(), name='poll-list-create'),
    path('<int:poll_id>/vote/', CastVoteView.as_view(), name='cast-vote'),
    path('<int:poll_id>/results/', PollResultsView.as_view(), name='poll-results'),
]

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PollViewSet, OptionViewSet

router = DefaultRouter()
router.register(r'polls', PollViewSet, basename='polls')
router.register(r'options', OptionViewSet, basename='options')

urlpatterns = [
    path('', include(router.urls)),
]

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('polls.urls')),
]
