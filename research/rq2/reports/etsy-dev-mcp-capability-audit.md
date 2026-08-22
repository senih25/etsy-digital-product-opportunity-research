# Etsy Dev MCP Capability Audit

## Summary

- MCP endpoint: `https://mcp.api.etsycloud.com/mcp`
- Local Codex config: added as `[mcp_servers.etsy]` in `~/.codex/config.toml`
- Connection status: not verified in this Codex session
- Available tools in the official Etsy Dev MCP docs:
  - `learn_etsy_api`
  - `search_etsy_api`
  - `list_endpoints`
  - `get_endpoint`
  - `get_schema`
  - `list_guides`
  - `get_guide`
- Auth requirement: no Etsy marketplace API auth is documented for the MCP endpoint itself; it is a documentation/specification server, not a live marketplace API client
- Endpoint/schema lookup: documented as available in the Etsy Dev MCP product, but not exposed through the current Codex session

## Evidence

- The official Etsy Dev MCP page documents the endpoint URL and the tool list.
- `tool_search` in this session did not expose Etsy Dev MCP tools after local config was updated.

## Limitations

- The MCP server is spec authority only.
- It must not be used to execute live Etsy marketplace API calls.
- This audit does not claim live endpoint invocation success.

## Note

The official docs page says the server provides five tools, but the list shown on the page contains seven named tools. The tool names above follow the explicit list on the page.

