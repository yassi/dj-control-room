from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.contrib import admin


def get_installed_panels():
    """
    Return list of installed panels with their metadata.
    This will eventually query the registry of installed panel apps.
    """
    # Mock data for now - these will be dynamically discovered from installed apps
    panels = [
        {
            "id": "redis",
            "name": "Redis Panel",
            "description": "Monitor connections, memory, keys, and throughput.",
            "icon": "database",
            "status": "connected",
            "status_label": "CONNECTED",
            "url": "#",  # Will be reverse('redis_panel:index') when integrated
            "installed": True,
        },
        {
            "id": "cache",
            "name": "Cache Panel",
            "description": "Inspect cached entries, hit/miss ratios.",
            "icon": "layers",
            "status": "healthy",
            "status_label": "HEALTHY",
            "url": "#",
            "installed": True,
        },
        {
            "id": "celery",
            "name": "Celery Panel",
            "description": "Track workers, monitor task queues.",
            "icon": "chart",
            "status": "connected",
            "status_label": "CONNECTED",
            "url": "#",
            "installed": True,
        },
        {
            "id": "urls",
            "name": "URLs Panel",
            "description": "Browse registered URL patterns.",
            "icon": "link",
            "status": "healthy",
            "status_label": "HEALTHY",
            "url": "#",
            "installed": True,
        },
        {
            "id": "signals",
            "name": "Signals Panel",
            "description": "Inspect connected signal receivers.",
            "icon": "radio",
            "status": "connected",
            "status_label": "CONNECTED",
            "url": "#",
            "installed": True,
        },
        {
            "id": "errors",
            "name": "Errors Panel",
            "description": "Track recent exceptions, tracebacks.",
            "icon": "alert",
            "status": "healthy",
            "status_label": "HEALTHY",
            "url": "#",
            "installed": True,
        },
    ]
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
