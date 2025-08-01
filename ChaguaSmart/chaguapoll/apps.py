from django.apps import AppConfig


class ChaguapollConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chaguapoll'
    verbose_name = 'ChaguaSmart Polling System'
    
    def ready(self):
        """
        Called when Django starts up.
        This is where you can register signals, perform initialization, etc.
        """
        # Import signals if you have any
        try:
            import chaguapoll.signals
        except ImportError:
            pass
        
        # You can add any other initialization code here
        # For example, registering custom checks, etc.