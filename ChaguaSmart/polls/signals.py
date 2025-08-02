from django.db.models.signals import post_save, post_delete, pre_save, m2m_changed
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.cache import cache
from django.db.models import Count, F

from .models import Poll, Option, Vote

User = get_user_model()


@receiver(post_save, sender=Poll)
def poll_created_or_updated(sender, instance, created, **kwargs):
    """Handle actions when a poll is created or updated"""
    # Clear cache for polls
    cache.delete(f'poll_{instance.id}')
    cache.delete('active_polls')
    
    if created:
        # Log poll creation
        print(f"New poll created: {instance.title} by {instance.created_by}")
        
        # You could send notifications here
        # from django.core.mail import send_mail
        # send_mail(
        #     f'New Poll: {instance.title}',
        #     f'A new poll has been created: {instance.title}',
        #     'noreply@chaguasmart.com',
        #     [user.email for user in User.objects.filter(campus=instance.created_by.campus)],
        #     fail_silently=True,
        # )


@receiver(post_save, sender=Option)
def option_created_or_updated(sender, instance, created, **kwargs):
    """Handle actions when a poll option is created or updated"""
    # Clear cache for related poll
    cache.delete(f'poll_{instance.poll_id}')
    cache.delete(f'poll_{instance.poll_id}_options')
    
    if created:
        # Log option creation
        print(f"New option added to poll '{instance.poll.title}': {instance.text}")


@receiver(post_save, sender=Vote)
def vote_cast(sender, instance, created, **kwargs):
    """Handle actions when a vote is cast"""
    if created:
        # Clear result caches
        cache.delete(f'poll_{instance.poll_id}_results')
        cache.delete(f'user_{instance.user_id}_votes')
        
        # Log vote
        print(f"Vote cast by {instance.user} for '{instance.option.text}' in poll '{instance.poll.title}'")
        
        # Update poll statistics if needed
        with transaction.atomic():
            poll = instance.poll
            option = instance.option
            # If you had a total_votes field, you could update it directly
            # poll.total_votes = F('total_votes') + 1
            # poll.save(update_fields=['total_votes'])


@receiver(post_delete, sender=Vote)
def vote_deleted(sender, instance, **kwargs):
    """Handle actions when a vote is deleted"""
    # Clear result caches
    cache.delete(f'poll_{instance.poll_id}_results')
    cache.delete(f'user_{instance.user_id}_votes')
    
    # Log vote deletion
    print(f"Vote deleted: {instance.user} for option '{instance.option.text}' in poll '{instance.poll.title}'")


@receiver(pre_save, sender=Poll)
def check_poll_dates(sender, instance, **kwargs):
    """Validate poll dates before saving"""
    if instance.end_time and instance.start_time and instance.end_time <= instance.start_time:
        # Auto-adjust the end_time to be 1 day after start_time
        instance.end_time = instance.start_time + timezone.timedelta(days=1)
        print(f"Warning: End time for poll '{instance.title}' was adjusted to be after start time")


# Check if poll is expired and auto-close it
@receiver(pre_save, sender=Poll)
def auto_close_expired_polls(sender, instance, **kwargs):
    """Auto-close polls that have reached their end_time"""
    if instance.is_active and timezone.now() >= instance.end_time:
        instance.is_active = False
        print(f"Poll '{instance.title}' automatically closed as it reached end time")


# Function to recalculate vote counts for a poll
def recalculate_poll_vote_counts(poll_id):
    """Recalculate and update vote counts for a poll's options"""
    with transaction.atomic():
        # Get all options with their vote counts
        options = Option.objects.filter(poll_id=poll_id).annotate(
            votes_count=Count('vote')
        )
        
        # Update any cache or fields if needed
        for option in options:
            cache.set(f'option_{option.id}_vote_count', option.votes_count, 3600)
        
        # Optionally update poll's total votes
        total_votes = sum(option.votes_count for option in options)
        cache.set(f'poll_{poll_id}_total_votes', total_votes, 3600)
        
        return total_votes