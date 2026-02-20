"""
Utility functions for DJ Control Room.
"""

from django.conf import settings
from django.urls import reverse
from django.apps import apps as django_apps
import logging

from .registry import registry
from .featured_panels import FEATURED_PANELS, get_featured_panel_ids, is_featured_panel

logger = logging.getLogger(__name__)


def should_register_panel_admin(panel_id=None):
    """
    Check if a panel should register its own admin entry.

    This allows end users to control whether panels show up in both
    DJ Control Room AND their own admin section, or only in DJ Control Room.

    Args:
        panel_id: The panel ID to check (optional, for granular control)

    Returns:
        bool: True if panel should register in admin, False otherwise

    Examples:
        # Simple boolean for all panels
        DJ_CONTROL_ROOM = {
            'REGISTER_PANELS_IN_ADMIN': True  # Panels show in both places
        }

        # Granular per-panel control
        DJ_CONTROL_ROOM = {
            'PANEL_ADMIN_REGISTRATION': {
                'redis': True,   # Redis shows in both places
                'cache': False,  # Cache only in Control Room
                '*': False,      # Default for others
            }
        }
    """
    config = getattr(settings, "DJ_CONTROL_ROOM", {})

    # Per-panel settings take precedence when provided (explicit allow/deny per panel)
    if panel_id and "PANEL_ADMIN_REGISTRATION" in config:
        panel_settings = config["PANEL_ADMIN_REGISTRATION"]
        if panel_id in panel_settings or "*" in panel_settings:
            return panel_settings.get(panel_id, panel_settings.get("*", False))

    # Global setting for all panels
    if "REGISTER_PANELS_IN_ADMIN" in config:
        return config["REGISTER_PANELS_IN_ADMIN"]

    # Default: don't register in admin (only show in Control Room)
    return False


def get_panel_config_status(panel_id, panel_app_name):
    """
    Return the configuration status for a panel broken down into its three
    independent conditions:

    - pip_installed     : the package's entry point is registered in the registry
    - in_installed_apps : the Django app is present in INSTALLED_APPS
    - urls_registered   : the panel's URL namespace can be reversed

    ``is_configured`` is True only when all three conditions hold.
    """
    installed_panel = registry.get_panel(panel_id)
    pip_installed = installed_panel is not None

    in_installed_apps = pip_installed and django_apps.is_installed(panel_app_name)

    urls_registered = False
    if pip_installed:
        try:
            url_name = getattr(installed_panel, "get_url_name", lambda: "index")()
            reverse(f"{panel_id}:{url_name}")
            urls_registered = True
        except Exception:
            pass

    return {
        "pip_installed": pip_installed,
        "in_installed_apps": in_installed_apps,
        "urls_registered": urls_registered,
        "is_configured": pip_installed and in_installed_apps and urls_registered,
        "installed_panel": installed_panel,
    }


def get_panel_data(panel):
    """
    Extract data from a registered panel instance.

    Args:
        panel: Panel instance from registry

    Returns:
        dict: Panel data dictionary
    """
    featured = is_featured_panel(panel.id)
    panel_app_name = panel.id  # entry point IDs match the Django app name
    config = get_panel_config_status(panel.id, panel_app_name)

    if config["urls_registered"]:
        url_name = getattr(panel, "get_url_name", lambda: "index")()
        url = reverse(f"{panel.id}:{url_name}")
    elif featured:
        url = reverse("dj_control_room:install_panel", args=[panel.id])
    else:
        url = "#"

    if not config["urls_registered"]:
        logger.warning(
            f"Panel '{panel.id}' is registered but its URLs could not be resolved. "
            "Make sure the panel is in INSTALLED_APPS and its URLs are included."
        )

    return {
        "id": panel.id,
        "name": panel.name,
        "description": panel.description,
        "icon": panel.icon,
        "url": url,
        "installed": True,
        "configured": config["is_configured"],
        "featured": featured,
    }


def get_featured_panels():
    """
    Get featured panels, marking which are installed.

    Returns:
        list: List of featured panel data with installation status
    """
    featured_panels = []

    for featured_meta in FEATURED_PANELS:
        panel_id = featured_meta["id"]

        installed_panel = registry.get_panel(panel_id)

        if installed_panel:
            panel_data = get_panel_data(installed_panel)
        else:
            coming_soon = featured_meta.get("coming_soon", False)
            panel_data = {
                "id": panel_id,
                "name": featured_meta["name"],
                "description": featured_meta["description"],
                "icon": featured_meta["icon"],
                "url": reverse("dj_control_room:install_panel", args=[panel_id]),
                "status": "coming_soon" if coming_soon else "not_installed",
                "status_label": "COMING SOON" if coming_soon else "NOT INSTALLED",
                "installed": False,
                "configured": False,
                "coming_soon": coming_soon,
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
            community_panels.append(get_panel_data(panel))

    return community_panels
