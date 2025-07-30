from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.utils import timezone
from users.models import User
from polls.models import Poll, Option, Vote
from datetime import timedelta

class PollTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create user and admin
        self.student = User.objects.create_user(username="student", password="pass123", campus="Main")
        self.admin = User.objects.create_user(username="admin", password="pass123", is_admin=True, campus="Main")

        # Login admin and get token
        self.client.login(username="admin", password="pass123")

        # Create a poll
        self.poll = Poll.objects.create(
            title="President Election",
            description="Vote your next president",
            created_by=self.admin,
            expiry_date=timezone.now() + timedelta(days=1)
        )
        self.option1 = Option.objects.create(poll=self.poll, title="Candidate A")
        self.option2 = Option.objects.create(poll=self.poll, title="Candidate B")

    def test_admin_can_create_poll(self):
        response = self.client.post(reverse('poll-list-create'), {
            "title": "Secretary",
            "description": "Secretary election",
            "expiry_date": (timezone.now() + timedelta(days=2)).isoformat()
        })
        self.assertEqual(response.status_code, 201)

    def test_student_cannot_vote_twice(self):
        self.client.logout()
        self.client.login(username="student", password="pass123")

        vote_url = reverse('cast-vote', kwargs={'poll_id': self.poll.id})
        response1 = self.client.post(vote_url, {"option": self.option1.id})
        response2 = self.client.post(vote_url, {"option": self.option2.id})

        self.assertEqual(response1.status_code, 201)
        self.assertEqual(response2.status_code, 400)

    def test_vote_fails_on_expired_poll(self):
        self.poll.expiry_date = timezone.now() - timedelta(hours=1)
        self.poll.save()

        self.client.login(username="student", password="pass123")
        vote_url = reverse('cast-vote', kwargs={'poll_id': self.poll.id})
        response = self.client.post(vote_url, {"option": self.option1.id})
        self.assertEqual(response.status_code, 403)

    def test_poll_results_return_correct_data(self):
        Vote.objects.create(user=self.student, poll=self.poll, option=self.option1)

        results_url = reverse('poll-results', kwargs={'poll_id': self.poll.id})
        response = self.client.get(results_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("votes", response.data[0])
