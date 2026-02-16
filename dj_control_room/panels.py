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
    
    def get_urls(self):
        """
        Optional: Return URL patterns for this panel.
        
        If implemented, Control Room will automatically mount these URLs
        under /admin/dj-control-room/{panel_id}/
        
        This means users only need to add Control Room to their urls.py
        once, and all panel URLs are automatically included.
        
        Returns:
            list: Django URL patterns (typically imported from your urls.py)
            
        Example:
            def get_urls(self):
                # Import from your standard Django urls.py file
                from .urls import urlpatterns
                return urlpatterns
        
        Your urls.py should define app_name for namespacing:
            # urls.py
            from django.urls import path
            from . import views
            
            app_name = 'mypanel'  # Your panel's namespace
            
            urlpatterns = [
                path('', views.index, name='index'),  # Main entry point
                path('detail/<str:key>/', views.detail, name='detail'),
            ]
        
        Note:
            - URLs are mounted at: /admin/dj-control-room/{panel_id}/
            - Use your own namespace: reverse('mypanel:index')
            - Include a root path ('') with name='index' as your main entry point
            - If not implemented, panel must provide standalone URLs
        """
        return None
    
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
