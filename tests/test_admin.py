"""
Tests for Django Admin integration with DJ Control Room.

The DJ Control Room integrates with Django Admin through a placeholder model
that appears in the admin interface and redirects to the Panel when clicked.
"""

from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from .base import CeleryPanelTestCase


User = get_user_model()


class TestAdminIntegration(CeleryPanelTestCase):
    """Test cases for Django Admin integration."""

    def test_celery_panel_appears_in_admin_index(self):
        """Test that DJ Control Room appears in the Django admin index page."""
        response = self.client.get("/admin/")

        self.assertEqual(response.status_code, 200)
        # Check for the app name and model
        self.assertContains(response, "dj_control_room")

        # Check that the link to the dashboard changelist exists
        changelist_url = reverse(
            "admin:dj_control_room_djcontrolroomdashboard_changelist"
        )
        self.assertContains(response, changelist_url)

    def test_celery_panel_changelist_redirects_to_index(self):
        """Test that clicking DJ Control Room Dashboard in admin redirects to the dashboard."""
        changelist_url = reverse(
            "admin:dj_control_room_djcontrolroomdashboard_changelist"
        )
        response = self.client.get(changelist_url)

        # Should redirect to the Control Room dashboard
        self.assertEqual(response.status_code, 302)
        expected_url = reverse("dj_control_room:index")
        self.assertRedirects(response, expected_url)

    def test_unauthenticated_user_cannot_access_admin_celery_panel(self):
        """Test that unauthenticated users cannot access DJ Control Room through admin."""
        client = Client()
        changelist_url = reverse(
            "admin:dj_control_room_djcontrolroomdashboard_changelist"
        )
        response = client.get(changelist_url)

        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response.url)

    def test_non_staff_user_cannot_access_admin_celery_panel(self):
        """Test that non-staff users cannot access DJ Control Room through admin."""
        # Create a non-staff user
        user = User.objects.create_user(
            username="regular_user", password="testpass123", is_staff=False
        )

        client = Client()
        client.force_login(user)

        changelist_url = reverse(
            "admin:dj_control_room_djcontrolroomdashboard_changelist"
        )
        response = client.get(changelist_url)

        # Should redirect to login page or show permission denied
        self.assertIn(response.status_code, [302, 403])
