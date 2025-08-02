from django.apps import AppConfig


class ConfigConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'config'

    def ready(self):
        # Import signals
        import config.signals
        
        # Call application startup handler
        from config.signals import application_startup
        application_startup()