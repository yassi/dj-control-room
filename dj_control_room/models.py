from django.db import models


class DjControlRoomDashboard(models.Model):
    """
    Proxy model for the DJ Control Room dashboard entry in admin.
    
    This creates the main "Dashboard" entry in the admin sidebar.
    Individual panels are registered dynamically via admin_integration.py
    """

    class Meta:
        managed = False
        verbose_name = " 🚀 Dashboard"
        verbose_name_plural = " 🚀 Dashboard"
        app_label = "dj_control_room"
