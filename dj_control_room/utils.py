"""
Utility functions for DJ Control Room.
"""
from django.conf import settings


def should_register_panel_admin(panel_id=None):
    """
    Check if a panel should register its own admin entry.
    
    This allows end users to control whether panels show up in both
    DJ Control Room AND their own admin section, or only in DJ Control Room.
    
    Args:
        panel_id: The panel ID to check (optional, for granular control)
    
    Returns:
        bool: True if panel should register in admin, False otherwise
        
    Examples:
        # Simple boolean for all panels
        DJ_CONTROL_ROOM = {
            'REGISTER_PANELS_IN_ADMIN': True  # Panels show in both places
        }
        
        # Granular per-panel control
        DJ_CONTROL_ROOM = {
            'PANEL_ADMIN_REGISTRATION': {
                'redis': True,   # Redis shows in both places
                'cache': False,  # Cache only in Control Room
                '*': False,      # Default for others
            }
        }
    """
    config = getattr(settings, 'DJ_CONTROL_ROOM', {})
    
    # Per-panel settings take precedence when provided (explicit allow/deny per panel)
    if panel_id and 'PANEL_ADMIN_REGISTRATION' in config:
        panel_settings = config['PANEL_ADMIN_REGISTRATION']
        if panel_id in panel_settings or '*' in panel_settings:
            return panel_settings.get(panel_id, panel_settings.get('*', False))
    
    # Global setting for all panels
    if 'REGISTER_PANELS_IN_ADMIN' in config:
        return config['REGISTER_PANELS_IN_ADMIN']
    
    # Default: don't register in admin (only show in Control Room)
    return False
