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

    Optional attributes:
        package (str): PyPI package name, e.g. "dj-example-panel".
            When set, enables the install/configure page for this panel and
            provides the ``pip install`` snippet.
        app_name (str): Django app label as it appears in INSTALLED_APPS,
            e.g. "dj_example_panel". When set, the Control Room can accurately
            check whether the app has been added to INSTALLED_APPS as part of
            the ``configured`` status check. Defaults to the panel's ``id``.
        docs_url (str): URL to the panel's documentation (optional).
        pypi_url (str): URL to the panel's PyPI page (optional).

    Optional methods:
        get_url_name(): Returns the URL name for this panel (defaults to "index")
    """

    id = None
    name = None
    description = None
    icon = "default"

    # Optional — provide these to enable the install/configure page and accurate
    # INSTALLED_APPS detection for community panels.
    package = None
    app_name = None
    docs_url = None
    pypi_url = None

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
            raise ValueError(
                f"Panel {self.__class__.__name__} must define 'description'"
            )
