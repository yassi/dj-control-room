# Configuration

DJ Control Room currently works out of the box with minimal configuration.

## Basic Setup

The only required configuration is adding the app to your `INSTALLED_APPS` and including the URLs in your URL configuration.

See the [Installation](installation.md) guide for setup instructions.

## URLs Configuration

```python
# urls.py
urlpatterns = [
    path('admin/dj-control-room/', include('dj_control_room.urls')),  # Custom path
    path('admin/', admin.site.urls),
]
```

## Security

DJ Control Room uses Django's built-in admin authentication:

- Only staff users (`is_staff=True`) can access the panel
- All views require authentication via `@staff_member_required`
- No additional security configuration needed

## Advanced Configuration

Advanced configuration options will be added in future releases.
