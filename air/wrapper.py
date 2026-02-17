"""One-line wrapper: redirect any OpenAI client through AIR gateway.

Usage:
    from openai import OpenAI
    import air

    client = air.air_wrap(OpenAI())
    # That's it. Every call now records through AIR.
"""

from __future__ import annotations

import os
from typing import Any


def air_wrap(client: Any, gateway_url: str | None = None) -> Any:
    """Wrap an OpenAI-compatible client to route through AIR gateway.

    Works with:
      - openai.OpenAI
      - openai.AsyncOpenAI
      - Any client with a base_url attribute

    Args:
        client: An OpenAI SDK client instance.
        gateway_url: AIR gateway URL. Defaults to AIR_GATEWAY_URL
                     env var or http://localhost:8080.
    """
    url = gateway_url or os.getenv(
        "AIR_GATEWAY_URL", "http://localhost:8080"
    )

    # OpenAI SDK v1+ uses httpx under the hood.
    # We just swap the base_url to point at the gateway.
    if hasattr(client, "base_url"):
        # openai.OpenAI stores base_url as an httpx.URL
        try:
            import httpx as _httpx
            client.base_url = _httpx.URL(url + "/v1")
        except ImportError:
            client.base_url = url + "/v1"
    elif hasattr(client, "_client") and hasattr(client._client, "base_url"):
        # Some wrappers nest the httpx client
        try:
            import httpx as _httpx
            client._client.base_url = _httpx.URL(url + "/v1")
        except ImportError:
            client._client.base_url = url + "/v1"
    else:
        raise TypeError(
            f"Cannot wrap {type(client).__name__}: no base_url attribute. "
            "air_wrap works with OpenAI SDK clients (OpenAI, AsyncOpenAI)."
        )

    return client
