"""
Tests for DJ Control Room utility functions.

Covers:
- get_panel_config_status: correct pip_installed / in_installed_apps /
  urls_registered breakdown
- get_panel_data: id field comes from _registry_id, not panel.id; package
  is always populated (stamped from dist.name when not explicit)
- get_community_panels: filters out featured panels, returns only community
- get_featured_panels: uninstalled featured panels carry their metadata
- should_register_panel_admin: global and per-panel settings respected
"""

from unittest.mock import patch, MagicMock

from django.test import TestCase, override_settings
from django.urls import reverse

from dj_control_room.registry import PanelRegistry
from dj_control_room.utils import (
    get_community_panels,
    get_featured_panels,
    get_panel_config_status,
    get_panel_data,
    should_register_panel_admin,
)


# ---------------------------------------------------------------------------
# Helper: build a minimal panel instance the way the registry stamps it
# ---------------------------------------------------------------------------

def _make_panel(registry_id, app_name=None, package=None, name="Test Panel",
                description="Test desc", icon="chart",
                docs_url=None, pypi_url=None):
    """Return a plain object that mimics a registry-stamped panel instance."""
    obj = MagicMock()
    obj._registry_id = registry_id
    obj.app_name = app_name or registry_id
    obj.package = package or registry_id
    obj.name = name
    obj.description = description
    obj.icon = icon
    obj.docs_url = docs_url
    obj.pypi_url = pypi_url
    obj.get_url_name = MagicMock(return_value="index")
    return obj


# ---------------------------------------------------------------------------
# get_panel_config_status
# ---------------------------------------------------------------------------

class TestGetPanelConfigStatus(TestCase):

    def test_not_installed_when_panel_not_in_registry(self):
        status = get_panel_config_status("nonexistent_panel", "nonexistent_panel")
        self.assertFalse(status["pip_installed"])
        self.assertFalse(status["in_installed_apps"])
        self.assertFalse(status["urls_registered"])
        self.assertFalse(status["is_configured"])
        self.assertIsNone(status["installed_panel"])

    def test_pip_installed_true_when_panel_registered(self):
        # dj_cache_panel is installed in the test environment via entry point
        status = get_panel_config_status("dj_cache_panel", "dj_cache_panel")
        self.assertTrue(status["pip_installed"])
        self.assertIsNotNone(status["installed_panel"])

    def test_in_installed_apps_reflects_settings(self):
        # dj_cache_panel is in INSTALLED_APPS in the test settings
        status = get_panel_config_status("dj_cache_panel", "dj_cache_panel")
        self.assertTrue(status["in_installed_apps"])

    def test_is_configured_requires_all_three(self):
        # A panel that is installed but has no URLs would have is_configured=False
        status = get_panel_config_status("nonexistent_panel", "nonexistent_panel")
        self.assertFalse(status["is_configured"])


# ---------------------------------------------------------------------------
# get_panel_data
# ---------------------------------------------------------------------------

class TestGetPanelData(TestCase):

    def test_id_field_comes_from_registry_id(self):
        """get_panel_data must use _registry_id, not any panel.id attribute."""
        panel = _make_panel("dist_derived_id")
        # Simulate a panel that still declares the old id attribute
        panel.id = "old_id_that_should_be_ignored"

        with patch("dj_control_room.utils.is_featured_panel", return_value=False), \
             patch("dj_control_room.utils.get_panel_config_status") as mock_cfg, \
             patch("dj_control_room.utils.reverse", return_value="/install/x/"):
            mock_cfg.return_value = {
                "is_configured": False,
                "pip_installed": True,
                "in_installed_apps": False,
                "urls_registered": False,
                "installed_panel": panel,
            }
            data = get_panel_data(panel)

        self.assertEqual(data["id"], "dist_derived_id")

    def test_package_always_present_in_data(self):
        """package is always included in the panel data dict."""
        panel = _make_panel("my_panel", package="my-panel")

        with patch("dj_control_room.utils.is_featured_panel", return_value=False), \
             patch("dj_control_room.utils.get_panel_config_status") as mock_cfg, \
             patch("dj_control_room.utils.reverse", return_value="/install/x/"):
            mock_cfg.return_value = {
                "is_configured": False,
                "pip_installed": True,
                "in_installed_apps": False,
                "urls_registered": False,
                "installed_panel": panel,
            }
            data = get_panel_data(panel)

        self.assertEqual(data["package"], "my-panel")

    def test_configured_panel_url_uses_app_name_namespace(self):
        """When configured, the URL is resolved using panel.app_name."""
        panel = _make_panel("my_panel", app_name="my_panel")

        with patch("dj_control_room.utils.is_featured_panel", return_value=False), \
             patch("dj_control_room.utils.get_panel_config_status") as mock_cfg, \
             patch("dj_control_room.utils.reverse",
                   return_value="/admin/dj-control-room/my-panel/") as mock_reverse:
            mock_cfg.return_value = {
                "is_configured": True,
                "pip_installed": True,
                "in_installed_apps": True,
                "urls_registered": True,
                "installed_panel": panel,
            }
            data = get_panel_data(panel)

        # When configured, reverse is called with the panel's app_name namespace
        mock_reverse.assert_called_once_with("my_panel:index")
        # URL should be the resolved panel URL, not the install page
        self.assertNotIn("install", data["url"])

    def test_unconfigured_panel_url_is_install_page(self):
        """Unconfigured panels link to their install/configure page."""
        panel = _make_panel("community_panel")

        with patch("dj_control_room.utils.is_featured_panel", return_value=False), \
             patch("dj_control_room.utils.get_panel_config_status") as mock_cfg, \
             patch("dj_control_room.utils.reverse",
                   return_value="/admin/dj-control-room/install/community_panel/"):
            mock_cfg.return_value = {
                "is_configured": False,
                "pip_installed": True,
                "in_installed_apps": False,
                "urls_registered": False,
                "installed_panel": panel,
            }
            data = get_panel_data(panel)

        self.assertIn("install", data["url"])


