"""
Panel Registry for DJ Control Room.

Discovers and manages panels registered via Python entry points.
"""
import logging
import sys

logger = logging.getLogger(__name__)


def _normalize_package_name(name):
    """Normalize a PyPI package name for comparison (PEP 503)."""
    return name.lower().replace("-", "_")


class PanelRegistry:
    """
    Registry for Control Room panels.
    
    Discovers panels via Python package entry points in the
    'dj_control_room.panels' group.
    """
    
    ENTRY_POINT_GROUP = "dj_control_room.panels"
    
    def __init__(self):
        self._panels = {}
        self._discovered = False
    
    def autodiscover(self):
        """
        Discover all panels registered via entry points.
        
        Looks for entry points in the 'dj_control_room.panels' group.
        Each entry point should point to a panel class that implements
        the required interface.
        """
        if self._discovered:
            return
        
        self._discovered = True
        
        # Use different import based on Python version
        if sys.version_info >= (3, 10):
            from importlib.metadata import entry_points
            eps = entry_points(group=self.ENTRY_POINT_GROUP)
        else:
            # Python 3.9 compatibility
            from importlib.metadata import entry_points
            eps = entry_points().get(self.ENTRY_POINT_GROUP, [])
        
        for ep in eps:
            try:
                self._load_panel(ep)
            except Exception as e:
                logger.warning(
                    f"Failed to load panel '{ep.name}' from {ep.value}: {e}",
                    exc_info=True
                )
    
    def _load_panel(self, entry_point):
        """
        Load a single panel from an entry point.

        Args:
            entry_point: The entry point to load
        """
        logger.debug(f"Loading panel '{entry_point.name}' from {entry_point.value}")

        # Load the panel class
        panel_class = entry_point.load()

        # Instantiate the panel
        panel = panel_class()

        # Validate required attributes
        self._validate_panel(panel, entry_point.name)

        # Register the panel
        panel_id = getattr(panel, 'id', entry_point.name)

        # Guard: if this ID belongs to a featured panel, verify the entry point
        # comes from the expected PyPI distribution. This prevents a malicious
        # package from squatting on an official featured panel's ID.
        if not self._verify_featured_identity(panel_id, entry_point):
            return

        if panel_id in self._panels:
            logger.warning(
                f"Panel ID '{panel_id}' is already registered. "
                f"Skipping duplicate from {entry_point.value}"
            )
            return

        self._panels[panel_id] = panel
        logger.info(f"Registered panel '{panel_id}' ({panel.name})")

    def _verify_featured_identity(self, panel_id, entry_point):
        """
        If panel_id matches a featured panel, verify the entry point's
        distribution matches the expected package.

        Returns True if the panel is safe to register, False if it should
        be rejected.
        """
        from .featured_panels import FEATURED_PANELS

        featured_map = {
            fp["id"]: fp["package"]
            for fp in FEATURED_PANELS
            if not fp.get("coming_soon", False)
        }

        if panel_id not in featured_map:
            return True  # Not a protected ID — always allow

        expected_package = featured_map[panel_id]

        try:
            actual_dist = entry_point.dist.name
        except AttributeError:
            # Older importlib.metadata versions may not expose .dist
            logger.debug(
                f"Cannot verify distribution for panel '{panel_id}' "
                "(importlib.metadata does not expose entry_point.dist). Allowing."
            )
            return True

        if _normalize_package_name(actual_dist) != _normalize_package_name(expected_package):
            logger.warning(
                f"Panel '{panel_id}' from distribution '{actual_dist}' is NOT "
                f"authorized to use this ID (expected '{expected_package}'). "
                "This panel will not be loaded."
            )
            return False

        return True
    
    def _validate_panel(self, panel, entry_point_name):
        """
        Validate that a panel has required attributes and methods.
        
        Args:
            panel: The panel instance to validate
            entry_point_name: Name of the entry point (for error messages)
            
        Raises:
            ValueError: If panel is missing required attributes/methods
        """
        required_attrs = ['id', 'name', 'description', 'icon']
        required_methods = []  # No required methods - all have defaults
        optional_methods = ['get_url_name', 'get_urls']
        
        # Check required attributes
        for attr in required_attrs:
            if not hasattr(panel, attr):
                raise ValueError(
                    f"Panel from entry point '{entry_point_name}' "
                    f"is missing required attribute: {attr}"
                )
            if not getattr(panel, attr):
                raise ValueError(
                    f"Panel from entry point '{entry_point_name}' "
                    f"has empty/None value for required attribute: {attr}"
                )
        
        # Check required methods
        for method in required_methods:
            if not hasattr(panel, method):
                raise ValueError(
                    f"Panel from entry point '{entry_point_name}' "
                    f"is missing required method: {method}"
                )
            if not callable(getattr(panel, method)):
                raise ValueError(
                    f"Panel from entry point '{entry_point_name}' "
                    f"attribute '{method}' is not callable"
                )
        
        # Check optional methods are callable if present
        for method in optional_methods:
            if hasattr(panel, method) and not callable(getattr(panel, method)):
                raise ValueError(
                    f"Panel from entry point '{entry_point_name}' "
                    f"attribute '{method}' is not callable"
                )
    
    def register(self, panel_class, panel_id=None):
        """
        Manually register a panel class.
        
        This is useful for testing or for apps that want to register
        panels programmatically rather than via entry points.
        
        Args:
            panel_class: The panel class to register
            panel_id: Optional ID for the panel (uses panel.id if not provided)
        """
        panel = panel_class()
        
        if panel_id is None:
            if not hasattr(panel, 'id'):
                raise ValueError("Panel must have an 'id' attribute")
            panel_id = panel.id
        
        self._validate_panel(panel, panel_id)
        self._panels[panel_id] = panel
        logger.info(f"Manually registered panel '{panel_id}' ({panel.name})")
    
    def get_panels(self):
        """
        Get all registered panels.
        
        Returns:
            list: List of panel instances
        """
        if not self._discovered:
            self.autodiscover()
        
        return list(self._panels.values())
    
    def get_panel(self, panel_id):
        """
        Get a specific panel by ID.
        
        Args:
            panel_id: The ID of the panel to retrieve
            
        Returns:
            Panel instance or None if not found
        """
        if not self._discovered:
            self.autodiscover()
        
        return self._panels.get(panel_id)
    
    def is_registered(self, panel_id):
        """
        Check if a panel is registered.
        
        Args:
            panel_id: The ID to check
            
        Returns:
            bool: True if the panel is registered
        """
        if not self._discovered:
            self.autodiscover()
        
        return panel_id in self._panels
    
    def clear(self):
        """
        Clear all registered panels.
        
        Useful for testing.
        """
        self._panels.clear()
        self._discovered = False


# Global registry instance
registry = PanelRegistry()
