"""
Example panels for testing DJ Control Room.

These are simple example panels that demonstrate the panel interface.
In a real setup, these would be in separate packages with their own urls.py files.

Note: These examples inline the URL patterns for simplicity, but real panels
should import from a standard Django urls.py file with app_name defined.
"""
from django.urls import path
from django.http import HttpResponse


def example_index(request):
    """Example panel index view"""
    return HttpResponse("""
        <html>
        <head><title>Example Panel</title></head>
        <body style="font-family: sans-serif; padding: 20px;">
            <h1>Example Panel</h1>
            <p>This is an auto-mounted panel at <code>/admin/dj-control-room/example/</code></p>
            <p><a href="/admin/dj-control-room/">← Back to Control Room</a></p>
            <h2>Features:</h2>
            <ul>
                <li>Automatically mounted by Control Room</li>
                <li>Uses own namespace (<code>example:index</code>)</li>
                <li>No manual URL configuration needed</li>
            </ul>
        </body>
        </html>
    """)


def demo_index(request):
    """Demo panel index view"""
    return HttpResponse("""
        <html>
        <head><title>Demo Panel</title></head>
        <body style="font-family: sans-serif; padding: 20px;">
            <h1>Demo Panel</h1>
            <p>This is an auto-mounted panel at <code>/admin/dj-control-room/demo/</code></p>
            <p><a href="/admin/dj-control-room/">← Back to Control Room</a></p>
            <h2>URL Namespace:</h2>
            <p>This panel's URLs are namespaced as: <code>demo:*</code></p>
            <p>Panel decoupled from DJ Control Room - can work standalone!</p>
        </body>
        </html>
    """)


# URL patterns with app_name for namespacing
# In real panels, these would be in separate urls.py files
example_urlpatterns = [
    path('', example_index, name='index'),
]

demo_urlpatterns = [
    path('', demo_index, name='index'),
]


class ExamplePanel:
    """Example panel showing the minimal required interface with auto-mounted URLs"""
    
    id = "example"
    name = "Example Panel"
    description = "A simple example panel for demonstration"
    icon = "chart"
    
    def get_urls(self):
        """
        Provide URL patterns - these are auto-mounted by Control Room.
        
        In a real panel, you would:
            from .urls import urlpatterns
            return urlpatterns
        
        And your urls.py would have:
            app_name = 'example'  # Must match panel id
            urlpatterns = [...]
        """
        # Return tuple format: (urlpatterns, app_name)
        # app_name must match the panel's id attribute
        return (example_urlpatterns, 'example')
    
    # get_url_name() not needed - defaults to "index"


class DemoPanel:
    """Another demo panel with auto-mounted URLs"""
    
    id = "demo"
    name = "Demo Panel"
    description = "Another demonstration panel"
    icon = "database"
    
    def get_urls(self):
        """
        Provide URL patterns - these are auto-mounted by Control Room.
        Real panels should import from urls.py.
        """
        # Return tuple format: (urlpatterns, app_name)
        # app_name must match the panel's id attribute
        return (demo_urlpatterns, 'demo')
    
    # get_url_name() not needed - defaults to "index"
