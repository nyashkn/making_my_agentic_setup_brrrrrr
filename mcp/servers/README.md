# MCP Servers

This directory contains Model Context Protocol (MCP) server configurations and custom implementations.

## Structure

```
mcp/
├── servers/
│   ├── custom-server-1/
│   │   ├── server.py          # Server implementation
│   │   ├── requirements.txt   # Dependencies
│   │   └── README.md          # Setup instructions
│   └── custom-server-2/
│       └── ...
└── plugins.toml              # Plugin configurations
```

## Installing MCP Servers

```bash
# List available MCP servers
task mcp:list

# Install an MCP server
task mcp:install -- server-name
```

## Creating MCP Servers

1. Create new directory in `mcp/servers/`
2. Implement server following MCP specification
3. Add `requirements.txt` for dependencies
4. Add `README.md` with setup instructions
5. Update `plugins.toml` with configuration
6. Commit to repo for sharing

## Example Server Structure

```
mcp/servers/my-server/
├── server.py              # Main server implementation
├── requirements.txt       # python-mcp-sdk>=0.1.0
├── README.md             # Setup and usage
└── config.example.json   # Configuration template
```

## Plugin Configuration

Edit `mcp/plugins.toml` to configure MCP plugins:

```toml
[servers.my-server]
command = "python"
args = ["mcp/servers/my-server/server.py"]
env = {API_KEY = "..."}
```

## Usage

MCP servers extend Claude Code capabilities by providing:
- Custom tools and functions
- External API integrations
- Database connections
- File system operations

See MCP documentation: https://modelcontextprotocol.io
