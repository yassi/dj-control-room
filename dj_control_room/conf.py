from dj_control_room_base.core import PanelConfig

panel_config = PanelConfig(
    settings_key="DJ_CONTROL_ROOM_SETTINGS",
    defaults={
        # Admin sidebar integration
        "REGISTER_PANELS_IN_ADMIN": False,
        "PANEL_ADMIN_REGISTRATION": {},
        # MCP Streamable HTTP transport — /admin/dj-control-room/mcp/
        # All three keys are required when MCP_ENABLED is True.
        # MCP_TOKEN:    secret Bearer token checked on every request.
        # MCP_USERNAME: user model identifier (USERNAME_FIELD) whose permissions
        #               apply to tool calls.
        "MCP_ENABLED": False,
        "MCP_TOKEN": None,
        "MCP_USERNAME": None,
    },
)
