from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Count
from .models import Poll, Option, Vote
from .serializers import PollSerializer, VoteSerializer, PollCreateSerializer
from .permissions import IsAdminOrReadOnly, CanVotePermission, IsPollCreatorOrAdmin


class PollViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        # Filter active polls (using end_time instead of expiry_date)
        return Poll.objects.filter(end_time__gt=timezone.now()).order_by('-start_time')

    def get_serializer_class(self):
        if self.action == 'create':
            return PollCreateSerializer
        return PollSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsPollCreatorOrAdmin])
    def close_poll(self, request, pk=None):
        poll = self.get_object()
        poll.end_time = timezone.now()
        poll.save()
        return Response({"detail": "Poll closed successfully."})

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get only currently active polls"""
        now = timezone.now()
        active_polls = Poll.objects.filter(
            start_time__lte=now,
            end_time__gt=now
        )
        serializer = self.get_serializer(active_polls, many=True)
        return Response(serializer.data)


class VoteAPIView(generics.CreateAPIView):
    serializer_class = VoteSerializer
    permission_classes = [IsAuthenticated, CanVotePermission]

    def create(self, request, *args, **kwargs):
        option_id = request.data.get('option')
        
        if not option_id:
            return Response(
                {"detail": "Option ID is required."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            option = Option.objects.get(id=option_id)
            poll = option.poll
            
            # Check if user already voted on this poll
            if Vote.objects.filter(user=request.user, option__poll=poll).exists():
                return Response(
                    {"detail": "You have already voted on this poll."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if poll is active
            now = timezone.now()
            if poll.end_time <= now:
                return Response(
                    {"detail": "This poll has ended."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if poll.start_time > now:
                return Response(
                    {"detail": "This poll has not started yet."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create the vote
            vote = Vote.objects.create(
                user=request.user,
                option=option
            )
            
            serializer = self.get_serializer(vote)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Option.DoesNotExist:
            return Response(
                {"detail": "Invalid option."}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class PollResultsAPIView(generics.RetrieveAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer

    def retrieve(self, request, *args, **kwargs):
        poll = self.get_object()
        
        # Get options with vote counts
        options_with_votes = Option.objects.filter(poll=poll).annotate(
            vote_count=Count('vote')
        )
        
        results = {
            'poll': PollSerializer(poll).data,
            'results': [
                {
                    'option_id': option.id,
                    'option_text': option.option_text,
                    'vote_count': option.vote_count
                }
                for option in options_with_votes
            ],
            'total_votes': Vote.objects.filter(option__poll=poll).count()
        }
        
        return Response(results)


class UserVotesAPIView(generics.ListAPIView):
    serializer_class = VoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Vote.objects.filter(user=self.request.user).order_by('-voted_at')


class ActivePollsAPIView(generics.ListAPIView):
    serializer_class = PollSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        now = timezone.now()
        return Poll.objects.filter(
            start_time__lte=now,
            end_time__gt=now
        ).order_by('-start_time')
