from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.contrib import admin


@staff_member_required
def index(request):
    """
    Display panel dashboard.
    """
    context = admin.site.each_context(request)
    context.update(
        {
            "title": "DJ Control Room",
        }
    )
    return render(request, "admin/dj_control_room/index.html", context)
