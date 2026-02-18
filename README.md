[![Tests](https://github.com/yassi/dj-control-room/actions/workflows/test.yml/badge.svg)](https://github.com/yassi/dj-control-room/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/yassi/dj-control-room/branch/main/graph/badge.svg)](https://codecov.io/gh/yassi/dj-control-room)
[![PyPI version](https://badge.fury.io/py/dj-control-room.svg)](https://badge.fury.io/py/dj-control-room)
[![Python versions](https://img.shields.io/pypi/pyversions/dj-control-room.svg)](https://pypi.org/project/dj-control-room/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/yassi/dj-control-room/main/images/hero-dark.png">
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/yassi/dj-control-room/main/images/hero-light.png">
    <img alt="Django Control Room" src="https://raw.githubusercontent.com/yassi/dj-control-room/main/images/hero-light.png">
  </picture>
</p>

<h1 align="center">Django Control Room</h1>
<p align="center">
  <strong>A centralized dashboard for managing Django admin panels</strong>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#panels">Official Panels</a> •
  <a href="https://yassi.github.io/dj-control-room/">Documentation</a>
</p>

---

## Features

- **Centralized Dashboard** - All your admin panels in one place
- **Plugin System** - Discover and install panels via PyPI
- **Beautiful UI** - Modern, responsive design with dark mode support
- **Secure** - Package verification prevents panel hijacking
- **Easy Integration** - Works seamlessly with Django admin
- **Official Panels** - Pre-built panels for common tasks

![Django Control Room Dashboard](https://raw.githubusercontent.com/yassi/dj-control-room/main/images/full-screenshot.png)

## Installation

### Basic Installation

```bash
pip install dj-control-room
```

### Install with Official Panels

```bash
# Install with specific panels
pip install dj-control-room[redis,cache,urls]

# Or install with all official panels
pip install dj-control-room[all]
```

**Available panel extras:**
- `redis` - Redis connection manager and inspector
- `cache` - Django cache backend inspector
- `urls` - URL pattern browser and tester
- `celery` - Celery task monitor
- `signals` - Django signals inspector (coming soon)
- `all` - All official panels

## Quick Start

### 1. Add to INSTALLED_APPS

```python
# settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Django Control Room
    'dj_control_room',
    
    # Add any panels you installed
    'dj_redis_panel',
    'dj_cache_panel',
    'dj_urls_panel',
    
    # Your apps
    # ...
]
```

### 2. Configure URLs

```python
# urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Panel URLs (include each panel you installed)
    path('admin/dj-redis-panel/', include('dj_redis_panel.urls')),
    path('admin/dj-cache-panel/', include('dj_cache_panel.urls')),
    path('admin/dj-urls-panel/', include('dj_urls_panel.urls')),
    
    # Control Room dashboard
    path('admin/dj-control-room/', include('dj_control_room.urls')),
    
    # Django admin
    path('admin/', admin.site.urls),
]
```

### 3. Access the Control Room

1. Run migrations: `python manage.py migrate`
2. Start your server: `python manage.py runserver`
3. Navigate to `http://localhost:8000/admin/dj-control-room/`

## Admin Sidebar Integration

All installed panels appear in the Django admin sidebar under "Django Control Room":

<img src="https://raw.githubusercontent.com/yassi/dj-control-room/main/images/sidebar.png" alt="Admin Sidebar" width="300">

### Control Sidebar Behavior (Optional)

```python
# settings.py
DJ_CONTROL_ROOM_SETTINGS = {
    # Global: Show panels in both Control Room and their own sections
    'REGISTER_PANELS_IN_ADMIN': False,  # Default: False
    
    # Per-panel: Override for specific panels
    'PANEL_ADMIN_REGISTRATION': {
        'dj_redis_panel': True,   # Redis in both places
        'dj_cache_panel': False,  # Cache only in Control Room
    }
}
```

## Official Panels

<div align="center">
  <img src="https://raw.githubusercontent.com/yassi/dj-control-room/main/images/grid_image.png" alt="Official Panels" width="800">
</div>

### Available Now

| Panel | Description | Install |
|-------|-------------|---------|
| **Redis Panel** | Monitor connections, inspect keys, view memory usage | `pip install dj-redis-panel` |
| **Cache Panel** | Inspect cache entries, view hit/miss ratios | `pip install dj-cache-panel` |
| **URLs Panel** | Browse URL patterns, test resolvers | `pip install dj-urls-panel` |
| **Celery Panel** | Monitor workers, track task queues | `pip install dj-celery-panel` |

### Coming Soon

| Panel | Description | Status |
|-------|-------------|--------|
| **Signals Panel** | Inspect Django signals, debug connections | In Development |
| **Error Panel** | Monitor errors, exceptions, and tracebacks | In Development |

## Creating Custom Panels

Want to create your own panel? It's easy!

```python
# my_panel/panel.py
class MyPanel:
    id = "my_panel"
    name = "My Panel"
    description = "My awesome panel"
    icon = "chart"
    
    def get_url_name(self):
        return "index"
```

```toml
# pyproject.toml
[project.entry-points."dj_control_room.panels"]
my_panel = "my_panel.panel:MyPanel"
```

See our [Creating Panels Guide](docs/creating-panels.md) for full documentation.

## Security

Django Control Room includes built-in security features:

- **Package Verification** - Featured panels are verified by package origin
- **Staff-Only Access** - Requires Django staff/superuser permissions
- **No Malicious Hijacking** - Prevents panels from impersonating official packages

## Documentation

Full documentation is available at: **[https://yassi.github.io/dj-control-room/](https://yassi.github.io/dj-control-room/)**

- [Installation Guide](docs/installation.md)
- [Configuration](docs/configuration.md)
- [Creating Panels](docs/creating-panels.md)
- [API Reference](docs/api-reference.md)

## Requirements

- Python 3.9+
- Django 4.2+

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

Created by [Yasser Toruno](https://github.com/yassi)

---

<p align="center">
  <a href="https://github.com/yassi/dj-control-room">Star us on GitHub</a> •
  <a href="https://github.com/yassi/dj-control-room/issues">Report Bug</a> •
  <a href="https://github.com/yassi/dj-control-room/issues">Request Feature</a>
</p>
