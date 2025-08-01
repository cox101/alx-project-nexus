from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError

User = get_user_model()


class Poll(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_polls')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Optional fields for enhanced functionality
    is_anonymous = models.BooleanField(default=False, help_text="Allow anonymous voting")
    allow_multiple_votes = models.BooleanField(default=False, help_text="Allow users to vote multiple times")
    campus_restricted = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        help_text="Restrict voting to specific campus"
    )
    
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
        
        if self.end_time and self.end_time <= timezone.now():
            if not self.pk:  # Only for new polls
                raise ValidationError("End time must be in the future.")
    
    @property
    def is_active(self):
        """Check if poll is currently active"""
        now = timezone.now()
        return self.start_time <= now <= self.end_time
    
    @property
    def total_votes(self):
        """Get total number of votes for this poll"""
        return Vote.objects.filter(option__poll=self).count()
    
    @property
    def status(self):
        """Get current status of the poll"""
        now = timezone.now()
        if now < self.start_time:
            return "upcoming"
        elif now > self.end_time:
            return "ended"
        else:
            return "active"
    
    def get_results(self):
        """Get poll results with vote counts per option"""
        results = []
        for option in self.options.all():
            results.append({
                'option': option.option_text,
                'votes': option.vote_count,
                'percentage': option.vote_percentage
            })
        return results


class Option(models.Model):
    poll = models.ForeignKey(Poll, related_name='options', on_delete=models.CASCADE)
    option_text = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['id']
        unique_together = ['poll', 'option_text']
        verbose_name = "Option"
        verbose_name_plural = "Options"
    
    def __str__(self):
        return f"{self.poll.title} - {self.option_text}"
    
    @property
    def vote_count(self):
        """Get number of votes for this option"""
        return self.vote_set.count()
    
    @property
    def vote_percentage(self):
        """Get percentage of votes for this option"""
        total_votes = self.poll.total_votes
        if total_votes == 0:
            return 0
        return round((self.vote_count / total_votes) * 100, 2)


class Vote(models.Model):
    option = models.ForeignKey(Option, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    voted_at = models.DateTimeField(auto_now_add=True)
    
    # Optional fields for analytics
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, help_text="Browser/device information")
    
    class Meta:
        unique_together = ('option', 'user')
        ordering = ['-voted_at']
        verbose_name = "Vote"
        verbose_name_plural = "Votes"
        indexes = [
            models.Index(fields=['voted_at']),
            models.Index(fields=['user', 'voted_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} voted for {self.option.option_text}"
    
    def clean(self):
        # Check if poll is active
        if not self.option.poll.is_active:
            raise ValidationError("Cannot vote on inactive polls.")
        
        # Check if user already voted (unless multiple votes allowed)
        if not self.option.poll.allow_multiple_votes:
            existing_vote = Vote.objects.filter(
                user=self.user,
                option__poll=self.option.poll
            ).exclude(pk=self.pk).exists()
            
            if existing_vote:
                raise ValidationError("User has already voted on this poll.")
        
        # Check campus restrictions
        if (self.option.poll.campus_restricted and 
            hasattr(self.user, 'campus') and 
            self.user.campus != self.option.poll.campus_restricted):
            raise ValidationError("User is not allowed to vote on this campus-restricted poll.")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class PollCategory(models.Model):
    """Optional: Category system for polls"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default="#007bff", help_text="Hex color code")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Poll Category"
        verbose_name_plural = "Poll Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name


# Add category field to Poll model (optional)
# Uncomment if you want to use categories
# Poll.add_to_class('category', models.ForeignKey(
#     PollCategory, 
#     on_delete=models.SET_NULL, 
#     null=True, 
#     blank=True,
#     related_name='polls'
# ))


class PollView(models.Model):
    """Track poll views for analytics"""
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('poll', 'user', 'ip_address')
        ordering = ['-viewed_at']
        verbose_name = "Poll View"
        verbose_name_plural = "Poll Views"
    
    def __str__(self):
        user_info = self.user.username if self.user else "Anonymous"
        return f"{user_info} viewed {self.poll.title}"