# ---------------------------------------------------------------------------
# get_community_panels
# ---------------------------------------------------------------------------

class TestGetCommunityPanels(TestCase):

    def test_featured_panels_excluded(self):
        """get_community_panels must not include featured panels."""
        with patch("dj_control_room.utils.registry") as mock_reg, \
             patch("dj_control_room.utils.get_featured_panel_ids",
                   return_value=["dj_cache_panel", "dj_redis_panel"]):
            featured = _make_panel("dj_cache_panel", name="Cache Panel")
            community = _make_panel("my_community_panel", name="Community Panel")
            mock_reg.get_panels.return_value = [featured, community]

            with patch("dj_control_room.utils.get_panel_data",
                       side_effect=lambda p: {"id": p._registry_id}):
                result = get_community_panels()

        ids = [r["id"] for r in result]
        self.assertNotIn("dj_cache_panel", ids)
        self.assertIn("my_community_panel", ids)

    def test_only_community_panels_returned(self):
        with patch("dj_control_room.utils.registry") as mock_reg, \
             patch("dj_control_room.utils.get_featured_panel_ids",
                   return_value=["dj_cache_panel"]):
            mock_reg.get_panels.return_value = [
                _make_panel("dj_cache_panel"),
                _make_panel("panel_a"),
                _make_panel("panel_b"),
            ]
            with patch("dj_control_room.utils.get_panel_data",
                       side_effect=lambda p: {"id": p._registry_id}):
                result = get_community_panels()

        self.assertEqual(len(result), 2)


# ---------------------------------------------------------------------------
# get_featured_panels
# ---------------------------------------------------------------------------

class TestGetFeaturedPanels(TestCase):

    def test_uninstalled_featured_panel_has_not_installed_status(self):
        """Featured panels that aren't pip-installed show as not installed."""
        with patch("dj_control_room.utils.registry") as mock_reg:
            # Return None for all panels (nothing installed)
            mock_reg.get_panel.return_value = None
            panels = get_featured_panels()

        not_installed = [p for p in panels if not p["installed"]]
        self.assertTrue(len(not_installed) > 0)
        for p in not_installed:
            self.assertFalse(p["configured"])
            self.assertIn("package", p)
            self.assertIn("name", p)


# ---------------------------------------------------------------------------
# should_register_panel_admin
# ---------------------------------------------------------------------------

class TestShouldRegisterPanelAdmin(TestCase):

    @override_settings(DJ_CONTROL_ROOM={})
    def test_default_is_false(self):
        self.assertFalse(should_register_panel_admin())

    @override_settings(DJ_CONTROL_ROOM={"REGISTER_PANELS_IN_ADMIN": True})
    def test_global_true(self):
        self.assertTrue(should_register_panel_admin())

    @override_settings(DJ_CONTROL_ROOM={"REGISTER_PANELS_IN_ADMIN": False})
    def test_global_false(self):
        self.assertFalse(should_register_panel_admin())

    @override_settings(DJ_CONTROL_ROOM={
        "PANEL_ADMIN_REGISTRATION": {"my_panel": True, "*": False}
    })
    def test_per_panel_override_true(self):
        self.assertTrue(should_register_panel_admin("my_panel"))

    @override_settings(DJ_CONTROL_ROOM={
        "PANEL_ADMIN_REGISTRATION": {"my_panel": False, "*": True}
    })
    def test_per_panel_override_false(self):
        self.assertFalse(should_register_panel_admin("my_panel"))

    @override_settings(DJ_CONTROL_ROOM={
        "PANEL_ADMIN_REGISTRATION": {"*": True}
    })
    def test_wildcard_applies_to_unknown_panel(self):
        self.assertTrue(should_register_panel_admin("some_other_panel"))

    @override_settings(DJ_CONTROL_ROOM={
        "PANEL_ADMIN_REGISTRATION": {"*": False}
    })
    def test_wildcard_false_applies_to_unknown_panel(self):
        self.assertFalse(should_register_panel_admin("some_other_panel"))
