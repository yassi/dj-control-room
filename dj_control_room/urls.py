from django.urls import path, include
from . import views


def get_panel_urls():
    """
    Dynamically generate URL patterns for all registered panels.
    
    Each panel that implements get_urls() will have its URLs
    automatically mounted under /admin/dj-control-room/{panel_id}/
    
    Returns:
        list: URL patterns for all registered panels
    """
    from .registry import registry
    
    # Force autodiscovery if not already done
    if not registry._discovered:
        registry.autodiscover()
    
    panel_patterns = []
    
    for panel in registry.get_panels():
        # Check if panel provides URL patterns
        if hasattr(panel, 'get_urls') and callable(panel.get_urls):
            try:
                panel_urls = panel.get_urls()
                if panel_urls:
                    # Include panel URLs with its own namespace
                    panel_patterns.append(
                        path(f'{panel.id}/', include((panel_urls, panel.id)))
                    )
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(
                    f"Failed to include URLs for panel '{panel.id}': {e}",
                    exc_info=True
                )
    
    return panel_patterns


app_name = "dj_control_room"

urlpatterns = [
    path("", views.index, name="index"),
]

# Dynamically add panel URLs
urlpatterns += get_panel_urls()
