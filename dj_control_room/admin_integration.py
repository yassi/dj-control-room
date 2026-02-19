"""
Dynamic admin integration for DJ Control Room panels.

Automatically registers admin entries for all discovered panels,
grouped under the "DJ Control Room" app in the admin sidebar.
"""
import logging
from django.contrib import admin
from django.db import models
from django.http import HttpResponseRedirect
from django.urls import reverse

from .registry import registry

logger = logging.getLogger(__name__)


def register_panel_admins():
    """
    Dynamically register admin entries for all discovered panels.
    
    Creates a proxy model and admin class for each panel, allowing them
    to appear in the Django admin sidebar under "DJ Control Room".
    
    Each panel entry redirects to the panel's URL when clicked.
    """
    # Discover all panels first
    registry.autodiscover()
    
    for panel in registry.get_panels():
        try:
            _register_panel_admin(panel)
        except Exception as e:
            logger.error(
                f"Failed to register admin for panel '{panel.id}': {e}",
                exc_info=True
            )


def _register_panel_admin(panel):
    """
    Register a single panel in the admin.
    
    Args:
        panel: The panel instance to register
    """
    # Create a safe model name from the panel ID
    # e.g., 'redis' -> 'RedisPanel', 'my-panel' -> 'MyPanelPanel'
    model_name = f"{panel.id.replace('-', '').replace('_', '').title()}PanelProxy"
    
    # Check if already registered
    try:
        existing_model = admin.site._registry
        for model in existing_model.keys():
            if model.__name__ == model_name:
                logger.debug(f"Panel proxy model {model_name} already registered, skipping")
                return
    except Exception:
        pass
    
    # Create the proxy model class dynamically
    model_attrs = {
        '__module__': 'dj_control_room.models',
        'Meta': type('Meta', (), {
            'managed': False,  # Don't create database table
            'verbose_name': panel.name,
            'verbose_name_plural': panel.name,
            'app_label': 'dj_control_room',  # Key: groups under DJ Control Room
        })
    }
    
    model_class = type(model_name, (models.Model,), model_attrs)
    
    # Get the URL name from the panel (default to "index" if method missing)
    url_name = getattr(panel, 'get_url_name', lambda: 'index')()
    
    # Build the panel URL using reverse
    panel_url = reverse(f'{panel.id}:{url_name}')
    
    # Create the admin class that redirects to the panel URL
    def make_changelist_view(panel_url):
        """Create a changelist view that redirects to the panel."""
        def changelist_view(self, request, extra_context=None):
            return HttpResponseRedirect(panel_url)
        return changelist_view
    
    admin_attrs = {
        'changelist_view': make_changelist_view(panel_url),
        'has_add_permission': lambda self, request: False,
        'has_change_permission': lambda self, request, obj=None: request.user.is_staff,
        'has_delete_permission': lambda self, request, obj=None: False,
        'has_view_permission': lambda self, request, obj=None: request.user.is_staff,
    }
    
    admin_class_name = f"{model_name}Admin"
    admin_class = type(admin_class_name, (admin.ModelAdmin,), admin_attrs)
    
    # Register it with the admin site
    admin.site.register(model_class, admin_class)
    
    logger.info(f"Registered admin entry for panel '{panel.id}' ({panel.name})")
