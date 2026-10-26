import os
import json
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["GATEWAY_API_KEY"],
    base_url=os.environ["GATEWAY_BASE_URL"],
    timeout=120,
)

mcp = FastMCP(
    "gateway",
    host="127.0.0.1",
    port=8000,
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=[
            "khozaabaliat.ir",
            "khozaabaliat.ir:*",
            "mcp.khozaabaliat.ir",
            "mcp.khozaabaliat.ir:*",
            "127.0.0.1:*",
            "localhost:*",
        ],
        allowed_origins=[
            "https://khozaabaliat.ir",
            "https://mcp.khozaabaliat.ir",
            "https://claude.ai",
        ],
    ),
)


@mcp.tool()
def list_models() -> str:
    """List all models available on the gateway."""
    try:
        return "\n".join(sorted(m.id for m in client.models.list().data))
    except Exception as e:
        return f"ERROR: {type(e).__name__}: {e}"


@mcp.tool()
def chat(
    model: str,
    prompt: str,
    system: str = "",
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> str:
    """Send a single prompt to a model on the gateway and return its reply.

    model: exact model id (use list_models to see them)
    prompt: the user message
    system: optional system prompt
    temperature: optional (some newer models reject it)
    max_tokens: optional cap on output length
    """
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    return _complete(model, messages, temperature, max_tokens)


@mcp.tool()
def chat_messages(
    model: str,
    messages_json: str,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> str:
    """Multi-turn chat. messages_json is a JSON list like
    [{"role":"system","content":"..."},{"role":"user","content":"..."}]"""
    try:
        messages = json.loads(messages_json)
    except Exception as e:
        return f"ERROR: invalid messages_json: {e}"
    return _complete(model, messages, temperature, max_tokens)


def _complete(model, messages, temperature, max_tokens) -> str:
    kwargs = {"model": model, "messages": messages}
    if temperature is not None:
        kwargs["temperature"] = temperature
    if max_tokens is not None:
        kwargs["max_tokens"] = max_tokens
    try:
        r = client.chat.completions.create(**kwargs)
        return r.choices[0].message.content or ""
    except Exception as e:
        return f"ERROR: {type(e).__name__}: {e}"


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
