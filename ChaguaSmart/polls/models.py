from django.db import models
from django.utils import timezone


class Poll(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_by = models.ForeignKey('users.User', on_delete=models.CASCADE)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)

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
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    option = models.ForeignKey(Option, on_delete=models.CASCADE)
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'poll')

    def __str__(self):
        return f"{self.user.username} voted for {self.option.text} in {self.poll.title}"
