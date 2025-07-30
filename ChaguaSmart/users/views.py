from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.utils.timezone import now
from django.db.models import Count

from .models import Poll, Option, Vote
from .serializers import PollSerializer, VoteSerializer
from rest_framework import generics
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
from .serializers import UserSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

class PollListCreateView(generics.ListCreateAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class CastVoteView(generics.CreateAPIView):
    serializer_class = VoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        poll_id = self.kwargs.get("poll_id")
        option_id = request.data.get("option")

        if Vote.objects.filter(user=user, poll_id=poll_id).exists():
            return Response({"detail": "You have already voted."}, status=status.HTTP_400_BAD_REQUEST)

        vote = Vote.objects.create(user=user, poll_id=poll_id, option_id=option_id)
        return Response(VoteSerializer(vote).data, status=status.HTTP_201_CREATED)

class PollResultsView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]

    def retrieve(self, request, *args, **kwargs):
        poll_id = kwargs.get("poll_id")
        options = Option.objects.filter(poll_id=poll_id).annotate(vote_count=Count('votes'))
        data = [{"option": option.title, "votes": option.vote_count} for option in options]
        return Response(data)


User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserSerializer
