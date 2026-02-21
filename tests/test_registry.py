"""
Tests for the PanelRegistry — the core of DJ Control Room's plugin system.

Key behaviours covered:
- registry key is derived from dist.name (autodiscovery) or explicit panel_id
  (manual registration); the panel's `id` attribute is silently ignored
- _registry_id, app_name, and package are stamped onto every panel instance
- app_name and package fall back to panel_id when not declared on the class
- explicit app_name / package declared on the class are preserved
- duplicate panel_ids: first registration wins, second is dropped
- missing required attributes (name, description, icon) raise ValueError
- `id` attribute is no longer required; declaring it causes no error
- two panels with the same `id=` value but different panel_ids both register
- get_panels(), get_panel(), is_registered(), clear() work correctly
- _normalize_package_name converts hyphens to underscores and lowercases
"""

from django.test import TestCase

from dj_control_room.registry import PanelRegistry, _normalize_package_name


# ---------------------------------------------------------------------------
# Reusable panel fixtures
# ---------------------------------------------------------------------------

class MinimalPanel:
    name = "Minimal Panel"
    description = "A minimal test panel"
    icon = "chart"


class PanelWithAppName:
    name = "Panel With App Name"
    description = "Has an explicit app_name"
    icon = "database"
    app_name = "custom_app"


class PanelWithPackage:
    name = "Panel With Package"
    description = "Has an explicit package"
    icon = "layers"
    package = "my-custom-package"


class PanelWithBoth:
    name = "Panel With Both"
    description = "Has both app_name and package"
    icon = "link"
    app_name = "explicit_app"
    package = "explicit-package"


class PanelWithOldId:
    """Panel that still declares the legacy id attribute — must be ignored."""
    id = "some_old_id"
    name = "Old ID Panel"
    description = "Has a legacy id attribute"
    icon = "radio"


class PanelWithUrlName:
    name = "URL Name Panel"
    description = "Has get_url_name"
    icon = "link"

    def get_url_name(self):
        return "dashboard"


class MissingNamePanel:
    description = "No name attribute"
    icon = "chart"


class MissingDescriptionPanel:
    name = "No Description"
    icon = "chart"


class MissingIconPanel:
    name = "No Icon"
    description = "Missing icon attribute"


# ---------------------------------------------------------------------------
# Manual registration
# ---------------------------------------------------------------------------

class TestManualRegistration(TestCase):

    def setUp(self):
        self.reg = PanelRegistry()
        # Prevent autodiscovery so tests are isolated from installed packages.
        self.reg._discovered = True

    def test_register_without_panel_id_raises(self):
        with self.assertRaises(ValueError) as ctx:
            self.reg.register(MinimalPanel)
        self.assertIn("panel_id is required", str(ctx.exception))

    def test_register_stamps_registry_id(self):
        self.reg.register(MinimalPanel, panel_id="my_panel")
        panel = self.reg.get_panel("my_panel")
        self.assertIsNotNone(panel)
        self.assertEqual(panel._registry_id, "my_panel")

    def test_app_name_defaults_to_panel_id(self):
        self.reg.register(MinimalPanel, panel_id="my_panel")
        panel = self.reg.get_panel("my_panel")
        self.assertEqual(panel.app_name, "my_panel")

    def test_package_defaults_to_panel_id(self):
        self.reg.register(MinimalPanel, panel_id="my_panel")
        panel = self.reg.get_panel("my_panel")
        self.assertEqual(panel.package, "my_panel")

    def test_explicit_app_name_is_preserved(self):
        self.reg.register(PanelWithAppName, panel_id="custom_panel")
        panel = self.reg.get_panel("custom_panel")
        self.assertEqual(panel.app_name, "custom_app")

    def test_explicit_package_is_preserved(self):
        self.reg.register(PanelWithPackage, panel_id="pkg_panel")
        panel = self.reg.get_panel("pkg_panel")
        self.assertEqual(panel.package, "my-custom-package")

    def test_explicit_app_name_and_package_both_preserved(self):
        self.reg.register(PanelWithBoth, panel_id="both_panel")
        panel = self.reg.get_panel("both_panel")
        self.assertEqual(panel.app_name, "explicit_app")
        self.assertEqual(panel.package, "explicit-package")

    def test_id_attribute_is_ignored_as_registry_key(self):
        """panel.id is silently ignored; panel_id determines the registry key."""
        self.reg.register(PanelWithOldId, panel_id="new_key")
        self.assertIsNotNone(self.reg.get_panel("new_key"))
        self.assertIsNone(self.reg.get_panel("some_old_id"))

    def test_id_attribute_is_not_required(self):
        """Panels without an id attribute register without error."""
        self.reg.register(MinimalPanel, panel_id="no_id_panel")
        self.assertTrue(self.reg.is_registered("no_id_panel"))

    def test_get_url_name_method_preserved(self):
        self.reg.register(PanelWithUrlName, panel_id="url_panel")
        panel = self.reg.get_panel("url_panel")
        self.assertEqual(panel.get_url_name(), "dashboard")


