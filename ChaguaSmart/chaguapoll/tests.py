from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta
from .models import Poll, Option, Vote

User = get_user_model()


class PollModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            campus='Test Campus'
        )
        
        self.poll = Poll.objects.create(
            title='Test Poll',
            description='Test Description',
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(days=1),
            created_by=self.user
        )
        
        self.option1 = Option.objects.create(
            poll=self.poll,
            option_text='Option 1'
        )
        
        self.option2 = Option.objects.create(
            poll=self.poll,
            option_text='Option 2'
        )

    def test_poll_str_representation(self):
        self.assertEqual(str(self.poll), 'Test Poll')

    def test_option_str_representation(self):
        expected = f"{self.poll.title} - {self.option1.option_text}"
        self.assertEqual(str(self.option1), expected)

    def test_poll_creation(self):
        self.assertEqual(self.poll.title, 'Test Poll')
        self.assertEqual(self.poll.created_by, self.user)
        self.assertEqual(self.poll.options.count(), 2)

    def test_vote_unique_constraint(self):
        # Create first vote
        Vote.objects.create(user=self.user, option=self.option1)
        
        # Try to create duplicate vote (should raise exception)
        with self.assertRaises(Exception):
            Vote.objects.create(user=self.user, option=self.option1)


class PollAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create users
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            campus='Admin Campus',
            is_admin=True
        )
        
        self.regular_user = User.objects.create_user(
            username='regular',
            email='regular@example.com',
            password='regularpass123',
            campus='Regular Campus'
        )
        
        # Create test poll
        self.poll = Poll.objects.create(
            title='Test Poll',
            description='Test Description',
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(days=1),
            created_by=self.admin_user
        )
        
        self.option1 = Option.objects.create(
            poll=self.poll,
            option_text='Option 1'
        )
        
        self.option2 = Option.objects.create(
            poll=self.poll,
            option_text='Option 2'
        )

    def get_jwt_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_poll_list_unauthenticated(self):
        url = reverse('poll-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_poll_list_authenticated(self):
        token = self.get_jwt_token(self.regular_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = reverse('poll-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_poll_create_admin(self):
        token = self.get_jwt_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = reverse('poll-list')
        data = {
            'title': 'New Poll',
            'description': 'New Description',
            'start_time': timezone.now().isoformat(),
            'end_time': (timezone.now() + timedelta(days=1)).isoformat(),
            'options': ['Option A', 'Option B', 'Option C']
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Poll.objects.count(), 2)

    def test_poll_create_regular_user(self):
        token = self.get_jwt_token(self.regular_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = reverse('poll-list')
        data = {
            'title': 'New Poll',
            'description': 'New Description',
            'start_time': timezone.now().isoformat(),
            'end_time': (timezone.now() + timedelta(days=1)).isoformat(),
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_vote_creation(self):
        token = self.get_jwt_token(self.regular_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = reverse('vote-create')
        data = {'option': self.option1.id}
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Vote.objects.count(), 1)

    def test_duplicate_vote_prevention(self):
        token = self.get_jwt_token(self.regular_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # Create first vote
        Vote.objects.create(user=self.regular_user, option=self.option1)
        
        url = reverse('vote-create')
        data = {'option': self.option2.id}  # Try to vote on same poll
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('already voted', response.data['detail'])

    def test_poll_results(self):
        # Create some votes
        Vote.objects.create(user=self.regular_user, option=self.option1)
        
        token = self.get_jwt_token(self.regular_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = reverse('poll-results', kwargs={'pk': self.poll.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_votes'], 1)
        self.assertEqual(len(response.data['results']), 2)

    def test_active_polls_filter(self):
        # Create expired poll
        expired_poll = Poll.objects.create(
            title='Expired Poll',
            description='Expired',
            start_time=timezone.now() - timedelta(days=2),
            end_time=timezone.now() - timedelta(days=1),
            created_by=self.admin_user
        )
        
        token = self.get_jwt_token(self.regular_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = reverse('active-polls')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only return active poll, not expired one
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.poll.id)

    def test_user_votes_list(self):
        # Create vote
        Vote.objects.create(user=self.regular_user, option=self.option1)
        
        token = self.get_jwt_token(self.regular_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = reverse('user-votes')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_close_poll_permission(self):
        token = self.get_jwt_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = reverse('poll-close-poll', kwargs={'pk': self.poll.pk})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refresh poll from database
        self.poll.refresh_from_db()
        self.assertLess(self.poll.end_time, timezone.now())

    def test_vote_on_expired_poll(self):
        # Create expired poll
        expired_poll = Poll.objects.create(
            title='Expired Poll',
            description='Expired',
            start_time=timezone.now() - timedelta(days=2),
            end_time=timezone.now() - timedelta(days=1),
            created_by=self.admin_user
        )
        
        expired_option = Option.objects.create(
            poll=expired_poll,
            option_text='Expired Option'
        )
        
        token = self.get_jwt_token(self.regular_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = reverse('vote-create')
        data = {'option': expired_option.id}
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('ended', response.data['detail'])


class VoteModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='voter',
            email='voter@example.com',
            password='voterpass123',
            campus='Voter Campus'
        )
        
        self.poll = Poll.objects.create(
            title='Vote Test Poll',
            description='For testing votes',
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(days=1),
            created_by=self.user
        )
        
        self.option = Option.objects.create(
            poll=self.poll,
            option_text='Test Option'
        )

    def test_vote_creation(self):
        vote = Vote.objects.create(
            user=self.user,
            option=self.option
        )
        
        self.assertEqual(vote.user, self.user)
        self.assertEqual(vote.option, self.option)
        self.assertIsNotNone(vote.voted_at)

    def test_vote_cascade_delete(self):
        vote = Vote.objects.create(user=self.user, option=self.option)
        
        # Delete poll should cascade to options and votes
        self.poll.delete()
        
        self.assertFalse(Vote.objects.filter(id=vote.id).exists())
        self.assertFalse(Option.objects.filter(id=self.option.id).exists())


# Run tests with: python manage.py test chaguapoll.tests