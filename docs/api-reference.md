# API Reference

Complete API reference for Django Control Room.

Official Site: **[djangocontrolroom.com](https://djangocontrolroom.com)**.

![Django Control Room](https://raw.githubusercontent.com/yassi/dj-control-room/main/images/grid_image.png)

## Panel Interface

### Panel Class

The core interface that all panels must implement.

```python
class MyPanel:
    """
    Panel class for Django Control Room.
    """
    
    # Required attributes
    id: str
    name: str
    description: str
    icon: str
    
    # Optional methods
    def get_url_name(self) -> str:
        """Return the URL name for the panel's main entry point."""
        return "index"
```

#### Required Attributes

##### `id`

**Type:** `str`  
**Description:** Unique identifier for the panel. Must match the `app_name` in your panel's `urls.py`.

**Example:**
```python
id = "my_panel"
```

##### `name`

**Type:** `str`  
**Description:** Display name shown in the Control Room dashboard.

**Example:**
```python
name = "My Panel"
```

##### `description`

**Type:** `str`  
**Description:** Brief description (1-2 sentences) of what the panel does.

**Example:**
```python
description = "Monitor system health and performance metrics"
```

##### `icon`

**Type:** `str`  
**Description:** Icon identifier for the panel.

**Available values:** `"database"`, `"layers"`, `"link"`, `"chart"`, `"radio"`, `"cog"`

**Example:**
```python
icon = "chart"
```

#### Optional Methods

##### `get_url_name()`

**Returns:** `str`  
**Default:** `"index"`  
**Description:** Returns the URL name for the panel's main entry point.

**Example:**
```python
def get_url_name(self):
    return "dashboard"  # Or "index", "home", etc.
```

Django Control Room resolves the panel's URL using:
```python
reverse(f'{panel.id}:{url_name}')
```

## Registry

### `registry`

Global panel registry instance. Automatically discovers and manages registered panels.

```python
from dj_control_room.registry import registry
```

#### Methods

##### `autodiscover()`

Discover all panels registered via Python entry points.

**Returns:** `None`

**Example:**
```python
registry.autodiscover()
```

This is automatically called when Django starts, but you can call it manually if needed.

##### `get_panels()`

Get list of all registered panels.

**Returns:** `List[Panel]` - List of panel instances

**Example:**
```python
panels = registry.get_panels()
for panel in panels:
    print(f"{panel.id}: {panel.name}")
```

##### `get_panel(panel_id)`

Get a specific panel by ID.

**Parameters:**
- `panel_id` (str): The panel's ID

**Returns:** `Panel` or `None` if not found

**Example:**
```python
panel = registry.get_panel('dj_redis_panel')
if panel:
    print(panel.name)
```

##### `register_panel(panel)`

Manually register a panel instance.

**Parameters:**
- `panel`: Panel instance to register

**Returns:** `None`

**Example:**
```python
from my_panel.panel import MyPanel

panel = MyPanel()
registry.register_panel(panel)
```

> **Note:** Panels are normally registered automatically via entry points. Manual registration is rarely needed.

## Views

### Decorators

#### `@staff_member_required`

Django's built-in decorator to require staff permissions.

**Example:**
```python
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def my_view(request):
    # Only staff members can access
    pass
```

### Context Helpers

#### `admin.site.each_context(request)`

Get Django admin context for proper rendering.

**Parameters:**
- `request`: Django HttpRequest object

**Returns:** `dict` - Admin context with site info, permissions, etc.

**Example:**
```python
from django.contrib import admin

def my_view(request):
    context = admin.site.each_context(request)
    context.update({
        'title': 'My Panel',
        'data': get_my_data(),
    })
    return render(request, 'admin/my_panel/index.html', context)
```

## Featured Panels

### `FEATURED_PANELS`

List of curated official panels.

```python
from dj_control_room.featured_panels import FEATURED_PANELS
```

**Structure:**
```python
[
    {
        "id": "dj_redis_panel",
        "name": "Redis Panel",
        "description": "Monitor connections, memory, keys",
        "icon": "database",
        "package": "dj-redis-panel",
        "docs_url": "https://github.com/yassi/dj-redis-panel",
        "pypi_url": "https://pypi.org/project/dj-redis-panel/",
        "coming_soon": False,  # Optional
    },
    # ...
]
```

### Helper Functions

#### `get_featured_panel_ids()`

Get list of all featured panel IDs.

**Returns:** `List[str]`

**Example:**
```python
from dj_control_room.featured_panels import get_featured_panel_ids

ids = get_featured_panel_ids()
# ['dj_redis_panel', 'dj_cache_panel', ...]
```

#### `get_featured_panel_metadata(panel_id)`

Get metadata for a featured panel.

**Parameters:**
- `panel_id` (str): The panel's ID

**Returns:** `dict` or `None` if not found

**Example:**
```python
from dj_control_room.featured_panels import get_featured_panel_metadata

meta = get_featured_panel_metadata('dj_redis_panel')
if meta:
    print(meta['name'])  # "Redis Panel"
    print(meta['package'])  # "dj-redis-panel"
```

#### `is_featured_panel(panel_id)`

Check if a panel ID is a featured panel.

**Parameters:**
- `panel_id` (str): The panel's ID

**Returns:** `bool`

**Example:**
```python
from dj_control_room.featured_panels import is_featured_panel

if is_featured_panel('dj_redis_panel'):
    print("This is an official panel")
```

## Settings

### `DJ_CONTROL_ROOM_SETTINGS`

Django settings dictionary for Django Control Room configuration.

**Location:** `settings.py`

**Structure:**
```python
DJ_CONTROL_ROOM_SETTINGS = {
    'REGISTER_PANELS_IN_ADMIN': bool,
    'PANEL_ADMIN_REGISTRATION': dict,
}
```

#### Settings Keys

##### `REGISTER_PANELS_IN_ADMIN`

**Type:** `bool`  
**Default:** `False`  
**Description:** Global setting for panel admin registration.

```python
DJ_CONTROL_ROOM_SETTINGS = {
    'REGISTER_PANELS_IN_ADMIN': True,
}
```

##### `PANEL_ADMIN_REGISTRATION`

**Type:** `dict`  
**Default:** `{}`  
**Description:** Per-panel admin registration overrides.

```python
DJ_CONTROL_ROOM_SETTINGS = {
    'PANEL_ADMIN_REGISTRATION': {
        'dj_redis_panel': True,
        'dj_cache_panel': False,
    }
}
```

## Entry Points

### `dj_control_room.panels`

Entry point group for panel registration.

**Format:**
```toml
[project.entry-points."dj_control_room.panels"]
panel_id = "package.module:PanelClass"
```

**Example:**
```toml
[project.entry-points."dj_control_room.panels"]
my_panel = "my_panel.panel:MyPanel"
```

**Requirements:**
- `panel_id` must match the panel's `id` attribute
- Must point to a valid Python class
- Class must implement the panel interface

## URL Patterns

### Panel URL Structure

Panels should define their URLs with proper namespacing:

```python
# my_panel/urls.py
from django.urls import path
from . import views

app_name = 'my_panel'  # Must match panel.id

urlpatterns = [
    path('', views.index, name='index'),
    path('detail/<str:id>/', views.detail, name='detail'),
]
```

### URL Resolution

Django Control Room resolves panel URLs using:

```python
from django.urls import reverse

url = reverse(f'{panel.id}:{url_name}')
# Example: reverse('my_panel:index') -> '/admin/my-panel/'
```

## Models

### Placeholder Models

Panels can define placeholder models for admin integration:

```python
# my_panel/models.py
from django.db import models

class MyPanelPlaceholder(models.Model):
    class Meta:
        managed = False
        verbose_name = "My Panel"
        verbose_name_plural = "My Panel"
        app_label = "my_panel"
```

> **Note:** Django Control Room automatically unregisters these and creates proxy models under "Django Control Room" (unless configured otherwise).

## Exceptions

### Panel Registration Errors

Panels that fail validation will be logged but won't break the app:

```python
logger.warning(f"Failed to load panel '{panel_id}': {error}")
```

**Common errors:**
- Missing required attributes (`id`, `name`, `description`, `icon`)
- Invalid icon value
- Duplicate panel ID
- Import errors

### URL Resolution Errors

If a panel's URL can't be resolved:

```python
logger.error(f"Failed to reverse URL for panel '{panel_id}': {error}")
```

The panel will still appear in the dashboard with a `#` URL.

## Logging

Django Control Room uses Python's standard logging:

```python
import logging

logger = logging.getLogger('dj_control_room')
```

**Log levels:**
- `INFO`: Panel registration, successful operations
- `WARNING`: Failed panel loads, duplicate panels, verification failures
- `ERROR`: URL resolution errors, critical failures
- `DEBUG`: Detailed discovery and registration steps

**Example configuration:**
```python
# settings.py
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'dj_control_room': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}
```

## Type Hints

Django Control Room is fully typed. You can use type checkers like mypy:

```python
from typing import List
from dj_control_room.registry import registry

def get_panel_names() -> List[str]:
    return [panel.name for panel in registry.get_panels()]
```

## Next Steps

- [Installation Guide](installation.md)
- [Configuration](configuration.md)
- [Creating Panels](creating-panels.md)
- [GitHub Repository](https://github.com/yassi/dj-control-room)
