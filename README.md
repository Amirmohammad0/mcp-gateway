# MCP gateway

Small MCP server (streamable HTTP) that proxies to an OpenAI-compatible gateway.
Tools: list_models, chat, chat_messages.

## Deploy
1. Install uv, then: `uv sync`
2. `cp .env.example .env` and fill in GATEWAY_API_KEY
3. Copy `deploy/mcp-gateway.service` to /etc/systemd/system/ (check the ExecStart path)
4. `systemctl daemon-reload && systemctl enable --now mcp-gateway`
5. Put `deploy/Caddyfile` in /etc/caddy/ and provide a TLS cert for your domain
6. MCP endpoint: https://YOUR-DOMAIN/mcp

## Notes
- Never commit .env or TLS private keys.
- allowed_hosts in server.py must include your domain.
