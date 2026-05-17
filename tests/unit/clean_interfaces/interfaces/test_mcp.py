"""Tests for MCP interface implementation."""

from collections.abc import Callable
from unittest.mock import MagicMock, patch

from fastmcp import FastMCP

from clean_interfaces.interfaces.base import BaseInterface
from clean_interfaces.interfaces.mcp import MCPInterface


class TestMCPInterface:
    """Test MCP interface functionality."""

    def test_mcp_interface_inherits_base(self) -> None:
        """Test that MCPInterface inherits from BaseInterface."""
        assert issubclass(MCPInterface, BaseInterface)

    def test_mcp_interface_has_name(self) -> None:
        """Test that MCPInterface has correct name."""
        mcp = MCPInterface()
        assert mcp.name == "MCP"

    def test_mcp_interface_has_fastmcp_app(self) -> None:
        """Test that MCPInterface has FastMCP app."""
        mcp = MCPInterface()
        assert hasattr(mcp, "mcp")
        assert isinstance(mcp.mcp, FastMCP)

    def test_mcp_registers_welcome_command(self) -> None:
        """Test that MCP setup registers welcome command."""
        registered_names: list[str] = []

        def fake_tool() -> object:
            def register(func: Callable[..., object]) -> Callable[..., object]:
                registered_names.append(func.__name__)
                return func

            return register

        with patch("fastmcp.FastMCP.tool", return_value=fake_tool()):
            MCPInterface()

        assert "welcome" in registered_names

    @patch("fastmcp.FastMCP.run")
    def test_mcp_run_method(self, mock_run: MagicMock) -> None:
        """Test MCP run method executes fastmcp app."""
        mcp = MCPInterface()
        mcp.run()
        mock_run.assert_called_once()
