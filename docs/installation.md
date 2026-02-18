# Installation Guide

This guide will walk you through installing Django Control Room and its panels.

Official Site: **[djangocontrolroom.com](https://djangocontrolroom.com)**.

![Django Control Room Dashboard](https://raw.githubusercontent.com/yassi/dj-control-room/main/images/full-screenshot.png)

## Basic Installation

Install Django Control Room via pip:

```bash
pip install dj-control-room
```

This installs the core Control Room without any panels.

## Install with Official Panels

Django Control Room supports installation with optional panel extras:

### Install Specific Panels

```bash
# Single panel
pip install dj-control-room[redis]

# Multiple panels
pip install dj-control-room[redis,cache,urls]
```

### Install All Panels

```bash
pip install dj-control-room[all]
```

## Available Panel Extras

| Extra | Package | Description |
|-------|---------|-------------|
| `redis` | `dj-redis-panel` | Redis connection manager and key inspector |
| `cache` | `dj-cache-panel` | Django cache backend inspector |
| `urls` | `dj-urls-panel` | URL pattern browser and tester |
| `celery` | `dj-celery-panel` | Celery task monitor |
| `signals` | `dj-signals-panel` | Django signals inspector (coming soon) |
| `all` | All panels | Install all official panels at once |

## Django Configuration

### 1. Add to INSTALLED_APPS

Add `dj_control_room` and any installed panels to your `INSTALLED_APPS`:

```python
# settings.py
INSTALLED_APPS = [
    # Django built-in apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Django Control Room (Required)
    'dj_control_room',
    
    # Panels (Add the ones you installed)
    'dj_redis_panel',   # If you installed [redis]
    'dj_cache_panel',   # If you installed [cache]
    'dj_urls_panel',    # If you installed [urls]
    'dj_celery_panel',  # If you installed [celery]
    'dj_signals_panel', # If you installed [signals]
    
    # Your apps
    'myapp',
    # ...
]
```

> **Note:** Panels are automatically discovered via entry points, so Django Control Room will detect them even if you install them separately.

### 2. Configure URLs

Include Django Control Room and panel URLs in your project's `urls.py`:

```python
# urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Panel URLs - include each panel you installed
    path('admin/dj-redis-panel/', include('dj_redis_panel.urls')),
    path('admin/dj-cache-panel/', include('dj_cache_panel.urls')),
    path('admin/dj-urls-panel/', include('dj_urls_panel.urls')),
    path('admin/dj-celery-panel/', include('dj_celery_panel.urls')),
    path('admin/dj-signals-panel/', include('dj_signals_panel.urls')),
    
    # Control Room dashboard
    path('admin/dj-control-room/', include('dj_control_room.urls')),
    
    # Django admin
    path('admin/', admin.site.urls),
]
```

> **Important:** Panels are mounted with explicit paths under `/admin/` to keep them integrated with Django admin. Each panel appears at its own admin-local URL like `/admin/dj-redis-panel/`.

### 3. Run Migrations

```bash
python manage.py migrate
```

> **Note:** Django Control Room itself has no migrations. This step is just for standard Django setup.

### 4. Collect Static Files (Production)

For production deployments:

```bash
python manage.py collectstatic
```

## Verify Installation

Once installed, your admin sidebar will show Django Control Room with all your panels:

<img src="https://raw.githubusercontent.com/yassi/dj-control-room/main/images/sidebar.png" alt="Admin Sidebar" width="300">

### Check Panel Discovery

Verify that panels are discovered correctly:

```bash
python manage.py shell
```

```python
from dj_control_room.registry import registry

registry.autodiscover()
for panel in registry.get_panels():
    print(f"{panel.name} ({panel.id})")
```

### Access the Dashboard

1. Start your development server:
   ```bash
   python manage.py runserver
   ```

2. Navigate to: `http://127.0.0.1:8000/admin/dj-control-room/`

3. You should see the Control Room dashboard with your installed panels:

![Django Control Room Dashboard](https://raw.githubusercontent.com/yassi/dj-control-room/main/images/full-screenshot.png)

## Troubleshooting

### Panels Not Showing Up

If panels don't appear in the dashboard:

1. Check INSTALLED_APPS - Ensure both `dj_control_room` and the panel apps are in `INSTALLED_APPS`
2. Check URLs - Verify panel URLs are included in your `urls.py`
3. Restart server - Django may need to be restarted to discover entry points
4. Check installation:
   ```bash
   pip list | grep dj-
   ```

### URL Resolution Errors

If you get `NoReverseMatch` errors:

1. Ensure panel URLs are included at root level (not nested)
2. Check that panel's `urls.py` defines `app_name` matching the panel ID
3. Verify URL patterns in panel's `urls.py` include an `index` view

### Package Not Found

If pip can't find the package:

1. Check PyPI - Ensure the package exists: https://pypi.org/project/dj-control-room/
2. Update pip:
   ```bash
   pip install --upgrade pip
   ```
3. Try direct install:
   ```bash
   pip install dj-control-room==0.1.0  # Specify version
   ```

## Next Steps

- [Configuration Guide](configuration.md) - Learn about available settings
- [Creating Panels](creating-panels.md) - Build your own panels
- [API Reference](api-reference.md) - Detailed API documentation

## Upgrading

To upgrade to the latest version:

```bash
pip install --upgrade dj-control-room
```

To upgrade with panels:

```bash
pip install --upgrade dj-control-room[all]
```
