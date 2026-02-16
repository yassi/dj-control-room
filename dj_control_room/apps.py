from django.apps import AppConfig


class DjControlRoomConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "dj_control_room"
    verbose_name = "DJ Control Room"
    
    def ready(self):
        """
        Initialize the panel registry and register admin entries.
        
        This discovers all panels registered via entry points and
        automatically creates admin sidebar entries for them.
        
        All panels will appear grouped under "DJ Control Room" in the
        Django admin sidebar.
        """
        from .registry import registry
        from .admin_integration import register_panel_admins
        
        # First, discover all panels via entry points
        registry.autodiscover()
        
        # Then, dynamically register admin entries for each discovered panel
        # This creates proxy models with app_label='dj_control_room' so they
        # all appear together in the admin sidebar
        register_panel_admins()
