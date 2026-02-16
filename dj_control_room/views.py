from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.contrib import admin
from django.urls import reverse
import logging

from .registry import registry
from .featured_panels import FEATURED_PANELS, get_featured_panel_ids, is_featured_panel

logger = logging.getLogger(__name__)


def get_panel_data(panel):
    """
    Extract data from a registered panel instance.
    
    Args:
        panel: Panel instance from registry
        
    Returns:
        dict: Panel data dictionary
    """
    try:
        # Get the panel's URL
        url = panel.get_url()
        
        # Get the panel's status
        status_info = panel.get_status()
        
        # Build panel data
        return {
            "id": panel.id,
            "name": panel.name,
            "description": panel.description,
            "icon": panel.icon,
            "url": url,
            "status": status_info.get("status", "unknown"),
            "status_label": status_info.get("status_label", "UNKNOWN"),
            "installed": True,
            "featured": is_featured_panel(panel.id),
        }
        
    except Exception as e:
        logger.error(
            f"Error loading panel '{panel.id}': {e}",
            exc_info=True
        )
        # Still show the panel but with error status
        return {
            "id": panel.id,
            "name": panel.name,
            "description": panel.description,
            "icon": panel.icon,
            "url": "#",
            "status": "error",
            "status_label": "ERROR",
            "installed": True,
            "featured": is_featured_panel(panel.id),
        }


def get_featured_panels():
    """
    Get featured panels, marking which are installed.
    
    Returns:
        list: List of featured panel data with installation status
    """
    featured_panel_ids = get_featured_panel_ids()
    featured_panels = []
    
    for featured_meta in FEATURED_PANELS:
        panel_id = featured_meta["id"]
        
        # Check if this featured panel is actually installed
        installed_panel = registry.get_panel(panel_id)
        
        if installed_panel:
            # Panel is installed - use real data
            panel_data = get_panel_data(installed_panel)
        else:
            # Panel not installed - use metadata and link to marketing page
            panel_data = {
                "id": panel_id,
                "name": featured_meta["name"],
                "description": featured_meta["description"],
                "icon": featured_meta["icon"],
                "url": reverse('dj_control_room:install_panel', args=[panel_id]),
                "status": "not_installed",
                "status_label": "NOT INSTALLED",
                "installed": False,
                "featured": True,
                "package": featured_meta["package"],
                "docs_url": featured_meta.get("docs_url"),
                "pypi_url": featured_meta.get("pypi_url"),
            }
        
        featured_panels.append(panel_data)
    
    return featured_panels


def get_community_panels():
    """
    Get community (non-featured) panels.
    
    Returns:
        list: List of community panel data
    """
    featured_ids = get_featured_panel_ids()
    community_panels = []
    
    for panel in registry.get_panels():
        if panel.id not in featured_ids:
            panel_data = get_panel_data(panel)
            community_panels.append(panel_data)
    
    return community_panels


@staff_member_required
def index(request):
    """
    Display panel dashboard.
    
    Shows featured panels first (with install prompts if not installed),
    followed by community panels.
    """
    context = admin.site.each_context(request)
    
    featured_panels = get_featured_panels()
    community_panels = get_community_panels()

    context.update({
        "title": "",
        "featured_panels": featured_panels,
        "community_panels": community_panels,
        "has_community_panels": len(community_panels) > 0,
    })
    
    return render(request, "admin/dj_control_room/index.html", context)


@staff_member_required
def install_panel(request, panel_id):
    """
    Marketing/installation page for uninstalled featured panels.
    
    Shows information about the panel and how to install it.
    Uses panel-specific template if available, otherwise falls back to generic.
    """
    from django.shortcuts import redirect
    from django.template.loader import get_template
    from django.template import TemplateDoesNotExist
    from django.http import HttpResponse
    from .featured_panels import get_featured_panel_metadata
    
    context = admin.site.each_context(request)
    
    # Get featured panel metadata
    panel_meta = get_featured_panel_metadata(panel_id)
    
    if not panel_meta:
        # Not a featured panel, redirect to dashboard
        return redirect('dj_control_room:index')
    
    # Check if panel is actually installed
    installed_panel = registry.get_panel(panel_id)
    
    context.update({
        "title": f"Install {panel_meta['name']}",
        "panel": panel_meta,
        "is_installed": installed_panel is not None,
        "panel_url": installed_panel.get_url() if installed_panel else None,
    })
    
    # Try to load panel-specific template first, fall back to generic
    template_name = f"admin/dj_control_room/install_panel_{panel_id}.html"
    try:
        template = get_template(template_name)
    except TemplateDoesNotExist:
        template_name = "admin/dj_control_room/install_panel.html"
        template = get_template(template_name)
    
    return HttpResponse(template.render(context, request))
