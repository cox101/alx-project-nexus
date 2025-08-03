from django.db import models
from django.utils import timezone
from django.conf import settings


class Poll(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_polls'  # Add related_name to avoid conflicts
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def has_started(self):
        return timezone.now() >= self.start_time

    @property
    def has_expired(self):
        return timezone.now() >= self.end_time

    @property
    def is_currently_active(self):
        return self.is_active and self.has_started and not self.has_expired

    @property
    def status(self):
        if not self.has_started:
            return "upcoming"
        elif self.has_expired:
            return "ended"
        else:
            return "active"


class Option(models.Model):
    poll = models.ForeignKey(Poll, related_name='options', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text

    @property
    def vote_count(self):
        return self.vote_set.count()


class Vote(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='votes')
    option = models.ForeignKey('Option', on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cast_votes'  # Add related_name to avoid conflicts
    )
    voted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('poll', 'user')  # Ensure one vote per user per poll

    def __str__(self):
        return f"{self.user.username} voted for {self.option.text} in {self.poll.title}"
