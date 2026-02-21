# Creating Control Room Panels

This guide explains how to create third-party panels for DJ Control Room.

## Overview

DJ Control Room uses Python entry points for plugin discovery. This means:
- ✅ No naming conventions required
- ✅ No manual configuration needed
- ✅ Automatic discovery when installed
- ✅ Works with any package structure
- ✅ Collision-proof: registry key is derived from your PyPI dist name, not a hand-picked string

**Key Pattern:**
- The registry key is derived from your **PyPI distribution name** (hyphens → underscores) — you don't declare an `id`
- `app_name` in your `urls.py` must match `panel.app_name` (defaults to the normalized dist name)
- Users include your panel's URLs in their project (like any Django app)
- Main view should be named "index" (convention)
- Control room auto-discovers your panel via entry points

## Quick Start

### 1. Create Your Panel Class

```python
# my_awesome_panel/panel.py

class AwesomePanel:
    """My awesome monitoring panel"""

    # Required attributes
    name = "Awesome Panel"
    description = "Monitor awesome things in real-time"
    icon = "chart"  # See available icons below

    # Optional: only needed if your Django app label differs from your PyPI dist name
    # app_name = "my_awesome_panel"

    def get_url_name(self):
        """
        Return the URL name for your main entry point.
        Defaults to "index" if not implemented.
        """
        return "index"  # or just omit this method to use default
```

**In your urls.py:**
```python
# my_awesome_panel/urls.py
from django.urls import path
from . import views

# Must match panel.app_name, which defaults to the normalized dist name.
# For a package named "my-awesome-panel", this should be "my_awesome_panel".
app_name = 'my_awesome_panel'

urlpatterns = [
    path('', views.index, name='index'),  # Main entry point
    path('details/', views.details, name='details'),
]
```

### 2. Register via Entry Point

Add this to your `pyproject.toml`:

```toml
[project.entry-points."dj_control_room.panels"]
my_awesome_panel = "my_awesome_panel.panel:AwesomePanel"
```

The format is: `entry_point_name = "package.module:ClassName"`

The entry point name is not used as the registry key (that comes from `dist.name`), but it should still be something meaningful and unique to your package.

### 3. Users Install and Configure!

```bash
pip install my-awesome-panel
```

Then users include your panel in their `urls.py`:
```python
# project/urls.py
urlpatterns = [
    # Include your panel
    path('', include('my_awesome_panel.urls')),
    # Control room dashboard
    path('admin/dj-control-room/', include('dj_control_room.urls')),
    path('admin/', admin.site.urls),
]
```

**How it works:**
- Panels are regular Django apps with standard `urls.py` files
- The control room discovers installed panels via entry points (for the dashboard)
- Users mount panel URLs like any other Django app
- This keeps things simple and gives users full control

## Panel Interface

### Required Attributes

| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| `name` | str | Display name | `"Redis Panel"` |
| `description` | str | Brief description | `"Monitor Redis connections"` |
| `icon` | str | Icon identifier | `"database"` |

### Optional Attributes

| Attribute | Type | Description | Default |
|-----------|------|-------------|---------|
| `app_name` | str | Django app label and URL namespace | Normalized dist name |
| `package` | str | PyPI package name — enables install page | `None` |
| `docs_url` | str | Link to documentation | `None` |
| `pypi_url` | str | Link to PyPI page | `None` |

> **Note on `id`:** Declaring an `id` attribute on your panel class is no longer needed and is silently ignored. The registry key is derived automatically from your PyPI distribution name (e.g. `my-panel` → `my_panel`). This prevents accidental collisions between community panels.

### Optional Methods

All methods are optional with sensible defaults!

#### `get_url_name()` (Optional)

Returns the URL name for your panel's main entry point. Defaults to `"index"` if not implemented.

```python
def get_url_name(self):
    """Return URL name for main entry point"""
    return "index"  # This is the default, so you can omit this method
```

**When to implement:**
- Only if your main view isn't named "index"
- Otherwise, just omit this method and use the default

```python
def get_url_name(self):
    return "dashboard"  # If your main view is named 'dashboard' instead
```

**How it works:**
- DJ Control Room calls: `reverse(f'{panel.app_name}:{get_url_name()}')`
- Example: app_name='dj_cache_panel', get_url_name()='index' → `reverse('dj_cache_panel:index')` → `/dj_cache_panel/`

## How It Works: Execution Flow

Understanding the order of operations:

1. **App Initialization** - When Django starts, DJ Control Room discovers your panel via entry points. The registry key is derived from your distribution's `dist.name` (hyphens → underscores).
2. **URL Mounting** - Users include your panel's URLs in their project `urls.py` (like any Django app)
3. **Dashboard Rendering** - When rendering the dashboard, DJ Control Room:
   - Reads `panel.app_name` (defaults to normalized dist name if not set)
   - Calls `get_url_name()` (defaults to "index")
   - Resolves URL: `reverse(f'{panel.app_name}:{url_name}')`
4. **User Navigation** - User clicks and navigates to your panel

**Key Points:**
- ✅ Your panel uses its **own namespace** (`app_name` in urls.py must match `panel.app_name`)
- ✅ No `id` attribute needed — the registry key is collision-proof by design
- ✅ DJ Control Room handles URL resolution, you just provide the name
- ✅ Convention over configuration: defaults to "index" if not specified
- ✅ No need to import `reverse` in your panel class

**Example:**
```python
# panel.py — for a package named "my-awesome-panel"
class MyPanel:
    name = "Awesome Panel"
    description = "An awesome panel"
    icon = "chart"
    # No id needed. Registry key = "my_awesome_panel" (from dist name)
    # app_name defaults to "my_awesome_panel" automatically

# urls.py
app_name = 'my_awesome_panel'  # Must match panel.app_name
urlpatterns = [
    path('', views.index, name='index'),
]
```

