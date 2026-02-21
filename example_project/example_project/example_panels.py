"""
Example panels for testing DJ Control Room.

These are simple in-process panels that demonstrate the minimal panel
interface. In a real setup each panel would be a separate pip-installable
package discovered automatically via entry points — no manual registration
needed.
"""


class ExamplePanel:
    """Minimal example panel registered manually for demonstration."""

    name = "Example Panel"
    description = "A simple example panel for demonstration"
    icon = "chart"
    # panel_id ('example') and app_name/package are supplied by the caller
    # of registry.register() since there is no entry point to read dist.name from.


class DemoPanel:
    """Another demo panel registered manually for demonstration."""

    name = "Demo Panel"
    description = "Another demonstration panel"
    icon = "database"
