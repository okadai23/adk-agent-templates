"""Type definitions for clean interfaces."""

from enum import StrEnum


class InterfaceType(StrEnum):
    """Available interface types."""

    CLI = "cli"
    RESTAPI = "restapi"
    MCP = "mcp"
