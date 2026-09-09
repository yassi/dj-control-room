"""
Tests for the MCP HTTP transport endpoint.

Covers authentication, JSON-RPC protocol validation, and the three
supported methods: initialize, tools/list, tools/call.
"""

import json

from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model

User = get_user_model()

MCP_URL = "/admin/dj-control-room/mcp/"

MCP_SETTINGS = {
    "MCP_ENABLED": True,
    "MCP_TOKEN": "test-secret",
    "MCP_USERNAME": "mcp_user",
}


def _post(client, payload, token="test-secret"):
    """POST a JSON-RPC payload to the MCP endpoint with a Bearer token."""
    headers = {"HTTP_AUTHORIZATION": f"Bearer {token}"}
    return client.post(
        MCP_URL,
        data=json.dumps(payload),
        content_type="application/json",
        **headers,
    )


class MCPTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="mcp_user",
            password="testpass",
            is_staff=True,
            is_active=True,
        )


class TestMCPDisabled(TestCase):
    """When MCP_ENABLED is False (the default) the endpoint returns 404."""

    def test_returns_404_when_disabled(self):
        from django.test import Client

        client = Client()
        response = client.post(
            MCP_URL,
            data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize"}),
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer test-secret",
        )
        self.assertEqual(response.status_code, 404)


@override_settings(DJ_CONTROL_ROOM_SETTINGS=MCP_SETTINGS)
class TestAuthentication(MCPTestCase):
    def test_missing_auth_header_returns_401(self):
        from django.test import Client

        client = Client()
        response = client.post(
            MCP_URL,
            data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertEqual(data["error"]["code"], -32600)

    def test_wrong_token_returns_401(self):
        from django.test import Client

        client = Client()
        response = _post(
            client, {"jsonrpc": "2.0", "id": 1, "method": "initialize"}, token="wrong"
        )
        self.assertEqual(response.status_code, 401)

    def test_correct_token_is_accepted(self):
        from django.test import Client

        client = Client()
        response = _post(client, {"jsonrpc": "2.0", "id": 1, "method": "initialize"})
        self.assertEqual(response.status_code, 200)

    @override_settings(DJ_CONTROL_ROOM_SETTINGS={**MCP_SETTINGS, "MCP_TOKEN": None})
    def test_misconfigured_token_returns_500(self):
        from django.test import Client

        client = Client()
        response = _post(client, {"jsonrpc": "2.0", "id": 1, "method": "initialize"})
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertEqual(data["error"]["code"], -32603)

    @override_settings(
        DJ_CONTROL_ROOM_SETTINGS={**MCP_SETTINGS, "MCP_USERNAME": "no_such_user"}
    )
    def test_misconfigured_username_returns_500(self):
        from django.test import Client

        client = Client()
        response = _post(client, {"jsonrpc": "2.0", "id": 1, "method": "initialize"})
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertEqual(data["error"]["code"], -32603)


@override_settings(DJ_CONTROL_ROOM_SETTINGS=MCP_SETTINGS)
class TestProtocolValidation(MCPTestCase):
    def setUp(self):
        super().setUp()
        from django.test import Client

        self.client = Client()

    def test_invalid_json_returns_parse_error(self):
        response = self.client.post(
            MCP_URL,
            data="not-json{{{",
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer test-secret",
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["error"]["code"], -32700)

    def test_json_array_returns_invalid_request(self):
        response = _post(
            self.client, [{"jsonrpc": "2.0", "id": 1, "method": "initialize"}]
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["error"]["code"], -32600)

    def test_json_scalar_returns_invalid_request(self):
        response = self.client.post(
            MCP_URL,
            data="123",
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer test-secret",
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["error"]["code"], -32600)

    def test_notification_no_id_returns_202(self):
        """A JSON-RPC message without an 'id' is a notification — 202, no body."""
        response = _post(self.client, {"jsonrpc": "2.0", "method": "initialized"})
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.json(), {})

    def test_params_as_list_returns_invalid_params(self):
        response = _post(
            self.client,
            {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": ["bad"]},
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["error"]["code"], -32602)
        self.assertEqual(data["id"], 1)

    def test_unknown_method_returns_method_not_found(self):
        response = _post(
            self.client, {"jsonrpc": "2.0", "id": 1, "method": "no/such/method"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["error"]["code"], -32601)
        self.assertIn("no/such/method", data["error"]["message"])

    def test_get_method_not_allowed(self):
        response = self.client.get(MCP_URL, HTTP_AUTHORIZATION="Bearer test-secret")
        self.assertEqual(response.status_code, 405)


@override_settings(DJ_CONTROL_ROOM_SETTINGS=MCP_SETTINGS)
class TestInitialize(MCPTestCase):
    def setUp(self):
        super().setUp()
        from django.test import Client

        self.client = Client()

    def test_initialize_returns_protocol_version(self):
        response = _post(
            self.client,
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("result", data)
        self.assertIn("protocolVersion", data["result"])
        self.assertIn("capabilities", data["result"])
        self.assertIn("serverInfo", data["result"])

    def test_initialize_echoes_rpc_id(self):
        response = _post(
            self.client,
            {"jsonrpc": "2.0", "id": "abc", "method": "initialize"},
        )
        self.assertEqual(response.json()["id"], "abc")

    def test_initialize_response_structure(self):
        response = _post(
            self.client,
            {"jsonrpc": "2.0", "id": 42, "method": "initialize"},
        )
        data = response.json()
        self.assertEqual(data["jsonrpc"], "2.0")
        self.assertNotIn("error", data)
        self.assertEqual(data["result"]["serverInfo"]["name"], "dj-control-room")


@override_settings(DJ_CONTROL_ROOM_SETTINGS=MCP_SETTINGS)
class TestToolsList(MCPTestCase):
    def setUp(self):
        super().setUp()
        from django.test import Client

        self.client = Client()

    def test_tools_list_returns_tools_key(self):
        response = _post(
            self.client, {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("result", data)
        self.assertIn("tools", data["result"])
        self.assertIsInstance(data["result"]["tools"], list)

    def test_tools_list_echoes_rpc_id(self):
        response = _post(
            self.client, {"jsonrpc": "2.0", "id": 99, "method": "tools/list"}
        )
        self.assertEqual(response.json()["id"], 99)


@override_settings(DJ_CONTROL_ROOM_SETTINGS=MCP_SETTINGS)
class TestToolsCall(MCPTestCase):
    def setUp(self):
        super().setUp()
        from django.test import Client

        self.client = Client()

    def test_missing_name_param_returns_error(self):
        response = _post(
            self.client,
            {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {}},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("error", data)
        self.assertEqual(data["error"]["code"], -32602)
        self.assertIn("name", data["error"]["message"])

    def test_unknown_tool_returns_error(self):
        response = _post(
            self.client,
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {"name": "no_such_panel__no_such_tool"},
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("error", data)
        self.assertEqual(data["error"]["code"], -32602)
        self.assertIn("no_such_panel__no_such_tool", data["error"]["message"])
