# Django Control Room Documentation

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/yassi/dj-control-room/main/images/hero-dark.png">
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/yassi/dj-control-room/main/images/hero-light.png">
    <img alt="Django Control Room" src="https://raw.githubusercontent.com/yassi/dj-control-room/main/images/hero-light.png">
  </picture>
</p>

Welcome to the Django Control Room documentation!

## Getting Started

New to Django Control Room? Start here:

1. **[Installation Guide](installation.md)** - Install Django Control Room and panels
2. **[Quick Start](#quick-start)** - Get up and running in 5 minutes
3. **[Configuration](configuration.md)** - Customize behavior and settings

## Quick Start

```bash
# Install with panels
pip install dj-control-room[all]
```

```python
# settings.py
INSTALLED_APPS = [
    # ...
    'dj_control_room',
    'dj_redis_panel',
    'dj_cache_panel',
    'dj_urls_panel',
]
```

```python
# urls.py
urlpatterns = [
    path('admin/dj-redis-panel/', include('dj_redis_panel.urls')),
    path('admin/dj-cache-panel/', include('dj_cache_panel.urls')),
    path('admin/dj-urls-panel/', include('dj_urls_panel.urls')),
    path('admin/dj-control-room/', include('dj_control_room.urls')),
    path('admin/', admin.site.urls),
]
```

Visit: `http://localhost:8000/admin/dj-control-room/`

![Django Control Room Dashboard](https://raw.githubusercontent.com/yassi/dj-control-room/main/images/full-screenshot.png)

## Documentation

### User Guides

- **[Installation Guide](installation.md)** - Step-by-step installation instructions
- **[Configuration](configuration.md)** - Settings and customization options

### Developer Guides

- **[Creating Panels](creating-panels.md)** - Build custom panels
- **[API Reference](api-reference.md)** - Complete API documentation

### Panel Documentation

Official panel documentation:

- [Redis Panel](https://github.com/yassi/dj-redis-panel) - Redis monitoring and key inspection
- [Cache Panel](https://github.com/yassi/dj-cache-panel) - Django cache backend inspection
- [URLs Panel](https://github.com/yassi/dj-urls-panel) - URL pattern browsing and testing

## Features

### Centralized Dashboard

All your admin panels in one unified dashboard. No more hunting through the admin sidebar.

![Panel Grid](https://raw.githubusercontent.com/yassi/dj-control-room/main/images/grid_image.png)

### Plugin System

Install panels from PyPI with a single command:

```bash
pip install dj-control-room[redis,cache,urls,celery]
```

### Beautiful UI

Modern, responsive design that looks great in both light and dark mode.

### Secure by Default

- Staff-only access
- Package verification for official panels
- Protection against panel hijacking

### Official Panels

Pre-built panels for common Django tasks:

- **Redis Panel** - Monitor Redis connections and inspect keys
- **Cache Panel** - Inspect Django cache backends
- **URLs Panel** - Browse and test URL patterns
- **Celery Panel** - Monitor Celery tasks
- **Signals Panel** (coming soon) - Debug Django signals
- **Error Panel** (coming soon) - Monitor errors and exceptions

## Architecture

### Panel Discovery

Panels are discovered via Python entry points:

```toml
[project.entry-points."dj_control_room.panels"]
my_panel = "my_panel.panel:MyPanel"
```

When Django starts, Django Control Room:
1. Scans for entry points in the `dj_control_room.panels` group
2. Loads panel classes
3. Validates required attributes
4. Registers panels in the global registry

### URL Structure

- `/admin/dj-control-room/` - Control Room dashboard
- `/admin/dj-redis-panel/` - Redis panel
- `/admin/dj-cache-panel/` - Cache panel
- etc.

Panels are mounted at root level for clean URLs.

### Admin Integration

Django Control Room automatically:
1. Creates proxy models for each panel
2. Registers them under "Django Control Room" in admin sidebar
3. Unregisters panel placeholder models (unless configured otherwise)

## Requirements

- Python 3.9+
- Django 4.2+

## Support

Need help? Here's how to get support:

- **[GitHub Discussions](https://github.com/yassi/dj-control-room/discussions)** - Ask questions
- **[Issue Tracker](https://github.com/yassi/dj-control-room/issues)** - Report bugs
- **[GitHub Repository](https://github.com/yassi/dj-control-room)** - View source code

## Contributing

We welcome contributions! Please check the GitHub repository for contribution guidelines.

## License

Django Control Room is licensed under the MIT License.

## Credits

Created by [Yasser Toruno](https://github.com/yassi)

---

## What's Next?

- **First time?** → [Installation Guide](installation.md)
- **Setting up?** → [Configuration](configuration.md)  
- **Building a panel?** → [Creating Panels](creating-panels.md)
- **Need API details?** → [API Reference](api-reference.md)
