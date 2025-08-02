from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings

User = get_user_model()


@receiver(post_save, sender=User)
def user_created_or_updated(sender, instance, created, **kwargs):
    """Handle actions when a user is created or updated"""
    # Clear user cache
    cache.delete(f'user_{instance.id}')
    cache.delete(f'user_{instance.id}_profile')
    
    if created:
        # Log new user
        campus_info = getattr(instance, 'campus', 'Not specified')
        print(f"New user registered: {instance.username} ({instance.email}) from campus {campus_info}")
        
        # You could create a profile, send welcome email, etc.
        # create_user_profile(instance)
        # send_welcome_email(instance)
    else:
        # For updates
        print(f"User updated: {instance.username} ({instance.email})")


@receiver(pre_save, sender=User)
def user_about_to_save(sender, instance, **kwargs):
    """Handle actions before a user is saved"""
    if instance.pk:  # If this is an update, not a new user
        try:
            old_instance = User.objects.get(pk=instance.pk)
            
            # If email changed, you might want to mark it unverified
            if old_instance.email != instance.email:
                # Set a flag for email verification if you have one
                # instance.email_verified = False
                print(f"User {instance.username} changed email from {old_instance.email} to {instance.email}")
            
            # If campus changed, check safely if the attribute exists
            if hasattr(old_instance, 'campus') and hasattr(instance, 'campus'):
                if getattr(old_instance, 'campus', None) != getattr(instance, 'campus', None):
                    print(f"User {instance.username} changed campus from {getattr(old_instance, 'campus', 'None')} to {getattr(instance, 'campus', 'None')}")
                
        except User.DoesNotExist:
            # This is a new user, though we should never reach here due to the if instance.pk condition
            pass


# Signal for password reset
try:
    from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed

    @receiver(user_logged_in)
    def user_logged_in_callback(sender, request, user, **kwargs):
        """Handle successful login"""
        # Update last login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        # You could record IP, device, etc.
        ip = request.META.get('REMOTE_ADDR', '')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        print(f"User {user.username} logged in from IP: {ip} using: {user_agent}")
        
        # You could create login history
        # LoginHistory.objects.create(user=user, ip_address=ip, user_agent=user_agent)

    @receiver(user_logged_out)
    def user_logged_out_callback(sender, request, user, **kwargs):
        """Handle logout"""
        if user:
            print(f"User {user.username} logged out")
            
            # You could update session end time
            # update_session_end_time(user)

    @receiver(user_login_failed)
    def user_login_failed_callback(sender, credentials, request, **kwargs):
        """Handle failed login attempt"""
        username = credentials.get('username', '')
        ip = request.META.get('REMOTE_ADDR', '')
        print(f"Failed login attempt for username: {username} from IP: {ip}")
        
        # You could implement security measures
        # track_failed_login_attempts(username, ip)
        
except ImportError:
    # Django version might not have these signals
    pass


# Signal for password reset/change
try:
    from django.contrib.auth.signals import password_changed, password_reset

    @receiver(password_changed)
    def password_changed_callback(sender, request, user, **kwargs):
        """Handle password change"""
        print(f"Password changed for user: {user.username}")
        
        # You could send notification email
        # send_password_changed_notification(user)

    @receiver(password_reset)
    def password_reset_callback(sender, request, user, **kwargs):
        """Handle password reset"""
        print(f"Password reset for user: {user.username}")
        
        # You could send notification email
        # send_password_reset_notification(user)
        
except ImportError:
    # Django version might not have these signals
    pass