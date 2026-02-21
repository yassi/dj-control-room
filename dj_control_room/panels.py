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
        name (str): Display name shown in the UI
        description (str): Brief description of what the panel does
        icon (str): Icon identifier (database, layers, chart, link, radio, alert, etc.)

    Optional attributes:
        app_name (str): Django app label as it appears in INSTALLED_APPS and
            the URL namespace declared in your urls.py, e.g. "dj_example_panel".
            Defaults to the normalized PyPI distribution name (hyphens replaced
            with underscores), which is typically the same value. Set this
            explicitly only when your app label differs from the dist name.
        package (str): PyPI package name override, e.g. "dj-example-panel".
            Defaults to the distribution name from the entry point metadata,
            so this only needs to be set if you want to display a different
            package name on the install page.
        docs_url (str): URL to the panel's documentation (optional).
        pypi_url (str): URL to the panel's PyPI page (optional).

    Optional methods:
        get_url_name(): Returns the URL name for this panel (defaults to "index")

    Note:
        ``id`` is no longer part of the panel contract. If present on a subclass
        it is silently ignored — the unique registry key is derived from the
        PyPI distribution name at discovery time.
    """

    name = None
    description = None
    icon = "default"

    # Optional — the registry stamps these from dist metadata if not set.
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
            - DJ Control Room resolves: reverse('{app_name}:{url_name}')
            - Example: app_name='dj_redis_panel', returns 'index' → reverse('dj_redis_panel:index')
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
        if not self.name:
            raise ValueError(f"Panel {self.__class__.__name__} must define 'name'")
        if not self.description:
            raise ValueError(
                f"Panel {self.__class__.__name__} must define 'description'"
            )
