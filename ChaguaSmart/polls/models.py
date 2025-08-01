from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError

User = get_user_model()


class Poll(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="polls")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField()  # Renamed from expiry_date for consistency
    
    # Additional fields for enhanced functionality
    is_active = models.BooleanField(default=True)
    allow_multiple_votes = models.BooleanField(default=False)
    is_anonymous = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Poll"
        verbose_name_plural = "Polls"

    def __str__(self):
        return self.title
    
    def clean(self):
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                raise ValidationError("End time must be after start time.")

    @property
    def has_expired(self):
        return timezone.now() > self.end_time
    
    @property
    def has_started(self):
        return timezone.now() >= self.start_time
    
    @property
    def is_currently_active(self):
        """Check if poll is currently accepting votes"""
        now = timezone.now()
        return (self.is_active and 
                self.start_time <= now <= self.end_time)
    
    @property
    def status(self):
        """Get current status of the poll"""
        if not self.is_active:
            return "inactive"
        
        now = timezone.now()
        if now < self.start_time:
            return "upcoming"
        elif now > self.end_time:
            return "ended"
        else:
            return "active"
    
    @property
    def total_votes(self):
        """Get total number of votes for this poll"""
        return self.votes.count()
    
    def get_results(self):
        """Get poll results with vote counts and percentages"""
        total_votes = self.total_votes
        results = []
        
        for option in self.options.all():
            vote_count = option.votes.count()
            percentage = (vote_count / total_votes * 100) if total_votes > 0 else 0
            
            results.append({
                'option': option.text,
                'votes': vote_count,
                'percentage': round(percentage, 2)
            })
        
        return results


class Option(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="options")
    text = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['id']
        unique_together = ['poll', 'text']  # Prevent duplicate options in same poll
        verbose_name = "Option"
        verbose_name_plural = "Options"

    def __str__(self):
        return f"{self.text} ({self.poll.title})"
    
    @property
    def vote_count(self):
        """Get number of votes for this option"""
        return self.votes.count()
    
    @property
    def vote_percentage(self):
        """Get percentage of votes for this option"""
        total_votes = self.poll.total_votes
        if total_votes == 0:
            return 0
        return round((self.vote_count / total_votes) * 100, 2)


class Vote(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="votes")
    option = models.ForeignKey(Option, on_delete=models.CASCADE, related_name="votes")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="votes")
    voted_at = models.DateTimeField(auto_now_add=True)
    
    # Optional fields for analytics
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        unique_together = ('poll', 'user')  # One vote per user per poll
        ordering = ['-voted_at']
        verbose_name = "Vote"
        verbose_name_plural = "Votes"
        indexes = [
            models.Index(fields=['voted_at']),
            models.Index(fields=['user', 'voted_at']),
        ]

    def __str__(self):
        return f"{self.user.username} voted for '{self.option.text}' in '{self.poll.title}'"
    
    def clean(self):
        # Ensure the option belongs to the poll
        if self.option and self.poll and self.option.poll != self.poll:
            raise ValidationError("Option must belong to the specified poll.")
        
        # Check if poll is active for voting
        if self.poll and not self.poll.is_currently_active:
            raise ValidationError("Cannot vote on inactive or expired polls.")
        
        # Check for existing vote if multiple votes not allowed
        if (self.poll and not self.poll.allow_multiple_votes and 
            Vote.objects.filter(poll=self.poll, user=self.user).exclude(pk=self.pk).exists()):
            raise ValidationError("User has already voted on this poll.")
    
    def save(self, *args, **kwargs):
        # Set poll from option if not provided
        if self.option and not self.poll:
            self.poll = self.option.poll
        
        self.full_clean()
        super().save(*args, **kwargs)
