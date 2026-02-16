from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import DjControlRoomDashboard


@admin.register(DjControlRoomDashboard)
class DjControlRoomDashboardAdmin(admin.ModelAdmin):
    """
    Admin entry for the DJ Control Room dashboard.
    
    This shows up first in the DJ Control Room section of the admin sidebar.
    Individual panels are registered dynamically via admin_integration.py
    """
    def changelist_view(self, request, extra_context=None):
        # Redirect to the main Control Room dashboard
        return HttpResponseRedirect(reverse("dj_control_room:index"))

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        # Allow staff members to "view" the dashboard
        return request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        # Allow staff members to view the dashboard
        return request.user.is_staff
