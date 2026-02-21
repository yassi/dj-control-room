"""
Example project app configuration.

Registers example panels for demonstration purposes.
"""
from django.apps import AppConfig


class ExampleProjectConfig(AppConfig):
    name = "example_project"
    verbose_name = "Example Project"
    
    def ready(self):
        """
        Register example panels when the app is ready.
        
        In a real setup, panels would be registered via entry points
        in their own packages. This manual registration is just for
        demonstration purposes.
        """
        from dj_control_room.registry import registry
        from .example_panels import ExamplePanel, DemoPanel
        
        # Manually register example panels.
        # panel_id is required for manual registration (normally derived from
        # dist.name during autodiscovery via entry points).
        registry.register(ExamplePanel, panel_id='example')
        registry.register(DemoPanel, panel_id='demo')
