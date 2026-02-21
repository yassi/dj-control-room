from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from django.http import HttpResponse
from django.contrib import admin
from django.urls import reverse

from .featured_panels import get_featured_panel_metadata
from .registry import registry
from .utils import get_panel_config_status, get_featured_panels, get_community_panels


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

    context.update(
        {
            "title": "",
            "featured_panels": featured_panels,
            "community_panels": community_panels,
            "has_community_panels": len(community_panels) > 0,
        }
    )

    return render(request, "admin/dj_control_room/index.html", context)


@staff_member_required
def install_panel(request, panel_id):
    """
    Installation guide page for featured panels.

    Shows the panel's features and step-by-step configuration instructions.
    Accessible whether or not the panel is currently installed/configured.
    Uses a panel-specific template if available, otherwise falls back to generic.
    """
    context = admin.site.each_context(request)

    panel_meta = get_featured_panel_metadata(panel_id)

    if not panel_meta:
        # Not a featured panel — check if it's a registered community panel
        # that has declared enough metadata to render the install page.
        community_panel = registry.get_panel(panel_id)
        if community_panel:
            panel_meta = {
                "id": community_panel._registry_id,
                "name": community_panel.name,
                "description": community_panel.description,
                "icon": community_panel.icon,
                "package": community_panel.package,
                "docs_url": getattr(community_panel, "docs_url", None),
                "pypi_url": getattr(community_panel, "pypi_url", None),
            }
        else:
            return redirect("dj_control_room:index")

    # app_name is stamped onto every installed panel by the registry at
    # discovery time. For uninstalled featured panels, fall back to deriving
    # it from the package name (hyphens → underscores).
    installed_panel = registry.get_panel(panel_id)
    panel_app_name = getattr(installed_panel, "app_name", None) or panel_meta[
        "package"
    ].replace("-", "_")

    config = get_panel_config_status(panel_id, panel_app_name)

    # config["installed_panel"] is the same object we may have already fetched
    # above, but we use the config value to stay consistent.
    panel_instance = config["installed_panel"]
    panel_url = None
    if config["urls_registered"] and panel_instance:
        try:
            url_name = getattr(panel_instance, "get_url_name", lambda: "index")()
            panel_url = reverse(f"{panel_app_name}:{url_name}")
        except Exception:
            pass

    context.update(
        {
            "panel": panel_meta,
            "is_installed": config["pip_installed"],
            "is_in_installed_apps": config["in_installed_apps"],
            "is_configured": config["is_configured"],
            "panel_url": panel_url,
            "panel_url_prefix": f"admin/{panel_id}",
            "panel_app_name": panel_app_name,
        }
    )

    template_name = f"admin/dj_control_room/install_panel_{panel_id}.html"
    try:
        template = get_template(template_name)
    except TemplateDoesNotExist:
        template_name = "admin/dj_control_room/install_panel.html"
        template = get_template(template_name)

    return HttpResponse(template.render(context, request))
