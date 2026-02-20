from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from django.http import HttpResponse
from django.contrib import admin
from django.urls import reverse

from .featured_panels import get_featured_panel_metadata
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
        return redirect("dj_control_room:index")

    panel_app_name = panel_meta["package"].replace("-", "_")
    config = get_panel_config_status(panel_id, panel_app_name)

    installed_panel = config["installed_panel"]
    panel_url = None
    if config["urls_registered"] and installed_panel:
        try:
            url_name = getattr(installed_panel, "get_url_name", lambda: "index")()
            panel_url = reverse(f"{installed_panel.id}:{url_name}")
        except Exception:
            pass

    context.update(
        {
            "title": f"Install {panel_meta['name']}",
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
