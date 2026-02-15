from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.contrib import admin
import logging

from .registry import registry

logger = logging.getLogger(__name__)


def get_installed_panels():
    """
    Return list of installed panels with their metadata.
    
    Discovers panels via the registry which uses Python entry points.
    Each panel provides its own metadata, URL, and status.
    
    Returns:
        list: List of panel data dictionaries with keys:
            - id: Unique panel identifier
            - name: Display name
            - description: Panel description
            - icon: Icon identifier
            - url: URL to access the panel
            - status: Status code (e.g., 'connected', 'healthy', 'error')
            - status_label: Display label for status (e.g., 'CONNECTED')
    """
    panels = []
    
    for panel in registry.get_panels():
        try:
            # Get the panel's URL
            url = panel.get_url()
            
            # Get the panel's status
            status_info = panel.get_status()
            
            # Build panel data
            panel_data = {
                "id": panel.id,
                "name": panel.name,
                "description": panel.description,
                "icon": panel.icon,
                "url": url,
                "status": status_info.get("status", "unknown"),
                "status_label": status_info.get("status_label", "UNKNOWN"),
            }
            
            panels.append(panel_data)
            
        except Exception as e:
            logger.error(
                f"Error loading panel '{panel.id}': {e}",
                exc_info=True
            )
            # Still show the panel but with error status
            panels.append({
                "id": panel.id,
                "name": panel.name,
                "description": panel.description,
                "icon": panel.icon,
                "url": "#",
                "status": "error",
                "status_label": "ERROR",
            })
    
    return panels


@staff_member_required
def index(request):
    """
    Display panel dashboard.
    """
    context = admin.site.each_context(request)
    panels = get_installed_panels()

    context.update(
        {
            "title": "",
            "panels": panels,
        }
    )
    return render(request, "admin/dj_control_room/index.html", context)
