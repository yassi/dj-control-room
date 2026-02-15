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
        id (str): Unique identifier for the panel
        name (str): Display name shown in the UI
        description (str): Brief description of what the panel does
        icon (str): Icon identifier (database, layers, chart, link, radio, alert, etc.)
    
    Required methods:
        get_url(): Returns the URL to access this panel
        get_status(): Returns dict with 'status' and 'status_label' keys
    
    Optional methods:
        get_urls(): Returns URL patterns for this panel (enables auto-mounting)
    """
    
    id = None
    name = None
    description = None
    icon = "default"
    
    def get_url(self):
        """
        Return the URL to access this panel.
        
        If the panel implements get_urls(), this should return a URL
        within the dj_control_room namespace. Otherwise, it can return
        any URL (useful for panels that can work standalone).
        
        Returns:
            str: The URL path for this panel
            
        Examples:
            # With auto-mounted URLs (recommended):
            def get_url(self):
                from django.urls import reverse
                return reverse('dj_control_room:mypanel:index')
            
            # Standalone panel:
            def get_url(self):
                from django.urls import reverse
                return reverse('my_panel:index')
        """
        raise NotImplementedError("Panels must implement get_url()")
    
    def get_urls(self):
        """
        Optional: Return URL patterns for this panel.
        
        If implemented, Control Room will automatically mount these URLs
        under /admin/dj-control-room/{panel_id}/ with namespace {panel_id}.
        
        This means users only need to add Control Room to their urls.py
        once, and all panel URLs are automatically included.
        
        Returns:
            list: Django URL patterns
            
        Example:
            def get_urls(self):
                from django.urls import path
                from . import views
                
                return [
                    path('', views.index, name='index'),
                    path('detail/<str:key>/', views.detail, name='detail'),
                    path('action/', views.action, name='action'),
                ]
        
        Note:
            - URLs are namespaced as: dj_control_room:{panel_id}:{name}
            - Example: reverse('dj_control_room:redis:index')
            - If not implemented, panel can still provide standalone URLs
        """
        return None
    
    def get_status(self):
        """
        Check the status of this panel's service/functionality.
        
        Returns:
            dict: Dictionary with 'status' and 'status_label' keys
            
        Example:
            def get_status(self):
                try:
                    # Check if service is available
                    if self.check_service():
                        return {"status": "connected", "status_label": "CONNECTED"}
                except Exception:
                    return {"status": "error", "status_label": "ERROR"}
        """
        return {"status": "unknown", "status_label": "UNKNOWN"}
    
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
