from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from django.contrib.auth import get_user_model
from polls.models import Poll, Option, Vote
from datetime import timedelta

User = get_user_model()


class PollTests(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Create user and admin
        self.student = User.objects.create_user(
            username="student", 
            password="pass123", 
            campus="Main"
        )
        self.admin = User.objects.create_user(
            username="admin", 
            password="pass123", 
            is_admin=True, 
            campus="Main"
        )

        # Create a poll with correct field names
        self.poll = Poll.objects.create(
            title="President Election",
            description="Vote your next president",
            created_by=self.admin,
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(days=1)  
        )
        
        # Create options with correct field name
        self.option1 = Option.objects.create(poll=self.poll, text="Candidate A")  
        self.option2 = Option.objects.create(poll=self.poll, text="Candidate B")

    def get_jwt_token(self, user):
        """Helper method to get JWT token for user"""
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def authenticate_user(self, user):
        """Helper method to authenticate user with JWT"""
        token = self.get_jwt_token(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_admin_can_create_poll(self):
        self.authenticate_user(self.admin)
        
        data = {
            "title": "Secretary Election",
            "description": "Secretary election",
            "start_time": timezone.now().isoformat(),
            "end_time": (timezone.now() + timedelta(days=2)).isoformat(),
            "options": ["Candidate X", "Candidate Y"] 
        }
        
        response = self.client.post(reverse('poll-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_student_cannot_create_poll(self):
        """Test that regular students cannot create polls"""
        self.authenticate_user(self.student)
        
        data = {
            "title": "Unauthorized Poll",
            "description": "Should not be created",
            "start_time": timezone.now().isoformat(),
            "end_time": (timezone.now() + timedelta(days=1)).isoformat(),
            "options": ["Option 1", "Option 2"]
        }
        
        response = self.client.post(reverse('poll-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_can_vote(self):
        self.authenticate_user(self.student)

        response = self.client.post(reverse('vote-create'), {
            "option": self.option1.id
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Vote.objects.count(), 1)

    def test_student_cannot_vote_twice(self):
        self.authenticate_user(self.student)

        # First vote
        response1 = self.client.post(reverse('vote-create'), {
            "option": self.option1.id
        }, format='json')
        
        # Second vote attempt on same poll
        response2 = self.client.post(reverse('vote-create'), {
            "option": self.option2.id
        }, format='json')

        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Vote.objects.count(), 1)

    def test_vote_fails_on_expired_poll(self):
        # Expire the poll
        self.poll.end_time = timezone.now() - timedelta(hours=1)
        self.poll.save()

        self.authenticate_user(self.student)
        
        response = self.client.post(reverse('vote-create'), {
            "option": self.option1.id
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("not currently accepting votes", str(response.data))

    def test_poll_results_return_correct_data(self):
        # Create a vote
        Vote.objects.create(user=self.student, poll=self.poll, option=self.option1)

        self.authenticate_user(self.admin)
        
        response = self.client.get(reverse('poll-results', kwargs={'pk': self.poll.id}))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_votes', response.data)
        self.assertIn('results', response.data)
        self.assertEqual(response.data['total_votes'], 1)

    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated users cannot access polls"""
        response = self.client.get(reverse('poll-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_poll_list_for_authenticated_user(self):
        self.authenticate_user(self.student)
        
        response = self.client.get(reverse('poll-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_active_polls_endpoint(self):
        # Create an expired poll
        expired_poll = Poll.objects.create(
            title="Expired Poll",
            description="This poll has ended",
            created_by=self.admin,
            start_time=timezone.now() - timedelta(days=2),
            end_time=timezone.now() - timedelta(days=1)
        )

        self.authenticate_user(self.student)
        
        response = self.client.get(reverse('active-polls'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only return active polls
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.poll.id)

    def test_user_votes_history(self):
        # Create a vote
        Vote.objects.create(user=self.student, poll=self.poll, option=self.option1)

        self.authenticate_user(self.student)
        
        response = self.client.get(reverse('user-votes'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_poll_creation_validation(self):
        """Test poll creation with invalid data"""
        self.authenticate_user(self.admin)
        
        # end time before start time
        invalid_data = {
            "title": "Invalid Poll",
            "description": "End time before start time",
            "start_time": timezone.now().isoformat(),
            "end_time": (timezone.now() - timedelta(hours=1)).isoformat(),
            "options": ["Option 1", "Option 2"]
        }
        
        response = self.client.post(reverse('poll-list'), invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_vote_on_future_poll(self):
        """Test voting on a poll that hasn't started yet"""
        future_poll = Poll.objects.create(
            title="Future Poll",
            description="Starts tomorrow",
            created_by=self.admin,
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=2)
        )
        
        future_option = Option.objects.create(poll=future_poll, text="Future Option")

        self.authenticate_user(self.student)
        
        response = self.client.post(reverse('vote-create'), {
            "option": future_option.id
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_poll_close_functionality(self):
        """Test that admin can close a poll"""
        self.authenticate_user(self.admin)
        
        response = self.client.post(reverse('poll-close-poll', kwargs={'pk': self.poll.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refresh poll from database and check it's closed
        self.poll.refresh_from_db()
        self.assertTrue(self.poll.has_expired)


class ModelTests(TestCase):
    """Test model properties and methods"""
    
    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin", 
            password="pass123", 
            is_admin=True, 
            campus="Main"
        )

    def test_poll_status_property(self):
        # Active poll
        active_poll = Poll.objects.create(
            title="Active Poll",
            created_by=self.admin,
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(days=1)
        )
        self.assertEqual(active_poll.status, "active")

        # Future poll
        future_poll = Poll.objects.create(
            title="Future Poll",
            created_by=self.admin,
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=2)
        )
        self.assertEqual(future_poll.status, "upcoming")

        # Expired poll
        expired_poll = Poll.objects.create(
            title="Expired Poll",
            created_by=self.admin,
            start_time=timezone.now() - timedelta(days=2),
            end_time=timezone.now() - timedelta(days=1)
        )
        self.assertEqual(expired_poll.status, "ended")

    def test_option_vote_count(self):
        poll = Poll.objects.create(
            title="Vote Count Poll",
            created_by=self.admin,
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(days=1)
        )
        option1 = Option.objects.create(poll=poll, text="Option 1")
        option2 = Option.objects.create(poll=poll, text="Option 2")

        # Create votes
        Vote.objects.create(poll=poll, option=option1, user=self.admin)
        Vote.objects.create(poll=poll, option=option1, user=self.student)

        # Refresh poll and check vote count
        poll.refresh_from_db()
        self.assertEqual(poll.get_vote_count(option1.id), 2)
        self.assertEqual(poll.get_vote_count(option2.id), 0)

    def test_poll_has_expired_property(self):
        """Test the has_expired property of the poll"""
        poll = Poll.objects.create(
            title="Test Poll",
            created_by=self.admin,
            start_time=timezone.now() - timedelta(days=1),
            end_time=timezone.now()
        )
        self.assertTrue(poll.has_expired)

        poll.end_time = timezone.now() + timedelta(days=1)
        poll.save()
        self.assertFalse(poll.has_expired)


class PollsApiTests(APITestCase):
    def test_list_polls(self):
        url = reverse('polls-list')  
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
