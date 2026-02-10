"""
Pytest configuration for DJ Control Room tests.

This configuration enables pytest-django to work with Django TestCase classes.
"""

import os
import sys
import django
from django.conf import settings


def pytest_configure(config):
    """Configure Django for pytest."""
    # Add the example_project directory to Python path for Django settings
    example_project_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "example_project"
    )
    if example_project_path not in sys.path:
        sys.path.insert(0, example_project_path)

    # Set TEST_DB_BACKEND environment variable (defaults to sqlite for local development)
    test_db_backend = os.environ.get("TEST_DB_BACKEND", "sqlite").lower()

    # Configure DB_ENGINE for the example_project settings to use
    # This must be set BEFORE Django setup
    if test_db_backend == "postgresql":
        os.environ.setdefault("DB_ENGINE", "postgresql")
        # Set PostgreSQL connection defaults for tests
        os.environ.setdefault("POSTGRES_HOST", "localhost")
        os.environ.setdefault("POSTGRES_PORT", "5432")
        os.environ.setdefault("POSTGRES_USER", "postgres")
        os.environ.setdefault("POSTGRES_PASSWORD", "postgres")
        os.environ.setdefault("POSTGRES_DB", "postgres")
    else:
        os.environ.setdefault("DB_ENGINE", "sqlite")

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "example_project.settings")

    if not settings.configured:
        django.setup()