**Result:**
- User includes `path('', include('my_awesome_panel.urls'))` in their urls.py
- User visits dashboard → DJ Control Room calls `reverse('my_awesome_panel:index')`
- User clicks panel → routes to wherever they mounted it → `my_awesome_panel:index` view

## Available Icons

Current built-in icons:
- `database` - Database/storage panels
- `layers` - Cache/layered systems
- `chart` - Analytics/metrics panels
- `link` - URL/routing panels
- `radio` - Signals/events panels
- `alert` - Error/monitoring panels

## Optional: Using BasePanel

You can optionally inherit from `BasePanel` for convenience:

```python
from dj_control_room.panels import BasePanel

class MyPanel(BasePanel):
    name = "My Panel"
    description = "Does cool stuff"
    icon = "chart"
```

## Complete Example

### File Structure
```
my-monitoring-panel/
├── pyproject.toml
├── my_monitoring/
│   ├── __init__.py
│   ├── panel.py          # Panel class
│   ├── views.py          # Django views
│   ├── urls.py           # URL patterns
│   └── templates/        # Templates
└── README.md
```

### panel.py
```python
# For a package named "my-monitoring-panel"
class MonitoringPanel:
    name = "Monitoring Panel"
    description = "Monitor system health and metrics"
    icon = "chart"
    # Registry key = "my_monitoring_panel" (derived from dist name automatically)
    # get_url_name() not needed - defaults to "index"
```

### urls.py
```python
from django.urls import path
from . import views

app_name = 'my_monitoring_panel'  # Must match panel.app_name (= normalized dist name)

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('stats/', views.stats, name='stats'),
]
```

### views.py
```python
from django.shortcuts import render

def index(request):
    """Main panel view"""
    context = {
        'title': 'Monitoring Panel'
    }
    return render(request, 'monitoring/index.html', context)

def dashboard(request):
    # Additional view
    pass

def stats(request):
    # Stats view
    pass
```

### pyproject.toml
```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "my-monitoring-panel"
version = "0.1.0"
dependencies = [
    "Django>=4.2",
    "dj-control-room>=0.1.0",
]

[project.entry-points."dj_control_room.panels"]
my_monitoring_panel = "my_monitoring_panel.panel:MonitoringPanel"
```

## Multiple Panels in One Package

You can register multiple panels from a single package:

```toml
[project.entry-points."dj_control_room.panels"]
panel1 = "mypkg.panels:Panel1"
panel2 = "mypkg.panels:Panel2"
panel3 = "mypkg.panels:Panel3"
```

## Testing Your Panel

### Manual Registration (for testing)

Manual registration requires an explicit `panel_id` since there is no entry point to derive the distribution name from:

```python
from dj_control_room.registry import registry
from myapp.panel import MyPanel

# Register manually — panel_id is required
registry.register(MyPanel, panel_id='my_panel')

# Check if registered
assert registry.is_registered('my_panel')

# Get the panel
panel = registry.get_panel('my_panel')
assert panel._registry_id == 'my_panel'
```

### Unit Test Example

```python
import pytest
from dj_control_room.registry import PanelRegistry
from myapp.panel import MyPanel

def test_panel_registration():
    registry = PanelRegistry()
    registry.register(MyPanel, panel_id='my_panel')

    panels = registry.get_panels()
    assert len(panels) == 1
    assert panels[0]._registry_id == 'my_panel'
    assert panels[0].name == 'My Panel'

def test_panel_url_name():
    panel = MyPanel()
    url_name = panel.get_url_name() if hasattr(panel, 'get_url_name') else 'index'

    assert url_name is not None
    assert isinstance(url_name, str)
    assert url_name  # not empty
```

## Troubleshooting

### Panel Not Appearing

1. **Check if entry point is correct:**
   ```bash
   python -c "from importlib.metadata import entry_points; print(list(entry_points(group='dj_control_room.panels')))"
   ```

2. **Check Django logs:**
   Look for warnings about failed panel loading

3. **Verify required attributes:**
   Make sure your panel has `id`, `name`, `description`, and `icon`

### Common Errors

**"Panel is missing required attribute: name"** (or `description`/`icon`)
- Make sure your panel class defines all required attributes

**"NoReverseMatch" errors**
- Verify `app_name` in your `urls.py` matches `panel.app_name` (which defaults to your normalized dist name)
- Ensure you have a URL named `index` (or implement `get_url_name()`)

**Import errors**
- Verify the entry point path is correct: `package.module:ClassName`

## Best Practices

1. **Follow Conventions**: Use your PyPI dist name (normalized) as your `app_name`, and name your main view "index"
2. **Fast Loading**: Keep your panel views responsive
3. **Error Handling**: Handle errors gracefully in your panel views
4. **Logging**: Use Django's logging to help with debugging
5. **Documentation**: Document what your panel does and its requirements

## Publishing Your Panel

1. **Test thoroughly** in development
2. **Add to PyPI** so others can `pip install` it
3. **Document** installation and configuration
4. **Tag releases** with semantic versioning
5. **List requirements** (Django version, external services, etc.)

## Example Panels

Reference these open-source panels:
- `dj-redis-panel` - Redis monitoring
- `dj-cache-panel` - Django cache inspection
- `dj-celery-panel` - Celery task monitoring

## Need Help?

- Check the [main documentation](https://github.com/yassi/dj-control-room)
- Open an issue for questions
- Submit PRs to improve this guide
