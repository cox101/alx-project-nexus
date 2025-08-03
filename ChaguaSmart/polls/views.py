from rest_framework import generics, permissions
from rest_framework.response import Response
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from .models import Poll, Option, Vote
from .serializers import PollSerializer, VoteSerializer
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
User = get_user_model()
from users.serializers import UserSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer
class CustomTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer   

from rest_framework.exceptions import PermissionDenied

class CastVoteView(generics.CreateAPIView):
    def create(self, request, *args, **kwargs):
        user = request.user
        poll_id = self.kwargs.get("poll_id")
        option_id = request.data.get("option")

        poll = Poll.objects.get(id=poll_id)

        if not poll.is_active:
            raise PermissionDenied("This poll has expired.")

        if Vote.objects.filter(user=user, poll_id=poll_id).exists():
            return Response({"detail": "You have already voted."}, status=status.HTTP_400_BAD_REQUEST)

        vote = Vote.objects.create(user=user, poll=poll, option_id=option_id)
        return Response(VoteSerializer(vote).data, status=status.HTTP_201_CREATED)

# (Move this block below the PollListCreateView and other view class definitions)
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
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
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# polls/views.py

from rest_framework.exceptions import PermissionDenied

class CastVoteView(generics.CreateAPIView):
    ...

    def create(self, request, *args, **kwargs):
        user = request.user
        poll_id = self.kwargs.get("poll_id")
        option_id = request.data.get("option")

        poll = Poll.objects.get(id=poll_id)

        if not poll.is_active:
            raise PermissionDenied("This poll has expired.")

        if Vote.objects.filter(user=user, poll_id=poll_id).exists():
            return Response({"detail": "You have already voted."}, status=status.HTTP_400_BAD_REQUEST)

        vote = Vote.objects.create(user=user, poll=poll, option_id=option_id)
        return Response(VoteSerializer(vote).data, status=status.HTTP_201_CREATED)

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Poll, Option, Vote
from .serializers import (
    PollSerializer,
    CreatePollSerializer,
    OptionSerializer,
    VoteSerializer
)

class PollViewSet(viewsets.ModelViewSet):
    queryset = Poll.objects.all().order_by('-created_at')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'create':
            return CreatePollSerializer
        return PollSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def vote(self, request, pk=None):
        poll = self.get_object()
        serializer = VoteSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user, poll=poll)
            return Response({"message": "Vote submitted"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OptionViewSet(viewsets.ModelViewSet):
    queryset = Option.objects.all()
    serializer_class = OptionSerializer
    permission_classes = [permissions.IsAdminUser]

from rest_framework.permissions import IsAuthenticated

class PollCreateView(generics.CreateAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

from django_filters.rest_framework import DjangoFilterBackend

class PollListCreateView(generics.ListCreateAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class FilteredPollListView(generics.ListAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active', 'created_by']

class PollResultsView(generics.RetrieveAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    permission_classes = [permissions.AllowAny]

    def retrieve(self, request, *args, **kwargs):
        poll_id = self.kwargs.get("poll_id")
class PollResultsView(generics.RetrieveAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    permission_classes = [permissions.AllowAny]

    def retrieve(self, request, *args, **kwargs):
        poll_id = self.kwargs.get("poll_id")
        poll = Poll.objects.get(id=poll_id)
        options = Option.objects.filter(poll=poll).annotate(vote_count=Count('vote'))
        results = {option.text: option.vote_count for option in options}
        return Response({
            "poll": PollSerializer(poll).data,
            "results": results
        })

from django.urls import path, include
urlpatterns = [
    path('', PollListCreateView.as_view(), name='poll-list-create'),
    path('<int:poll_id>/vote/', CastVoteView.as_view(), name='cast-vote'),
    path('<int:poll_id>/results/', PollResultsView.as_view(), name='poll-results'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token-refresh'),
]
