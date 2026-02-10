"""
Base test class for dj-control-room tests.
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model


User = get_user_model()


class CeleryPanelTestCase(TestCase):
    """
    Base test case for DJ Control Room tests.
    Sets up authenticated admin user for testing.
    """

    def setUp(self):
        """Set up test fixtures."""
        # Create a staff user for admin access
        self.user = User.objects.create_user(
            username="admin",
            password="testpass123",
            is_staff=True,
            is_superuser=True,
        )

        # Create authenticated client
        self.client = Client()
        self.client.force_login(self.user)

    def tearDown(self):
        """Clean up after tests."""
        pass
