from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils.timezone import now
from django.db.models import Count
from django.contrib.auth import get_user_model
from .models import Poll, Option, Vote
from .serializers import PollSerializer, VoteSerializer, RegisterSerializer

User = get_user_model()


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

        # Check if user has already voted on this poll
        if Vote.objects.filter(user=user, option__poll_id=poll_id).exists():
            return Response({"detail": "You have already voted."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            option = Option.objects.get(id=option_id, poll_id=poll_id)
            vote = Vote.objects.create(user=user, option=option)
            return Response(VoteSerializer(vote).data, status=status.HTTP_201_CREATED)
        except Option.DoesNotExist:
            return Response({"detail": "Invalid option."}, status=status.HTTP_400_BAD_REQUEST)


class PollResultsView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]

    def retrieve(self, request, *args, **kwargs):
        poll_id = kwargs.get("poll_id")
        options = Option.objects.filter(poll_id=poll_id).annotate(vote_count=Count('vote'))
        data = [{"option": option.option_text, "votes": option.vote_count} for option in options]
        return Response(data)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

