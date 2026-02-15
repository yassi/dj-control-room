from django.apps import AppConfig


class DjControlRoomConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "dj_control_room"
    verbose_name = "DJ Control Room"
    
    def ready(self):
        """
        Initialize the panel registry when the app is ready.
        
        This discovers all panels registered via entry points.
        """
        from .registry import registry
        registry.autodiscover()
