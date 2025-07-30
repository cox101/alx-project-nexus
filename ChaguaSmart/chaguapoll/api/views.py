from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from .models import Poll, Option, Vote
from .serializers import PollSerializer, VoteSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.utils import timezone
from rest_framework.views import APIView

class PollViewSet(viewsets.ModelViewSet):
    serializer_class = PollSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Poll.objects.filter(expiry_date__gt=timezone.now())

    def perform_create(self, serializer):
        poll = serializer.save()
        options = self.request.data.get('options', [])
        for opt in options:
            Option.objects.create(poll=poll, text=opt)

class VoteAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request):
        serializer = VoteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(voter_ip=request.META['REMOTE_ADDR'])
            return Response({"detail": "Vote recorded."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PollResultsAPIView(generics.RetrieveAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer

    def retrieve(self, request, *args, **kwargs):
        poll = self.get_object()
        data = PollSerializer(poll).data
        for option in data['options']:
            option_obj = Option.objects.get(id=option['id'])
            option['votes'] = option_obj.votes
        return Response(data)
