"""
MCP Streamable HTTP transport endpoint for dj-control-room.

Exposes all registered panel tools as MCP tools so that Cursor (and other
MCP clients) can discover and call them without a bridge process.

Required Django settings (all three must be set)::

    DJ_CONTROL_ROOM_SETTINGS = {
        "MCP_ENABLED": True,           # False (default) returns 404
        "MCP_TOKEN": "your-secret",    # Bearer token checked on every request
        "MCP_USERNAME": "admin",       # User model identifier (USERNAME_FIELD)
    }

Configure in ``.cursor/mcp.json``::

    {
      "mcpServers": {
        "dj-control-room": {
          "url": "http://localhost:8000/admin/dj-control-room/mcp/",
          "headers": { "Authorization": "Bearer <your-token>" }
        }
      }
    }
"""

import json
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .conf import panel_config
from .registry import registry

logger = logging.getLogger(__name__)

_PROTOCOL_VERSION = "2024-11-05"
_SERVER_INFO = {"name": "dj-control-room", "version": "1.0.0"}


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------


class _MisconfiguredError(Exception):
    """Raised when MCP settings are present but incomplete."""


def _resolve_user():
    """
    Return the Django User configured for MCP access.

    MCP_USERNAME must be set explicitly — there is no fallback.  This is
    intentional: silently running as the first superuser in the database is a
    dangerous default that could grant unintended access.
    """
    from django.contrib.auth import get_user_model

    User = get_user_model()

    username = panel_config.get_settings("MCP_USERNAME")
    if not username:
        raise _MisconfiguredError(
            "MCP_USERNAME is not set in DJ_CONTROL_ROOM_SETTINGS. "
            f"Set it to the {User.USERNAME_FIELD} of the Django user whose "
            "permissions should apply to MCP tool calls."
        )

    user = User.objects.filter(
        **{User.USERNAME_FIELD: username}, is_staff=True, is_active=True
    ).first()
    if user is None:
        raise _MisconfiguredError(
            f"MCP_USERNAME '{username}' does not match any active staff user "
            f"(matched against the '{User.USERNAME_FIELD}' field)."
        )
    return user


def _authenticate(request):
    """
    Validate the Bearer token from the Authorization header.

    Returns a Django User on success, raises _MisconfiguredError for config
    problems, or returns None for auth failures (wrong / missing token).
    """
    configured_token = panel_config.get_settings("MCP_TOKEN")

    if not configured_token:
        raise _MisconfiguredError("MCP_TOKEN is not set in DJ_CONTROL_ROOM_SETTINGS.")

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None

    provided_token = auth_header[len("Bearer ") :]
    if provided_token != configured_token:
        return None

    return _resolve_user()


# ---------------------------------------------------------------------------
# JSON-RPC helpers
# ---------------------------------------------------------------------------


def _result(rpc_id, result):
    return {"jsonrpc": "2.0", "id": rpc_id, "result": result}


def _error(rpc_id, code, message):
    return {"jsonrpc": "2.0", "id": rpc_id, "error": {"code": code, "message": message}}


# ---------------------------------------------------------------------------
# MCP method handlers
# ---------------------------------------------------------------------------


def _handle_initialize(rpc_id, params):
    return _result(
        rpc_id,
        {
            "protocolVersion": _PROTOCOL_VERSION,
            "capabilities": {"tools": {}},
            "serverInfo": _SERVER_INFO,
        },
    )


def _handle_tools_list(rpc_id, user):
    tools = registry.get_tools_for_user(user)
    return _result(
        rpc_id,
        {
            "tools": [
                {
                    "name": key,
                    "description": tool.description,
                    # MCP spec uses camelCase for the schema key
                    "inputSchema": tool.input_schema,
                }
                for key, (panel, tool) in tools.items()
            ]
        },
    )


def _handle_tools_call(rpc_id, params, user):
    from dj_control_room_base.core.panel_tool import PanelToolContext

    tool_name = params.get("name")
    arguments = params.get("arguments") or {}

    if not tool_name:
        return _error(rpc_id, -32602, "Missing required param: name")

    available = registry.get_tools_for_user(user)
    if tool_name not in available:
        return _error(
            rpc_id, -32602, f"Tool '{tool_name}' not found or not accessible."
        )

    panel, tool = available[tool_name]
    config = panel.get_config()
    ctx = PanelToolContext(user=user, inputs=arguments, config=config)

    try:
        outcome = tool.handler(ctx)
    except Exception as exc:
        logger.exception("MCP tool '%s' raised an exception", tool_name)
        return _result(
            rpc_id,
            {
                "content": [{"type": "text", "text": str(exc)}],
                "isError": True,
            },
        )

    text = json.dumps({"message": outcome.message, "data": outcome.data}, indent=2)
    return _result(
        rpc_id,
        {
            "content": [{"type": "text", "text": text}],
            "isError": not outcome.success,
        },
    )


# ---------------------------------------------------------------------------
# View
# ---------------------------------------------------------------------------


@csrf_exempt
@require_POST
def mcp_endpoint(request):
    """
    MCP Streamable HTTP transport — single POST endpoint.

    Handles JSON-RPC 2.0 requests: initialize, tools/list, tools/call.
    Notifications (messages with no ``id``) return HTTP 202 with an empty body.

    Disabled entirely when ``DJ_CONTROL_ROOM_SETTINGS["MCP_ENABLED"]`` is False
    (returns 404).  Requires both ``MCP_TOKEN`` and ``MCP_USERNAME`` to be set.
    """
    if not panel_config.get_settings("MCP_ENABLED"):
        from django.http import Http404

        raise Http404

    try:
        user = _authenticate(request)
    except _MisconfiguredError as exc:
        logger.error("MCP endpoint misconfigured: %s", exc)
        return JsonResponse(
            _error(None, -32603, f"Server misconfiguration: {exc}"),
            status=500,
        )

    if user is None:
        return JsonResponse(
            _error(None, -32600, "Unauthorized."),
            status=401,
        )

    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(_error(None, -32700, "Parse error."), status=400)

    if not isinstance(body, dict):
        return JsonResponse(_error(None, -32600, "Invalid Request."), status=400)

    # JSON-RPC notifications have no "id" key — acknowledge and move on.
    if "id" not in body:
        return JsonResponse({}, status=202)

    method = body.get("method", "")
    params = body.get("params") or {}
    if not isinstance(params, dict):
        return JsonResponse(_error(body.get("id"), -32602, "Invalid params."), status=400)
    rpc_id = body.get("id")

    if method == "initialize":
        response = _handle_initialize(rpc_id, params)
    elif method == "tools/list":
        response = _handle_tools_list(rpc_id, user)
    elif method == "tools/call":
        response = _handle_tools_call(rpc_id, params, user)
    else:
        response = _error(rpc_id, -32601, f"Method not found: {method}")

    return JsonResponse(response)