# ---------------------------------------------------------------------------
# Collision behaviour
# ---------------------------------------------------------------------------

class TestCollisionBehaviour(TestCase):

    def setUp(self):
        self.reg = PanelRegistry()
        self.reg._discovered = True

    def test_two_panels_with_same_id_attr_both_register(self):
        """
        Two panels that both declare id='clashing' but have different
        panel_ids must both survive — this is the core collision fix.
        """
        class PanelA:
            id = "clashing_id"
            name = "Panel A"
            description = "First panel"
            icon = "chart"

        class PanelB:
            id = "clashing_id"
            name = "Panel B"
            description = "Second panel"
            icon = "database"

        self.reg.register(PanelA, panel_id="panel_a")
        self.reg.register(PanelB, panel_id="panel_b")

        self.assertIsNotNone(self.reg.get_panel("panel_a"))
        self.assertIsNotNone(self.reg.get_panel("panel_b"))
        self.assertEqual(len(self.reg.get_panels()), 2)

    def test_duplicate_panel_id_keeps_first(self):
        """When two panels share the same panel_id, the first one wins."""
        class FirstPanel:
            name = "First"
            description = "First panel"
            icon = "chart"

        class SecondPanel:
            name = "Second"
            description = "Second panel"
            icon = "database"

        self.reg.register(FirstPanel, panel_id="dupe")
        self.reg.register(SecondPanel, panel_id="dupe")

        panels = self.reg.get_panels()
        self.assertEqual(len(panels), 1)
        self.assertEqual(panels[0].name, "First")


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

class TestValidation(TestCase):

    def setUp(self):
        self.reg = PanelRegistry()
        self.reg._discovered = True

    def test_missing_name_raises(self):
        with self.assertRaises(ValueError) as ctx:
            self.reg.register(MissingNamePanel, panel_id="bad")
        self.assertIn("name", str(ctx.exception))

    def test_missing_description_raises(self):
        with self.assertRaises(ValueError) as ctx:
            self.reg.register(MissingDescriptionPanel, panel_id="bad")
        self.assertIn("description", str(ctx.exception))

    def test_missing_icon_raises(self):
        with self.assertRaises(ValueError) as ctx:
            self.reg.register(MissingIconPanel, panel_id="bad")
        self.assertIn("icon", str(ctx.exception))

    def test_empty_name_raises(self):
        class EmptyName:
            name = ""
            description = "Has description"
            icon = "chart"

        with self.assertRaises(ValueError):
            self.reg.register(EmptyName, panel_id="bad")

    def test_none_description_raises(self):
        class NoneDescription:
            name = "Has name"
            description = None
            icon = "chart"

        with self.assertRaises(ValueError):
            self.reg.register(NoneDescription, panel_id="bad")


# ---------------------------------------------------------------------------
# Lookup methods
# ---------------------------------------------------------------------------

class TestLookupMethods(TestCase):

    def setUp(self):
        self.reg = PanelRegistry()
        self.reg._discovered = True
        self.reg.register(MinimalPanel, panel_id="p1")

    def test_get_panel_returns_instance(self):
        panel = self.reg.get_panel("p1")
        self.assertIsNotNone(panel)
        self.assertEqual(panel.name, "Minimal Panel")

    def test_get_panel_returns_none_for_unknown(self):
        self.assertIsNone(self.reg.get_panel("does_not_exist"))

    def test_is_registered_true(self):
        self.assertTrue(self.reg.is_registered("p1"))

    def test_is_registered_false(self):
        self.assertFalse(self.reg.is_registered("absent"))

    def test_get_panels_returns_all(self):
        self.reg.register(PanelWithAppName, panel_id="p2")
        panels = self.reg.get_panels()
        self.assertEqual(len(panels), 2)
        ids = {p._registry_id for p in panels}
        self.assertEqual(ids, {"p1", "p2"})

    def test_clear_empties_registry(self):
        self.reg.clear()
        # Inspect internal state directly — get_panels() would re-trigger
        # autodiscovery after clear() resets _discovered.
        self.assertEqual(list(self.reg._panels.values()), [])
        self.assertFalse(self.reg._panels.get("p1"))

    def test_clear_resets_discovered_flag(self):
        self.reg._discovered = True
        self.reg.clear()
        self.assertFalse(self.reg._discovered)


# ---------------------------------------------------------------------------
# _normalize_package_name
# ---------------------------------------------------------------------------

class TestNormalizePackageName(TestCase):

    def test_hyphens_to_underscores(self):
        self.assertEqual(_normalize_package_name("my-panel"), "my_panel")

    def test_uppercase_lowercased(self):
        self.assertEqual(_normalize_package_name("MyPanel"), "mypanel")

    def test_mixed_hyphens_and_case(self):
        self.assertEqual(_normalize_package_name("Dj-Cache-Panel"), "dj_cache_panel")

    def test_already_normalized_unchanged(self):
        self.assertEqual(_normalize_package_name("dj_cache_panel"), "dj_cache_panel")

    def test_multiple_hyphens(self):
        self.assertEqual(_normalize_package_name("a-b-c-d"), "a_b_c_d")
