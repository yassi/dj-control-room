"""
Featured panels - curated panels created by DJ Control Room.

These panels are always shown in the dashboard, even if not installed.
If not installed, they show a marketing page with installation instructions.
"""

FEATURED_PANELS = [
    {
        "id": "dj_redis_panel",
        "name": "Redis Panel",
        "description": "Monitor connections, memory, keys, and throughput.",
        "icon": "database",
        "package": "dj-redis-panel",
        "docs_url": "https://github.com/yassi/dj-redis-panel",
        "pypi_url": "https://pypi.org/project/dj-redis-panel/",
    },
    {
        "id": "dj_cache_panel",
        "name": "Cache Panel",
        "description": "Inspect cached entries, hit/miss ratios.",
        "icon": "layers",
        "package": "dj-cache-panel",
        "docs_url": "https://github.com/yassi/dj-cache-panel",
        "pypi_url": "https://pypi.org/project/dj-cache-panel/",
    },
    {
        "id": "dj_celery_panel",
        "name": "Celery Panel",
        "description": "Track workers, monitor task queues.",
        "icon": "chart",
        "package": "dj-celery-panel",
        "docs_url": "https://github.com/yassi/dj-celery-panel",
        "pypi_url": "https://pypi.org/project/dj-celery-panel/",
    },
    {
        "id": "dj_urls_panel",
        "name": "URLs Panel",
        "description": "Browse registered URL patterns.",
        "icon": "link",
        "package": "dj-urls-panel",
        "docs_url": "https://github.com/yassi/dj-urls-panel",
        "pypi_url": "https://pypi.org/project/dj-urls-panel/",
    },
    {
        "id": "dj_signals_panel",
        "name": "Signals Panel",
        "description": "Monitor signals, debug connections.",
        "icon": "link",
        "coming_soon": True,
        "package": "dj-signals-panel",
        "docs_url": "https://github.com/yassi/dj-signals-panel",
        "pypi_url": "https://pypi.org/project/dj-signals-panel/",
    },
    {
        "id": "dj_error _panel",
        "name": "Error Panel",
        "description": "Monitor errors, stack traces, and exceptions.",
        "icon": "link",
        "coming_soon": True,
        "package": "dj-error-panel",
        "docs_url": "https://github.com/yassi/dj-error-panel",
        "pypi_url": "https://pypi.org/project/dj-error-panel/",
    },
]


def get_featured_panel_ids():
    """
    Get list of featured panel IDs.

    Returns:
        list: List of panel IDs
    """
    return [panel["id"] for panel in FEATURED_PANELS]


def get_featured_panel_metadata(panel_id):
    """
    Get metadata for a featured panel.

    Args:
        panel_id: The panel ID to look up

    Returns:
        dict: Panel metadata or None if not found
    """
    for panel in FEATURED_PANELS:
        if panel["id"] == panel_id:
            return panel
    return None


def is_featured_panel(panel_id):
    """
    Check if a panel ID is a featured panel.

    Args:
        panel_id: The panel ID to check

    Returns:
        bool: True if featured panel
    """
    return panel_id in get_featured_panel_ids()
