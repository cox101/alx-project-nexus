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
        related_name='created_polls'  
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Add these missing fields with default values
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(default=timezone.now)  

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

    def get_vote_count(self, option_id):
        """Return the number of votes for a specific option"""
        return self.votes.filter(option_id=option_id).count()

    def get_results(self):
        """Compute complete poll results"""
        options = self.options.all()
        total_votes = self.votes.count()
        
        results = []
        for option in options:
            vote_count = self.get_vote_count(option.id)
            percentage = (vote_count / total_votes * 100) if total_votes > 0 else 0
            
            results.append({
                'option_id': option.id,
                'text': option.text,
                'votes': vote_count,
                'percentage': round(percentage, 2)
            })
        
        return {
            'total_votes': total_votes,
            'results': results
        }


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
        unique_together = ('poll', 'user')  

    def __str__(self):
        return f"{self.user.username} voted for {self.option.text} in {self.poll.title}"

class Region(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    
    def __str__(self):
        return self.name

class PollingStation(models.Model):
    name = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='stations')
    address = models.TextField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} ({self.region.name})"
