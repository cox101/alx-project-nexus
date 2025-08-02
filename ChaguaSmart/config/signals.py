from django.core.signals import request_started, request_finished
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.conf import settings
from django.apps import apps
import os
import time
import logging

User = get_user_model()
logger = logging.getLogger('django')


@receiver(request_started)
def request_started_handler(sender, environ, **kwargs):
    """Handle the beginning of an HTTP request"""
    # Start request timing
    environ['request_start_time'] = time.time()
    
    # Log request info (careful with production volume!)
    if settings.DEBUG:
        path = environ.get('PATH_INFO', '')
        method = environ.get('REQUEST_METHOD', '')
        ip = environ.get('REMOTE_ADDR', '')
        user_agent = environ.get('HTTP_USER_AGENT', '')
        logger.debug(f"Request started: {method} {path} from {ip} using {user_agent}")


@receiver(request_finished)
def request_finished_handler(sender, **kwargs):
    """Handle the end of an HTTP request"""
    # In practice, it's hard to get the same environ object here
    # so request timing is better done with middleware
    # But you can use this for cleanup operations
    if settings.DEBUG:
        logger.debug("Request finished")


@receiver(post_migrate)
def create_default_data(sender, app_config, **kwargs):
    """Create default data after migrations"""
    # Only run for specific apps
    if app_config and app_config.name == 'users':
        # Create default admin user if none exists
        User = get_user_model()
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                username=os.environ.get('DJANGO_ADMIN_USERNAME', 'admin'),
                email=os.environ.get('DJANGO_ADMIN_EMAIL', 'admin@chaguasmart.com'),
                password=os.environ.get('DJANGO_ADMIN_PASSWORD', 'admin'),
                is_admin=True,
                campus='Main'
            )
            print("Created default admin user")
    
    # Create default poll categories if needed
    if app_config and app_config.name == 'polls':
        if 'PollCategory' in [m.__name__ for m in app_config.get_models()]:
            PollCategory = apps.get_model('polls', 'PollCategory')
            
            default_categories = [
                {'name': 'Student Government', 'color': '#3498db'},
                {'name': 'Campus Events', 'color': '#2ecc71'},
                {'name': 'Academic', 'color': '#e74c3c'},
                {'name': 'Campus Services', 'color': '#f39c12'},
                {'name': 'Other', 'color': '#95a5a6'}
            ]
            
            for category in default_categories:
                PollCategory.objects.get_or_create(
                    name=category['name'],
                    defaults={'color': category['color']}
                )
                
            print(f"Checked/created {len(default_categories)} default poll categories")


# Application startup signal (Django doesn't have a built-in one, so we create our own)
# You would need to call this manually in your AppConfig.ready() method
def application_startup():
    """Called when the application starts up"""
    print("ChaguaSmart application starting up")
    
    # Check for critical environment variables
    required_env_vars = ['SECRET_KEY', 'DEBUG']
    missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
    
    if missing_vars:
        logger.warning(f"Missing environment variables: {', '.join(missing_vars)}")
    
    # Initialize application cache
    cache_keys = ['active_polls', 'system_status']
    from django.core.cache import cache
    for key in cache_keys:
        cache.delete(key)
    
    # Set application status
    cache.set('system_status', {
        'status': 'online',
        'version': getattr(settings, 'APPLICATION_VERSION', '1.0.0'),
        'startup_time': time.time()
    }, timeout=None)  # No expiration
    
    print("ChaguaSmart application startup complete")


# You can add this to your AppConfig.ready() method:
"""
from config.signals import application_startup
application_startup()
"""