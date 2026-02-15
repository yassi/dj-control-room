"""
Example panels for testing DJ Control Room.

These are simple example panels that demonstrate the panel interface.
In a real setup, these would be in separate packages.
"""
from django.urls import path
from django.http import HttpResponse
from django.shortcuts import render


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
                <li>Namespaced URLs</li>
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
            <p>This panel's URLs are namespaced as: <code>dj_control_room:demo:*</code></p>
        </body>
        </html>
    """)


class ExamplePanel:
    """Example panel showing the minimal required interface with auto-mounted URLs"""
    
    id = "example"
    name = "Example Panel"
    description = "A simple example panel for demonstration"
    icon = "chart"
    
    def get_url(self):
        """Return URL to this panel (auto-mounted by Control Room)"""
        from django.urls import reverse
        return reverse('dj_control_room:example:index')
    
    def get_urls(self):
        """Provide URL patterns - these are auto-mounted by Control Room"""
        return [
            path('', example_index, name='index'),
        ]
    
    def get_status(self):
        """Return healthy status"""
        return {
            "status": "healthy",
            "status_label": "READY"
        }


class DemoPanel:
    """Another demo panel with auto-mounted URLs"""
    
    id = "demo"
    name = "Demo Panel"
    description = "Another demonstration panel"
    icon = "database"
    
    def get_url(self):
        """Return URL to this panel (auto-mounted by Control Room)"""
        from django.urls import reverse
        return reverse('dj_control_room:demo:index')
    
    def get_urls(self):
        """Provide URL patterns - these are auto-mounted by Control Room"""
        return [
            path('', demo_index, name='index'),
        ]
    
    def get_status(self):
        """Return connected status"""
        return {
            "status": "connected",
            "status_label": "CONNECTED"
        }
