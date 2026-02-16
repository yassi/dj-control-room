"""
Base Panel class for Control Room panels.

This is an optional base class that panel developers can inherit from.
It provides sensible defaults and type hints, but is not required.
"""


class BasePanel:
    """
    Optional base class for Control Room panels.
    
    Panel developers can inherit from this for convenience, but it's not required.
    Any class that implements the required interface can be registered as a panel.
    
    Required attributes:
        id (str): Unique identifier for the panel (also used as URL namespace)
        name (str): Display name shown in the UI
        description (str): Brief description of what the panel does
        icon (str): Icon identifier (database, layers, chart, link, radio, alert, etc.)
    
    Optional methods:
        get_url_name(): Returns the URL name for this panel (defaults to "index")
        get_urls(): Returns URL patterns for this panel (enables auto-mounting)
    """
    
    id = None
    name = None
    description = None
    icon = "default"
    
    def get_url_name(self):
        """
        Return the URL name for this panel's main entry point.
        
        By convention, this should be "index" (the default). DJ Control Room
        will resolve this using your panel's namespace (from urls.py app_name).
        
        Returns:
            str: The URL name (default: "index")
            
        Examples:
            # Default - just return "index"
            def get_url_name(self):
                return "index"
            
            # Or use a different name if your main view isn't called "index"
            def get_url_name(self):
                return "dashboard"
        
        Note:
            - Panel's namespace comes from app_name in your urls.py
            - DJ Control Room resolves: reverse('{panel_id}:{url_name}')
            - Example: panel.id='redis', returns 'index' → reverse('redis:index')
        """
        return "index"
    
    # Note: get_urls() is no longer used
    # Panels are included directly by users in their urls.py
    # like any other Django app
    
    def validate(self):
        """
        Validate that the panel has all required attributes.
        
        Raises:
            ValueError: If required attributes are missing
        """
        if not self.id:
            raise ValueError(f"Panel {self.__class__.__name__} must define 'id'")
        if not self.name:
            raise ValueError(f"Panel {self.__class__.__name__} must define 'name'")
        if not self.description:
            raise ValueError(f"Panel {self.__class__.__name__} must define 'description'")
